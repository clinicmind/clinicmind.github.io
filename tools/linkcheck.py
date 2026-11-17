#!/usr/bin/env python3
"""PsyPick 連結健康檢查（計劃 T1-7）。

對全站所有來源網址做 HEAD 請求（失敗或不支援時轉 GET），分類：
- dead：HTTP 404 / 410，或網域無法解析（失效）
- manual：HTTP 403、逾時、連線錯誤、5xx 等，需人手覆核
- ok：其餘 2xx/3xx

只用 Python 標準庫。用法：
    python3 tools/linkcheck.py [--data-dir site/data] [--out linkcheck-report.json]
                                [--timeout 15] [--workers 12]
輸出 JSON 報告並在 stdout 印摘要。exit code：有 dead 時 0（只報告不擋），
參數錯誤 2。
"""
import argparse
import json
import os
import socket
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (compatible; PsyPickLinkCheck/1.0)"


def collect(data_dir):
    """回傳 {url: [labels]}。"""
    urls = {}

    def add(url, label):
        if url and isinstance(url, str) and url.startswith("http"):
            urls.setdefault(url, []).append(label)

    cases_dir = os.path.join(data_dir, "cases")
    if os.path.isdir(cases_dir):
        for fn in sorted(os.listdir(cases_dir)):
            if not fn.endswith(".json"):
                continue
            try:
                d = json.load(open(os.path.join(cases_dir, fn), encoding="utf-8"))
            except Exception:
                continue
            for p in d.get("posts") or []:
                add(p.get("url"), "case:" + d.get("slug", fn))
    for name, key in (("family.json", "items"), ("conferences.json", "items")):
        path = os.path.join(data_dir, name)
        if os.path.exists(path):
            d = json.load(open(path, encoding="utf-8"))
            for it in d.get(key) or []:
                add(it.get("url"), name[:-5] + ":" + it.get("slug", "?"))
    fig_path = os.path.join(data_dir, "figures.json")
    if os.path.exists(fig_path):
        d = json.load(open(fig_path, encoding="utf-8"))
        # updates 是頂層陣列，以 person 欄位連結人物，網址欄位是 url
        for u in d.get("updates") or []:
            add(u.get("url") or u.get("source_url"),
                "figures-update:" + str(u.get("person", "?")))
        # 人物帳戶網址也一併檢查
        for person in d.get("people") or []:
            for a in person.get("accounts") or []:
                add(a.get("url"), "figures-account:" + person.get("slug", "?"))
    return urls


def check(url, timeout):
    """回傳 (category, status, detail)。category: ok/dead/manual。"""
    # 非 ASCII 網址（如中文路徑）先編碼，否則 urllib 會拋 UnicodeEncodeError
    try:
        url.encode("ascii")
    except UnicodeEncodeError:
        from urllib.parse import quote, urlsplit, urlunsplit
        parts = urlsplit(url)
        url = urlunsplit((parts.scheme, parts.netloc,
                          quote(parts.path), quote(parts.query, safe="=&?"),
                          parts.fragment))
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method,
                                     headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                resp.read(512)
                return ("ok", resp.status, resp.geturl())
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                return ("dead", e.code, "HTTP %d" % e.code)
            if e.code in (405, 501) and method == "HEAD":
                continue  # 轉 GET 重試
            if e.code == 403:
                return ("manual", 403, "HTTP 403（可能擋機械人）")
            if 500 <= e.code < 600:
                return ("manual", e.code, "HTTP %d（伺服器錯誤）" % e.code)
            return ("manual", e.code, "HTTP %d" % e.code)
        except urllib.error.URLError as e:
            reason = e.reason
            if isinstance(reason, socket.gaierror):
                return ("dead", None, "網域無法解析：%s" % reason)
            if method == "HEAD":
                continue  # 連線層面失敗，轉 GET 再試一次
            return ("manual", None, "連線錯誤：%s" % reason)
        except Exception as e:  #逾時、SSL 等
            if method == "HEAD":
                continue
            return ("manual", None, "%s: %s" % (type(e).__name__, e))
    return ("manual", None, "未知")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="site/data")
    ap.add_argument("--out", default="")
    ap.add_argument("--timeout", type=int, default=15)
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()

    urls = collect(args.data_dir)
    results = {"dead": [], "manual": [], "ok": 0}
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for url, (cat, status, detail) in zip(
                urls, ex.map(lambda u: check(u, args.timeout), urls)):
            if cat == "ok":
                results["ok"] += 1
            else:
                results[cat].append({
                    "url": url, "status": status, "detail": detail,
                    "used_by": urls[url],
                })
    report = {
        "total_urls": len(urls),
        "ok": results["ok"],
        "dead": sorted(results["dead"], key=lambda x: x["url"]),
        "manual_review": sorted(results["manual"], key=lambda x: x["url"]),
    }
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=1)
    print("checked %d urls: ok %d, dead %d, manual %d"
          % (report["total_urls"], report["ok"],
             len(report["dead"]), len(report["manual_review"])))
    for d in report["dead"]:
        print("DEAD %s -> %s (%s)" % (d["status"], d["url"], d["used_by"][0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
