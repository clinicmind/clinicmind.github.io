#!/usr/bin/env python3
"""inbox_to_cases.py 的測試。全部在暫存複本上跑，不改 psypick/data/。

用法：python3 tools/psypick/test_inbox_to_cases.py
"""

import copy
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
REAL_DATA = os.path.join(REPO, "psypick", "data")
sys.path.insert(0, HERE)
import inbox_to_cases as conv  # noqa: E402

LEVEL_ZH = {0: "個人經驗或評論", 1: "產品宣稱", 2: "前導或質性研究",
            3: "對照試驗", 4: "系統性回顧或統合分析"}


def case_to_item(c):
    """把現有 case 檔反推成 inbox v2 item（供往返測試）。"""
    p = c["posts"][0]
    item = {
        "type": "case", "slug": c["slug"],
        "title_zh": c["title_zh"], "title_en": c["title_en"],
        "summary_zh": c["summary_zh"], "summary_en": c["summary_en"],
        "category": c["category"], "kind": c["kind"],
        "evidence_hint": LEVEL_ZH[c["evidence_level"]],
        "evidence_note": c["evidence_note"],
        "evidence_quote": c["evidence_quote"],
        "ethics_flags": c["ethics_flags"],
        "psych_concepts": c["psych_concepts"],
        "caution": c["caution"], "verify_needed": c["verify_needed"],
        "verify_reason": c["verify_reason"], "brief_zh": c["brief_zh"],
        "brief_en": c["brief_en"], "model_names": c["model_names"],
        "tags": c["tags"], "population": c["population"],
        "supervision_questions": c["supervision_questions"],
        "related": c["related"],
        "page_date": (p.get("posted_at") or "")[:10],
        "source": {k: p[k] for k in ("platform", "url", "author_handle",
                                     "author_name", "title", "content")},
    }
    if c.get("training"):
        item["training"] = c["training"]
    return item


def sample_item(**over):
    it = {
        "type": "case",
        "title_zh": "測試研究", "title_en": "A test study of something",
        "summary_zh": "摘要。", "summary_en": "Summary.",
        "category": "研究與證據", "kind": "research",
        "evidence_hint": "對照試驗", "evidence_note": "RCT",
        "evidence_quote": "short verbatim quote",
        "caution": "小樣本。", "verify_needed": False,
        "brief_zh": ["重點一"], "tags": ["測試"], "population": ["成人"],
        "supervision_questions": ["問題？"],
        "page_date": "2026-11-20",
        "source": {"url": "https://example.org/unique-test-study",
                   "title": "A Test Study", "author_name": "Example Journal"},
    }
    it.update(over)
    return it


def training_item(**over):
    it = sample_item(
        title_en="A free online test workshop", title_zh="測試工作坊",
        category="進修培訓", kind="training", evidence_hint="個人經驗或評論",
        evidence_note="培訓課程",
        source={"url": "https://example.org/unique-test-workshop",
                "title": "Workshop", "author_name": "Example Org"},
        training={"provider": "Example Org", "format": "線上直播",
                  "price": "Free", "price_tier": "免費",
                  "event_date": "2026-12-30",
                  "signup_url": "https://example.org/unique-test-workshop"})
    it.update(over)
    return it


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.data = os.path.join(self.tmp, "data")
        shutil.copytree(REAL_DATA, self.data)
        for name in ("index-lite.json", "family-lite.json", "version.json"):
            p = os.path.join(self.data, name)
            if os.path.exists(p):
                os.remove(p)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_conv(self, items, *extra):
        path = os.path.join(self.tmp, "inbox.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"version": 2, "items": items}, f, ensure_ascii=False)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = conv.main([path, "--data-dir", self.data,
                            "--now", "2026-11-25T01:00:00+00:00"]
                           + list(extra))
        return rc, buf.getvalue()

    def case_path(self, slug):
        return os.path.join(self.data, "cases", slug + ".json")

    def n_cases(self):
        return len(os.listdir(os.path.join(self.data, "cases")))


class TestConverter(Base):
    def test_roundtrip_existing_1124(self):
        """11-24 上架的條目反推成 inbox 再轉換，應與現有檔 0 差異。"""
        cases_dir = os.path.join(REAL_DATA, "cases")
        originals = []
        for fn in sorted(os.listdir(cases_dir)):
            c = conv.load_json(os.path.join(cases_dir, fn))
            if (c.get("first_seen_at") or "").startswith("2026-11-24") \
                    and "poster" not in c:
                originals.append(c)
        self.assertGreater(len(originals), 0)
        kinds, levels = conv.load_config(REAL_DATA)
        checked, gaps = 0, []
        for c in originals:
            out, errs = conv.convert_item(case_to_item(c), c["slug"], kinds,
                                          levels, c["first_seen_at"])
            if errs:
                # 現有資料本身缺必填欄位（新規則會擋），列出但不當失敗
                gaps.extend(errs)
                continue
            checked += 1
            self.assertEqual(out, c, c["slug"])
            self.assertEqual(list(out.keys()), list(c.keys()), c["slug"])
        for g in gaps:
            print("\n  現有資料缺口：", g, end="")
        self.assertGreaterEqual(checked, len(originals) - 2)

    def test_writes_and_validates(self):
        before = self.n_cases()
        rc, out = self.run_conv([sample_item(), training_item(),
                                 {"type": "family", "title_zh": "x"}])
        self.assertEqual(rc, 0, out)
        self.assertIn("VALIDATION PASSED", out)
        self.assertIn("type=family", out)
        self.assertEqual(self.n_cases(), before + 2)
        c = conv.load_json(self.case_path("a-test-study-of-something"))
        self.assertEqual(c["evidence_level"], 3)
        self.assertEqual(c["posts"][0]["posted_at"],
                         "2026-11-20T00:00:00+00:00")
        idx = conv.load_json(os.path.join(self.data, "index.json"))
        self.assertIn("a-free-online-test-workshop",
                      [e["slug"] for e in idx["cases"]])

    def test_legacy_category_mapped(self):
        rc, out = self.run_conv([sample_item(category="評估與篩檢")])
        self.assertEqual(rc, 0, out)
        c = conv.load_json(self.case_path("a-test-study-of-something"))
        self.assertEqual(c["category"], "臨床實務")

    def test_error_means_nothing_written(self):
        before = self.n_cases()
        rc, out = self.run_conv([sample_item(),
                                 training_item(category="奇怪分類")])
        self.assertEqual(rc, 1)
        self.assertIn("奇怪分類", out)
        self.assertEqual(self.n_cases(), before)

    def test_field_rules(self):
        cases = [
            (sample_item(evidence_quote="x" * 41), "超過 40 字"),
            (sample_item(page_date=""), "verify_needed 必須是 true"),
            (sample_item(page_date="", verify_needed=True), "verify_reason"),
            (sample_item(evidence_hint="很強"), "evidence_hint"),
            (sample_item(tags=[]), "tags"),
            (sample_item(source={"url": "https://e.org/x"}),
             "source.author_name"),
            (training_item(training={"provider": "X", "format": "線上",
                                     "event_date": "12月30日",
                                     "signup_url": ""}),
             "training.signup_url"),
            (training_item(training={"provider": "X", "format": "線上",
                                     "event_date": "12月30日",
                                     "signup_url": "https://e.org/y"}),
             "event_date"),
        ]
        for item, needle in cases:
            rc, out = self.run_conv([item])
            self.assertEqual(rc, 1, needle)
            self.assertIn(needle, out)

    def test_no_page_date_ok_when_flagged(self):
        rc, out = self.run_conv([sample_item(
            page_date="", verify_needed=True, verify_reason="原文頁面冇日期")])
        self.assertEqual(rc, 0, out)
        c = conv.load_json(self.case_path("a-test-study-of-something"))
        self.assertEqual(c["posts"][0]["posted_at"], "")

    def test_duplicates_skipped(self):
        cases_dir = os.path.join(self.data, "cases")
        fn = sorted(os.listdir(cases_dir))[0]
        old = conv.load_json(os.path.join(cases_dir, fn))
        before = self.n_cases()
        same_slug = sample_item(slug=old["slug"])
        same_url = sample_item(
            title_en="Another title",
            source={"url": old["posts"][0]["url"].rstrip("/") + "/",
                    "title": "t", "author_name": "a"})
        rc, out = self.run_conv([same_slug, same_url])
        self.assertEqual(rc, 0, out)
        self.assertIn("已存在", out)
        self.assertIn("來源網址已見於", out)
        self.assertEqual(self.n_cases(), before)
        self.assertEqual(conv.load_json(os.path.join(cases_dir, fn)), old)

    def test_rollback_when_validate_fails(self):
        """validate.py (d) 擋實體培訓 → 新檔刪走、index.json 還原。"""
        idx_path = os.path.join(self.data, "index.json")
        with open(idx_path, "rb") as f:
            idx_before = f.read()
        before = self.n_cases()
        bad = training_item()
        bad["training"]["format"] = "實體面授"
        rc, out = self.run_conv([sample_item(), bad])
        self.assertEqual(rc, 1)
        self.assertIn("ROLLED BACK", out)
        self.assertEqual(self.n_cases(), before)
        with open(idx_path, "rb") as f:
            self.assertEqual(f.read(), idx_before)
        self.assertFalse(os.path.exists(
            os.path.join(self.data, "version.json")))

    def test_slugify(self):
        self.assertEqual(conv.slugify("DBT Crash Course for Clinicians!"),
                         "dbt-crash-course-for-clinicians")
        self.assertLessEqual(len(conv.slugify("word " * 40)), conv.SLUG_MAX)


if __name__ == "__main__":
    unittest.main(verbosity=2)
