#!/usr/bin/env python3
"""PsyPick 建置腳本（主站 repo 用）。

第一版（T2-3）：只產生 psypick/data/version.json，
內容包括建置提交 SHA、時間與各類數量，供上架後核實部署版本。
T2-4 起本腳本亦負責由 cases/*.json 產生 index.json。

只用 Python 標準函式庫。
用法：
  python3 tools/psypick/build.py [--data-dir psypick/data] [--sha SHA]
"""

import argparse
import json
import os
from datetime import datetime, timezone


def count_in(path, key):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        val = data.get(key)
        return len(val) if isinstance(val, list) else 0
    except Exception:
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="psypick/data")
    ap.add_argument("--sha", default=os.environ.get("GITHUB_SHA", "local"))
    args = ap.parse_args()
    d = args.data_dir

    family_items = []
    try:
        with open(os.path.join(d, "family.json"), encoding="utf-8") as f:
            family_items = json.load(f).get("items") or []
    except Exception:
        pass

    version = {
        "sha": args.sha,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "index": count_in(os.path.join(d, "index.json"), "cases"),
            "family": len(family_items),
            "deal": sum(1 for i in family_items if i.get("kind") == "deal"),
            "figures_people": count_in(os.path.join(d, "figures.json"), "people"),
            "figures_updates": count_in(os.path.join(d, "figures.json"), "updates"),
            "conferences": count_in(os.path.join(d, "conferences.json"), "items"),
        },
    }
    out = os.path.join(d, "version.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(version, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("version.json:", json.dumps(version, ensure_ascii=False))


if __name__ == "__main__":
    main()
