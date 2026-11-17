#!/usr/bin/env python3
"""PsyPick 資料自動檢查（T1-1）。

只用 Python 標準函式庫。檢查 site/data 的完整性與紅線合規：

  (a) 所有 JSON 可解析
  (b) index 的 slug 與 case 檔對應（include=true 的 case 必須在 index 內；
      index 內每則必須有 case 檔）
  (c) 沒有 kind=deal、沒有 deal_platforms、family topics 沒有「優惠」
  (d) 在架培訓的 format 不含「實體／現場／面授」，除非同時含「線上」
  (e) 每則有來源網址（case 的 posts[].url、family 的 url、會議的 url）
  (f) generated_at 不早於上一個提交（需 --prev-dir）
  (g) 任一集合數量比上一個提交減少超過 5 項，而提交訊息沒有 [remove]，
      就失敗（需 --prev-dir 與 --message）
  (h) 新條目（first_seen_at 在 2026-11-20 之後）必須有 evidence_quote，
      且不多於 40 字
  (i) 培訓 event_date 必須是 ISO 日期（YYYY-MM-DD）、空白或「隨選」（警告）
  (j) 迷幻藥／氯胺酮相關條目不可以有 poster 欄位

用法：
  python3 tools/validate.py [--data-dir site/data] [--prev-dir DIR]
                            [--message "提交訊息"]

結束碼：0 = 通過（可帶警告）；1 = 失敗。
已知舊問題（舊條目缺 evidence_quote、event_date 舊格式等）列為警告，不算失敗。
"""

import argparse
import json
import os
import re
import sys
from datetime import date

ERRORS = []
WARNINGS = []

NEW_ENTRY_CUTOFF = "2026-11-20"
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
IN_PERSON_WORDS = ("實體", "現場", "面授")
POSTER_BANNED_ZH = ("迷幻", "氯胺酮", "裸蓋菇", "搖頭丸", "大麻")
POSTER_BANNED_EN = ("psilocybin", "lsd", "mdma", "ketamine", "esketamine",
                    "ayahuasca", "psychedelic")


def err(rule, msg):
    ERRORS.append("[%s] %s" % (rule, msg))


def warn(rule, msg):
    WARNINGS.append("[%s] %s" % (rule, msg))


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def collect_urls_from_case(case):
    urls = []
    for p in case.get("posts") or []:
        if p.get("url"):
            urls.append(p["url"])
    return urls


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="site/data")
    ap.add_argument("--prev-dir", default=None,
                    help="上一個提交的 data 目錄（供 (f)(g) 比較）")
    ap.add_argument("--message", default="",
                    help="本次提交訊息（供 (g) 檢查 [remove]）")
    args = ap.parse_args()
    data_dir = args.data_dir

    # ---------- (a) JSON 可解析 ----------
    index = family = figures = conferences = None
    for name in ("index.json", "family.json", "figures.json", "conferences.json"):
        path = os.path.join(data_dir, name)
        try:
            data = load_json(path)
        except Exception as e:
            err("a", "%s 無法解析：%s" % (name, e))
            continue
        if name == "index.json":
            index = data
        elif name == "family.json":
            family = data
        elif name == "figures.json":
            figures = data
        else:
            conferences = data

    cases = {}  # slug -> case dict
    cases_dir = os.path.join(data_dir, "cases")
    case_files = []
    if os.path.isdir(cases_dir):
        case_files = sorted(f for f in os.listdir(cases_dir)
                            if f.endswith(".json"))
    for fn in case_files:
        path = os.path.join(cases_dir, fn)
        try:
            c = load_json(path)
        except Exception as e:
            err("a", "cases/%s 無法解析：%s" % (fn, e))
            continue
        slug = c.get("slug") or fn[:-5]
        cases[slug] = c

    if index is None:
        print("VALIDATION FAILED")
        for e in ERRORS:
            print("ERROR", e)
        return 1

    index_cases = index.get("cases") or []
    index_slugs = [c.get("slug") for c in index_cases]

    # ---------- (b) slug 對應 ----------
    for slug in index_slugs:
        if slug not in cases:
            err("b", "index 有 slug=%s 但沒有 case 檔" % slug)
    for slug, c in cases.items():
        if c.get("include") is not False and slug not in index_slugs:
            err("b", "case slug=%s include!=false 但不在 index 內" % slug)

    # ---------- (c) 優惠 ----------
    for slug, c in cases.items():
        if c.get("kind") == "deal":
            err("c", "case slug=%s kind=deal（優惠已停收）" % slug)
    for c in index_cases:
        if c.get("kind") == "deal":
            err("c", "index slug=%s kind=deal（優惠已停收）" % c.get("slug"))
    if family is not None:
        if "deal_platforms" in family:
            err("c", "family.json 仍有 deal_platforms 欄位")
        if "優惠" in (family.get("topics") or []):
            err("c", "family.json topics 仍含「優惠」")
        for it in family.get("items") or []:
            if it.get("kind") == "deal":
                err("c", "family slug=%s kind=deal（優惠已停收）"
                    % it.get("slug"))

    # ---------- (d)(e)(h)(i)(j) 逐 case 檢查 ----------
    missing_quote_old = 0
    for slug, c in cases.items():
        live = c.get("include") is not False
        # (e) 來源網址
        if live and not collect_urls_from_case(c):
            err("e", "case slug=%s 沒有任何 posts[].url" % slug)
        # (h) evidence_quote
        first_seen = (c.get("first_seen_at") or "")[:10]
        quote = c.get("evidence_quote")
        if first_seen and first_seen > NEW_ENTRY_CUTOFF:
            if not quote:
                err("h", "新條目 slug=%s 缺 evidence_quote" % slug)
            elif len(quote) > 40:
                err("h", "新條目 slug=%s evidence_quote 超過 40 字（%d 字）"
                    % (slug, len(quote)))
        else:
            if not quote:
                missing_quote_old += 1
            elif len(quote) > 40:
                warn("h", "舊條目 slug=%s evidence_quote 超過 40 字（%d 字）"
                     % (slug, len(quote)))
        # (j) 海報紅線
        if c.get("poster"):
            text = " ".join([c.get("title_zh") or "", c.get("title_en") or ""]
                            + list(c.get("tags") or []))
            low = text.lower()
            hit = [w for w in POSTER_BANNED_ZH if w in text]
            hit += [w for w in POSTER_BANNED_EN
                    if re.search(r"(?<![a-z])%s(?![a-z])" % w, low)]
            if hit:
                err("j", "slug=%s 屬迷幻藥／氯胺酮題材（%s）但有 poster"
                    % (slug, "、".join(hit)))
        # 培訓專項
        if c.get("kind") == "training":
            tr = c.get("training") or {}
            fmt = tr.get("format") or ""
            if live and any(w in fmt for w in IN_PERSON_WORDS) \
                    and "線上" not in fmt:
                err("d", "培訓 slug=%s format=「%s」含實體／現場／面授"
                    "而沒有線上" % (slug, fmt))
            ev = tr.get("event_date")
            if ev not in (None, "", "隨選") and not ISO_DATE.match(str(ev)):
                warn("i", "培訓 slug=%s event_date=「%s」不是 ISO 日期"
                     % (slug, ev))

    if missing_quote_old:
        warn("h", "舊條目缺 evidence_quote 共 %d 則（T1-6 分批補齊中）"
             % missing_quote_old)

    # family (e)
    if family is not None:
        for it in family.get("items") or []:
            if not it.get("url"):
                err("e", "family slug=%s 沒有 url" % it.get("slug"))
    # conferences (e)
    if conferences is not None:
        for it in conferences.get("items") or []:
            if not it.get("url") and not it.get("register_url"):
                err("e", "conferences slug=%s 沒有 url" % it.get("slug"))

    # figures 欄位漂移（警告）
    if figures is not None:
        miss = [u for u in figures.get("updates") or []
                if "tier" not in u or "verify_needed" not in u]
        if miss:
            warn("figures", "figures updates 缺 tier／verify_needed 共 %d 則"
                 % len(miss))

    # ---------- (f)(g) 與上一個提交比較 ----------
    if args.prev_dir:
        prev = {}
        for name in ("index.json", "family.json", "figures.json",
                     "conferences.json"):
            p = os.path.join(args.prev_dir, name)
            if os.path.exists(p):
                try:
                    prev[name] = load_json(p)
                except Exception:
                    prev[name] = None
        # (f) generated_at
        for name, cur in (("index.json", index), ("family.json", family),
                          ("conferences.json", conferences)):
            old = prev.get(name)
            if old and cur:
                if (cur.get("generated_at") or "") < (old.get("generated_at")
                                                      or ""):
                    err("f", "%s generated_at %s 早於上一個提交 %s"
                        % (name, cur.get("generated_at"),
                           old.get("generated_at")))
        if figures is not None and prev.get("figures.json"):
            if (figures.get("updated") or "") < \
                    (prev["figures.json"].get("updated") or ""):
                err("f", "figures.json updated %s 早於上一個提交 %s"
                    % (figures.get("updated"),
                       prev["figures.json"].get("updated")))
        # (g) 數量減少
        def count(data, key):
            return len(data.get(key) or []) if data else None
        cur_counts = {
            "index cases": len(index_cases),
            "family items": count(family, "items"),
            "figures updates": count(figures, "updates"),
            "conferences items": count(conferences, "items"),
            "case 檔案": len(case_files),
        }
        prev_counts = {
            "index cases": count(prev.get("index.json"), "cases"),
            "family items": count(prev.get("family.json"), "items"),
            "figures updates": count(prev.get("figures.json"), "updates"),
            "conferences items": count(prev.get("conferences.json"), "items"),
            "case 檔案": None,
        }
        prev_cases_dir = os.path.join(args.prev_dir, "cases")
        if os.path.isdir(prev_cases_dir):
            prev_counts["case 檔案"] = len(
                [f for f in os.listdir(prev_cases_dir)
                 if f.endswith(".json")])
        has_remove_tag = "[remove]" in (args.message or "")
        for label, cur_n in cur_counts.items():
            old_n = prev_counts.get(label)
            if cur_n is None or old_n is None:
                continue
            drop = old_n - cur_n
            if drop > 5 and not has_remove_tag:
                err("g", "%s 數量減少 %d（%d → %d），提交訊息沒有 [remove]"
                    % (label, drop, old_n, cur_n))
    else:
        print("NOTE: 未提供 --prev-dir，跳過 (f)(g) 比較檢查")

    # ---------- 輸出 ----------
    for w in WARNINGS:
        print("WARN", w)
    for e in ERRORS:
        print("ERROR", e)
    print("counts: index=%d family=%s figures_updates=%s conferences=%s "
          "case_files=%d" % (
              len(index_cases),
              len(family.get("items") or []) if family else "-",
              len(figures.get("updates") or []) if figures else "-",
              len(conferences.get("items") or []) if conferences else "-",
              len(case_files)))
    if ERRORS:
        print("VALIDATION FAILED (%d errors, %d warnings)"
              % (len(ERRORS), len(WARNINGS)))
        return 1
    print("VALIDATION PASSED (%d warnings)" % len(WARNINGS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
