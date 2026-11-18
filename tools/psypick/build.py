#!/usr/bin/env python3
"""PsyPick 建置腳本（主站 repo 用）。

T2-3 第一版：產生 psypick/data/version.json。
T2-4 第二版：同時由 psypick/data/cases/*.json 產生 psypick/data/index.json。
index.json 由本腳本產生，切勿人手修改（見 .gitattributes）。

產生規則（與舊管線逐則比對後定案）：
  - 只收錄 include != false 的 case；順序沿用上一版 index.json 的順序，
    新 slug 按 first_seen_at 由新到舊排在最前。
  - 條目欄位為 case 的子集；mention_count = posts 數量；
    has_ethics_flags = ethics_flags 非空；date 取 case 的 date 欄位
    （T2-4 一次性遷移：由舊 index 回寫），缺失時用 posts[0].posted_at，
    再缺失用 first_seen_at。
  - training 只保留 8 個列表欄位（provider, format, price, price_tier,
    ce_credits, language, event_date, deadline）。
  - tier：case 已 archive 的保留 archive；培訓 event_date 已過期改 archive。
  - deadline_soon（只限有 training 的條目）：deadline 或 event_date
    在今天起 7 日內（含今天）為 true。
  - related 不入 index（詳情頁直接讀 case 檔）；case 有 poster 欄位時帶入。
  - config 沿用上一版 index.json 的 config。

只用 Python 標準函式庫。
用法：
  python3 tools/psypick/build.py [--data-dir psypick/data] [--sha SHA]
                                  [--today YYYY-MM-DD]
"""

import argparse
import json
import os
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlparse

ENTRY_FIELDS = ["slug", "title_zh", "title_en", "summary_zh", "summary_en",
                "category", "kind", "model_names", "tags", "first_seen_at",
                "evidence_level", "population", "hero_media", "verify_needed",
                "hot_score", "featured_at"]
TRAINING_FIELDS = ["provider", "format", "price", "price_tier",
                   "ce_credits", "language", "event_date", "deadline"]


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def iso_day(s):
    try:
        return date.fromisoformat(str(s)[:10])
    except Exception:
        return None


def build_index(data_dir, today):
    cases_dir = os.path.join(data_dir, "cases")
    prev_path = os.path.join(data_dir, "index.json")
    prev = load_json(prev_path) if os.path.exists(prev_path) else {}
    prev_order = [c.get("slug") for c in prev.get("cases") or []]
    config = prev.get("config") or {}

    cases = {}
    for name in os.listdir(cases_dir):
        if name.endswith(".json"):
            case = load_json(os.path.join(cases_dir, name))
            if case.get("include") is not False and case.get("slug"):
                cases[case["slug"]] = case

    def sort_key(slug):
        # 已在上一版的沿用原順序；新 slug 排最前（first_seen_at 新→舊）
        if slug in prev_order:
            return (1, prev_order.index(slug), "")
        return (0, "", "")

    new_slugs = [s for s in cases if s not in prev_order]
    new_slugs.sort(key=lambda s: cases[s].get("first_seen_at") or "", reverse=True)
    ordered = new_slugs + [s for s in prev_order if s in cases]

    entries = []
    for slug in ordered:
        case = cases[slug]
        entry = {}
        for k in ENTRY_FIELDS:
            entry[k] = case.get(k)
        entry["mention_count"] = len(case.get("posts") or [])
        # tier（過期規則）
        tier = case.get("tier") or "live"
        tr = case.get("training") or {}
        ev = iso_day(tr.get("event_date")) if tr else None
        if tier != "archive" and ev is not None and ev < today:
            tier = "archive"
        entry["tier"] = tier
        entry["has_ethics_flags"] = bool(case.get("ethics_flags"))
        # T3-3：卡片底行顯示來源網域（取第一個來源的 hostname）
        entry["source_domain"] = ""
        _posts = case.get("posts") or []
        if _posts and _posts[0].get("url"):
            try:
                entry["source_domain"] = urlparse(_posts[0]["url"]).hostname or ""
            except Exception:
                entry["source_domain"] = ""
        # date
        d = case.get("date")
        if not d:
            posts = case.get("posts") or []
            d = (posts[0].get("posted_at") if posts else None) or case.get("first_seen_at")
        entry["date"] = d
        if case.get("training"):
            entry["training"] = {k: tr.get(k) for k in TRAINING_FIELDS}
            soon = False
            for cand in (tr.get("deadline"), tr.get("event_date")):
                dd = iso_day(cand) if cand else None
                if dd is not None and today <= dd <= today + timedelta(days=7):
                    soon = True
            entry["deadline_soon"] = soon
        if case.get("poster"):
            entry["poster"] = case["poster"]
        entries.append(entry)

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "config": config,
        "cases": entries,
    }


def count_in(data, key):
    val = data.get(key)
    return len(val) if isinstance(val, list) else 0


# T3-7：列表用的 lite 版——只留卡片／篩選／搜尋需要的欄位，摘要截短到卡片
# 可見長度（約 3 行）。詳情頁本來就另外讀完整 case 檔／family.json，不受影響。
LITE_CASE_FIELDS = (
    "slug", "title_zh", "title_en", "category", "kind", "tags", "model_names",
    "date", "evidence_level", "verify_needed", "tier", "has_ethics_flags",
    "hot_score", "featured_at", "mention_count", "deadline_soon",
    "source_domain", "training",
)
LITE_FAM_FIELDS = (
    "slug", "kind", "title_zh", "title_en", "topic", "region", "org", "ages",
    "age_min", "age_max", "tags", "posted_at", "ended", "verify_needed",
)
LITE_ACTIVITY_FIELDS = ("date_start", "date_end", "free", "venue", "time", "organizer", "price")
LITE_BOUNTY_FIELDS = ("reward", "organizer", "deadline", "guaranteed", "method",
                      "eligibility", "duration", "reward_type", "location")


def lite_case(e):
    out = {k: e[k] for k in LITE_CASE_FIELDS if k in e}
    out["summary_zh"] = (e.get("summary_zh") or "")[:72]
    out["summary_en"] = (e.get("summary_en") or "")[:144]
    if e.get("poster"):
        p = e["poster"]
        out["poster"] = {k: p.get(k, "") for k in ("src", "alt_zh", "alt_en")}
    return out


def lite_family_item(it):
    out = {k: it[k] for k in LITE_FAM_FIELDS if k in it}
    out["summary_zh"] = (it.get("summary_zh") or "")[:72]
    out["summary_en"] = (it.get("summary_en") or "")[:144]
    if it.get("activity"):
        out["activity"] = {k: it["activity"].get(k) for k in LITE_ACTIVITY_FIELDS}
    if it.get("bounty"):
        out["bounty"] = {k: it["bounty"].get(k) for k in LITE_BOUNTY_FIELDS}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="psypick/data")
    ap.add_argument("--sha", default=os.environ.get("GITHUB_SHA", "local"))
    ap.add_argument("--today", default=None)
    args = ap.parse_args()
    d = args.data_dir
    today = iso_day(args.today) if args.today else date.today()

    index = build_index(d, today)
    with open(os.path.join(d, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
        f.write("\n")
    # T3-7：index-lite.json
    lite = {"generated_at": index["generated_at"], "config": index["config"],
            "cases": [lite_case(e) for e in index["cases"]]}
    with open(os.path.join(d, "index-lite.json"), "w", encoding="utf-8") as f:
        json.dump(lite, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")

    family = load_json(os.path.join(d, "family.json"))
    # T3-7：family-lite.json（不含 devhelp；詳情與求助頁按需讀完整版）
    fam_lite = {k: v for k, v in family.items() if k not in ("items", "devhelp")}
    fam_lite["items"] = [lite_family_item(it) for it in family.get("items") or []]
    with open(os.path.join(d, "family-lite.json"), "w", encoding="utf-8") as f:
        json.dump(fam_lite, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    figures = load_json(os.path.join(d, "figures.json"))
    conferences = load_json(os.path.join(d, "conferences.json"))
    version = {
        "sha": args.sha,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "index": len(index["cases"]),
            "family": count_in(family, "items"),
            "deal": sum(1 for i in family.get("items") or [] if i.get("kind") == "deal"),
            "figures_people": count_in(figures, "people"),
            "figures_updates": count_in(figures, "updates"),
            "conferences": count_in(conferences, "items"),
        },
    }
    with open(os.path.join(d, "version.json"), "w", encoding="utf-8") as f:
        json.dump(version, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("index cases:", len(index["cases"]), "| version:", json.dumps(version, ensure_ascii=False))


if __name__ == "__main__":
    main()
