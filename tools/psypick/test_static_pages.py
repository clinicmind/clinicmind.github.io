#!/usr/bin/env python3
"""靜態頁／sitemap／RSS 的驗證測試（C-3、C-4）。

在暫存複本上跑 build.py --sitemap，然後檢查：
  - 靜態頁數 = index.json 在架條目數；人物頁數 = figures.json 人數
  - 每頁純 HTML 已有標題、摘要、canonical、可解析的 JSON-LD
  - 所有站內連結（href／src）都指向存在的檔案（零內部斷鏈）
  - sitemap.xml 可解析、保留原有網址、包含全部靜態頁
  - feed.xml 可解析、最多 50 則

用法：python3 tools/psypick/test_static_pages.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SITE = "https://clinicmind.github.io/"
SM = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ld, self.canonical, self.h1 = [], [], None, ""
        self.lang = None
        self._in_ld = self._in_h1 = False
        self._buf = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag in ("a", "link") and a.get("href"):
            self.links.append(a["href"])
            if a.get("rel") == "canonical":
                self.canonical = a["href"]
        if tag in ("img", "script") and a.get("src"):
            self.links.append(a["src"])
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld, self._buf = True, ""
        if tag == "h1":
            self._in_h1 = True

    def handle_endtag(self, tag):
        if tag == "script" and self._in_ld:
            self.ld.append(self._buf)
            self._in_ld = False
        if tag == "h1":
            self._in_h1 = False

    def handle_data(self, data):
        if self._in_ld:
            self._buf += data
        if self._in_h1:
            self.h1 += data


def resolve(page_path, link, root):
    """站內連結 → 本地檔案路徑；站外連結回傳 None。"""
    if link.startswith(SITE):
        link = "/" + link[len(SITE):]
    u = urlparse(link)
    if u.scheme or u.netloc or link.startswith(("#", "mailto:")):
        return None
    path = u.path
    if not path:
        return None
    if path.startswith("/"):
        target = os.path.join(root, path.lstrip("/"))
    else:
        target = os.path.normpath(os.path.join(os.path.dirname(page_path), path))
    if path.endswith("/") or os.path.isdir(target):
        target = os.path.join(target, "index.html")
    return target


class TestStaticPages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        root = cls.root = os.path.join(cls.tmp, "site")
        os.makedirs(root)
        for fn in os.listdir(REPO):
            src = os.path.join(REPO, fn)
            if os.path.isfile(src) and fn.endswith((".html", ".xml", ".txt")):
                shutil.copy(src, root)
        shutil.copytree(os.path.join(REPO, "psypick"),
                        os.path.join(root, "psypick"),
                        ignore=shutil.ignore_patterns("p", "fig", "feed.xml"))
        shutil.copytree(os.path.join(REPO, "assets"),
                        os.path.join(root, "assets"))
        cls.base_locs = [u.findtext(SM + "loc").strip() for u in
                         ET.parse(os.path.join(REPO, "sitemap.xml")).getroot()]
        r = subprocess.run([sys.executable,
                            os.path.join(HERE, "build.py"), "--data-dir",
                            os.path.join(root, "psypick", "data"), "--sitemap"],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        data = os.path.join(root, "psypick", "data")
        with open(os.path.join(data, "index.json"), encoding="utf-8") as f:
            cls.index = json.load(f)
        with open(os.path.join(data, "figures.json"), encoding="utf-8") as f:
            cls.figures = json.load(f)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def pages(self, sub):
        d = os.path.join(self.root, "psypick", sub)
        return sorted(os.path.join(d, f) for f in os.listdir(d))

    def test_counts(self):
        self.assertEqual(len(self.pages("p")), len(self.index["cases"]))
        self.assertEqual(len(self.pages("fig")), len(self.figures["people"]))

    def test_pages_have_content_and_no_broken_links(self):
        cases = {c["slug"]: c for c in self.index["cases"]}
        broken = []
        for path in self.pages("p") + self.pages("fig"):
            with open(path, encoding="utf-8") as f:
                html = f.read()
            p = Page()
            p.feed(html)
            name = os.path.basename(path)
            self.assertEqual(p.lang, "zh-Hant", name)
            self.assertTrue(p.h1.strip(), name)
            self.assertTrue(p.canonical and p.canonical.endswith(name), name)
            self.assertEqual(len(p.ld), 1, name)
            ld = json.loads(p.ld[0])
            self.assertIn(ld["@type"], ("ScholarlyArticle", "Article", "Event",
                                        "Person"), name)
            self.assertIn("adsbygoogle", html)
            if "/p/" in path:
                c = cases[name[:-5]]
                self.assertIn(c["title_zh"].replace("&", "&amp;")
                              .replace('"', "&quot;").replace("'", "&#x27;")
                              .replace("<", "&lt;").replace(">", "&gt;")[:20],
                              html)
                self.assertIn("../#/case/" + c["slug"], html)
                want = "Event" if c["kind"] == "training" else (
                    "ScholarlyArticle" if c["kind"] == "research" else "Article")
                self.assertEqual(ld["@type"], want, name)
            for link in p.links:
                t = resolve(path, link, self.root)
                if t and not os.path.exists(t):
                    broken.append("%s → %s" % (name, link))
        self.assertEqual(broken, [])

    def test_sitemap(self):
        root = ET.parse(os.path.join(self.root, "sitemap.xml")).getroot()
        locs = [u.findtext(SM + "loc").strip() for u in root]
        self.assertEqual(locs[:len(self.base_locs)], self.base_locs)
        n = len(self.index["cases"]) + len(self.figures["people"])
        self.assertEqual(len(locs), len(self.base_locs) + n)
        self.assertEqual(len(set(locs)), len(locs))
        for loc in locs[len(self.base_locs):]:
            self.assertTrue(os.path.exists(resolve("/", loc, self.root)), loc)
        # 再跑一次不會重複加入
        subprocess.run([sys.executable, os.path.join(HERE, "build.py"),
                        "--data-dir", os.path.join(self.root, "psypick", "data"),
                        "--sitemap"], check=True, capture_output=True)
        again = ET.parse(os.path.join(self.root, "sitemap.xml")).getroot()
        self.assertEqual(len(list(again)), len(locs))

    def test_feed(self):
        root = ET.parse(os.path.join(self.root, "psypick", "feed.xml")).getroot()
        items = root.findall("channel/item")
        self.assertEqual(len(items), min(50, len(self.index["cases"])))
        for it in items:
            loc = it.findtext("link")
            self.assertTrue(os.path.exists(resolve("/", loc, self.root)), loc)


if __name__ == "__main__":
    unittest.main(verbosity=2)
