#!/usr/bin/env python3
"""PsyPick 唯一上架工具：inbox v2 JSON → psypick/data/cases/<slug>.json。

用法：
  python3 tools/psypick/inbox_to_cases.py <inbox.json> [--data-dir psypick/data]
                                          [--dry-run] [--skip-build]

流程：
  1. 讀 inbox，逐則檢查 items[]（只處理 type=case；其他 type 列出後略過）。
  2. 任何一則有錯 → 全部不寫，列出所有錯誤，結束碼 1（成批唔寫）。
  3. slug 或來源網址已存在（含已下架的 case 檔）→ 略過該則，列出原因。
  4. 寫入新 case 檔，然後自動跑 build.py 與 validate.py。
     任一失敗 → 刪走今次新寫的 case 檔、還原索引檔，結束碼 1。
  5. 成功時最後一行印出 validate.py 的「VALIDATION PASSED」。

inbox v2 格式見 CLAUDE.md 第 3 節。只用 Python 標準函式庫。
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD_PY = os.path.join(HERE, "build.py")
VALIDATE_PY = os.path.join(os.path.dirname(HERE), "validate.py")

VALID_CATEGORIES = ("研究與證據", "臨床實務", "AI 與倫理", "進修培訓")
LEGACY_CATEGORY_MAP = {
    "臨床與治療應用": "臨床實務",
    "評估與篩檢": "臨床實務",
    "進修與培訓": "進修培訓",
    "倫理與風險": "AI 與倫理",
    "人機互動心理": "AI 與倫理",
}
DEFAULT_KINDS = ("research", "practice", "product", "incident", "training")
DEFAULT_EVIDENCE = {
    "個人經驗或評論": 0, "產品宣稱": 1, "前導或質性研究": 2,
    "對照試驗": 3, "系統性回顧或統合分析": 4,
}
REQUIRED_TEXT = ("title_zh", "title_en", "summary_zh", "summary_en",
                 "category", "kind", "evidence_quote", "evidence_note",
                 "caution")
REQUIRED_LIST = ("tags", "population", "brief_zh", "supervision_questions")
REQUIRED_SOURCE = ("url", "title", "author_name")
REQUIRED_TRAINING = ("provider", "format", "event_date", "signup_url")
TRAINING_KEYS = ("provider", "format", "price", "price_tier", "ce_credits",
                 "language", "event_date", "deadline", "audience_level",
                 "topic", "signup_url")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SLUG_MAX = 60
# build.py 會改寫的檔：失敗時要還原
GENERATED = ("index.json", "index-lite.json", "family-lite.json",
             "version.json")


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def slugify(title_en):
    s = (title_en or "").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    if len(s) > SLUG_MAX:
        s = s[:SLUG_MAX].rstrip("-")
    return s


def norm_url(u):
    u = (u or "").strip()
    u = re.sub(r"^https?://(www\.)?", "", u, flags=re.I)
    return u.rstrip("/").lower()


def existing_index(data_dir):
    """回傳 (slug 集合, 正規化來源網址→slug)，涵蓋所有 case 檔（含已下架）。"""
    slugs, urls = set(), {}
    cases_dir = os.path.join(data_dir, "cases")
    for fn in os.listdir(cases_dir):
        if not fn.endswith(".json"):
            continue
        slugs.add(fn[:-5])
        try:
            c = load_json(os.path.join(cases_dir, fn))
        except Exception:
            continue
        if c.get("slug"):
            slugs.add(c["slug"])
        for p in c.get("posts") or []:
            if p.get("url"):
                urls.setdefault(norm_url(p["url"]), c.get("slug") or fn[:-5])
    return slugs, urls


def load_config(data_dir):
    path = os.path.join(data_dir, "index.json")
    cfg = {}
    if os.path.exists(path):
        cfg = load_json(path).get("config") or {}
    kinds = tuple((cfg.get("kinds") or {}).keys()) or DEFAULT_KINDS
    levels = {}
    for k, v in (cfg.get("evidence_levels") or {}).items():
        if isinstance(v, dict) and v.get("zh"):
            levels[v["zh"]] = int(k)
    return kinds, (levels or dict(DEFAULT_EVIDENCE))


def blank(v):
    return v is None or (isinstance(v, str) and not v.strip())


def convert_item(item, label, kinds, levels, first_seen_at):
    """回傳 (case dict 或 None, 錯誤清單)。"""
    errs = []
    for k in REQUIRED_TEXT:
        if blank(item.get(k)):
            errs.append("%s 缺 %s" % (label, k))
    for k in REQUIRED_LIST:
        v = item.get(k)
        if not isinstance(v, list) or not [x for x in v if not blank(x)]:
            errs.append("%s 缺 %s（要非空清單）" % (label, k))
    if not isinstance(item.get("verify_needed"), bool):
        errs.append("%s 缺 verify_needed（要 true／false）" % label)

    # 分類（舊名對照）
    cat = item.get("category")
    if not blank(cat):
        cat = LEGACY_CATEGORY_MAP.get(cat, cat)
        if cat not in VALID_CATEGORIES:
            errs.append("%s category「%s」不是站內分類（%s）"
                        % (label, item.get("category"),
                           "／".join(VALID_CATEGORIES)))
    kind = item.get("kind")
    if not blank(kind) and kind not in kinds:
        errs.append("%s kind「%s」不是既有值（%s）"
                    % (label, kind, "、".join(kinds)))

    # 證據摘句
    quote = item.get("evidence_quote") or ""
    if len(quote) > 40:
        errs.append("%s evidence_quote 超過 40 字（%d 字）"
                    % (label, len(quote)))

    # 證據等級：evidence_hint（中文名）或 evidence_level（0–4）
    level = None
    hint = item.get("evidence_hint")
    if not blank(hint):
        if hint in levels:
            level = levels[hint]
        else:
            errs.append("%s evidence_hint「%s」不在 config.evidence_levels"
                        "（%s）" % (label, hint, "／".join(levels)))
    elif isinstance(item.get("evidence_level"), int) \
            and not isinstance(item.get("evidence_level"), bool) \
            and 0 <= item["evidence_level"] <= 4:
        level = item["evidence_level"]
    else:
        errs.append("%s 缺 evidence_hint（或 0–4 的 evidence_level）" % label)
    if level is not None and not blank(item.get("evidence_level")) \
            and not blank(hint) and item.get("evidence_level") != level:
        errs.append("%s evidence_hint 與 evidence_level 不一致" % label)

    # 來源
    src = item.get("source")
    if not isinstance(src, dict):
        errs.append("%s 缺 source{url,title,author_name}" % label)
        src = {}
    for k in REQUIRED_SOURCE:
        if blank(src.get(k)):
            errs.append("%s 缺 source.%s" % (label, k))
    if not blank(src.get("url")) and \
            not re.match(r"^https?://", src["url"].strip()):
        errs.append("%s source.url 不是 http(s) 網址" % label)

    # 原文日期
    page_date = item.get("page_date") or ""
    if page_date and not ISO_DATE.match(page_date):
        errs.append("%s page_date「%s」要用 YYYY-MM-DD" % (label, page_date))
    if not page_date and item.get("verify_needed") is not True:
        errs.append("%s 冇 page_date，verify_needed 必須是 true"
                    "（不可以用上架時間代替）" % label)
    if item.get("verify_needed") is True and blank(item.get("verify_reason")):
        errs.append("%s verify_needed=true 但缺 verify_reason" % label)

    # 培訓
    training = None
    if kind == "training" or cat == "進修培訓":
        tr = item.get("training")
        if not isinstance(tr, dict):
            errs.append("%s 培訓條目缺 training{}" % label)
            tr = {}
        for k in REQUIRED_TRAINING:
            if blank(tr.get(k)):
                errs.append("%s 缺 training.%s" % (label, k))
        ev = tr.get("event_date")
        if not blank(ev) and ev != "隨選" and not ISO_DATE.match(str(ev)):
            errs.append("%s training.event_date「%s」要用 YYYY-MM-DD 或「隨選」"
                        % (label, ev))
        training = {k: tr.get(k, "") for k in TRAINING_KEYS}
        for k, v in tr.items():
            if k not in training:
                training[k] = v
    elif item.get("training"):
        errs.append("%s 非培訓條目不應有 training{}" % label)

    # slug
    slug = item.get("slug") or slugify(item.get("title_en"))
    if not slug or not SLUG_RE.match(slug):
        errs.append("%s slug「%s」無效（只可小寫英文、數字、連字號）"
                    % (label, slug))

    if errs:
        return None, errs

    posted_at = (page_date + "T00:00:00+00:00") if page_date else ""
    case = {
        "title_zh": item["title_zh"],
        "title_en": item["title_en"],
        "summary_zh": item["summary_zh"],
        "summary_en": item["summary_en"],
        "category": cat,
        "kind": kind,
        "evidence_level": level,
        "evidence_note": item["evidence_note"],
        "ethics_flags": list(item.get("ethics_flags") or []),
        "psych_concepts": list(item.get("psych_concepts") or []),
        "caution": item["caution"],
        "verify_needed": item["verify_needed"],
        "verify_reason": item.get("verify_reason") or "",
        "brief_zh": list(item["brief_zh"]),
        "brief_en": list(item.get("brief_en") or []),
        "model_names": list(item.get("model_names") or []),
        "tags": list(item["tags"]),
        "population": list(item["population"]),
        "supervision_questions": list(item["supervision_questions"]),
        "original_prompt": "",
        "training": training,
        "posts": [{
            "platform": src.get("platform") or "web",
            "url": src["url"].strip(),
            "author_handle": src.get("author_handle") or "",
            "author_name": src["author_name"],
            "title": src["title"],
            "content": src.get("content") or item["summary_zh"],
            "posted_at": posted_at,
        }],
        "first_seen_at": first_seen_at,
        "hero_media": None,
        "include": True,
        "reject_reason": "",
        "slug": slug,
        "featured_at": None,
        "hot_score": 0.0,
        "tier": "live",
        "deadline_soon": False,
        "related": list(item.get("related") or []),
        "evidence_quote": item["evidence_quote"],
    }
    return case, []


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main(argv=None):
    ap = argparse.ArgumentParser(description="inbox v2 → PsyPick case 檔")
    ap.add_argument("inbox")
    ap.add_argument("--data-dir", default="psypick/data")
    ap.add_argument("--dry-run", action="store_true",
                    help="只檢查，不寫檔")
    ap.add_argument("--skip-build", action="store_true",
                    help="（只供測試）寫檔後不跑 build／validate")
    ap.add_argument("--now", default=None,
                    help="（只供測試）first_seen_at 用的時間")
    args = ap.parse_args(argv)
    data_dir = args.data_dir
    cases_dir = os.path.join(data_dir, "cases")

    try:
        inbox = load_json(args.inbox)
    except Exception as e:
        print("ERROR inbox 無法解析：%s" % e)
        return 1
    items = inbox.get("items") if isinstance(inbox, dict) else None
    if not isinstance(items, list):
        print("ERROR inbox 沒有 items[]")
        return 1

    first_seen_at = args.now or datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%S+00:00")
    kinds, levels = load_config(data_dir)
    have_slugs, have_urls = existing_index(data_dir)

    errors, skipped, todo = [], [], []
    batch_slugs, batch_urls = set(), set()
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append("items[%d] 不是物件" % i)
            continue
        label = "items[%d]（%s）" % (i, item.get("slug") or item.get("title_en")
                                    or item.get("title_zh") or "?")
        if item.get("type") != "case":
            skipped.append("%s type=%s，不是 case，略過"
                           % (label, item.get("type")))
            continue
        case, errs = convert_item(item, label, kinds, levels, first_seen_at)
        if errs:
            errors.extend(errs)
            continue
        slug, url = case["slug"], norm_url(case["posts"][0]["url"])
        if slug in have_slugs:
            skipped.append("%s slug=%s 已存在，略過（不覆蓋）" % (label, slug))
            continue
        if url in have_urls:
            skipped.append("%s 來源網址已見於 %s，略過"
                           % (label, have_urls[url]))
            continue
        if slug in batch_slugs or url in batch_urls:
            errors.append("%s 與同批另一則 slug 或來源網址重複" % label)
            continue
        batch_slugs.add(slug)
        batch_urls.add(url)
        todo.append(case)

    for s in skipped:
        print("SKIP", s)
    if errors:
        for e in errors:
            print("ERROR", e)
        print("CONVERT FAILED：%d 個錯誤，全部不寫入" % len(errors))
        return 1
    if not todo:
        print("沒有新條目要寫入（略過 %d 則）" % len(skipped))
        return 0
    if args.dry_run:
        for c in todo:
            print("DRY-RUN 會寫入 cases/%s.json" % c["slug"])
        print("DRY-RUN OK：%d 則可寫入" % len(todo))
        return 0

    # 備份 build.py 會改寫的檔
    backup = {}
    for name in GENERATED:
        p = os.path.join(data_dir, name)
        backup[name] = None
        if os.path.exists(p):
            with open(p, "rb") as f:
                backup[name] = f.read()

    written = []
    try:
        for c in todo:
            path = os.path.join(cases_dir, c["slug"] + ".json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(c, f, ensure_ascii=False, indent=2)
                f.write("\n")
            written.append(path)
    except Exception as e:
        print("ERROR 寫檔失敗：%s" % e)
        ok, out = False, ""
    else:
        ok, out = True, ""

    if ok and not args.skip_build:
        rc, out = run([sys.executable, BUILD_PY, "--data-dir", data_dir])
        print(out.rstrip())
        if rc != 0:
            print("ERROR build.py 失敗（結束碼 %d）" % rc)
            ok = False
        else:
            rc, out = run([sys.executable, VALIDATE_PY, "--data-dir",
                           data_dir])
            print(out.rstrip())
            if rc != 0 or "VALIDATION PASSED" not in out:
                print("ERROR validate.py 未通過")
                ok = False

    if not ok:
        for p in written:
            if os.path.exists(p):
                os.remove(p)
        for name, content in backup.items():
            p = os.path.join(data_dir, name)
            if content is None:
                if os.path.exists(p):
                    os.remove(p)
            else:
                with open(p, "wb") as f:
                    f.write(content)
        print("ROLLED BACK：已刪走今次新寫的 %d 個 case 檔並還原索引，"
              "不可以推送" % len(written))
        return 1

    for c in todo:
        print("WROTE cases/%s.json" % c["slug"])
    print("DONE：新增 %d 則，略過 %d 則" % (len(todo), len(skipped)))
    if not args.skip_build:
        print("VALIDATION PASSED — 可以提交推送")
    return 0


if __name__ == "__main__":
    sys.exit(main())
