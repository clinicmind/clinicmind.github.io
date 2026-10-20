"""全書 15 題測驗：解析 quiz.md、檢查出題規則、產生前端資料（規劃第 8.3 節）。

quiz.md 格式見規劃 8.3。本模組不寫檔；由 build.py 呼叫。
答案不以明文輸出：每題只給 key = SHA-256(slug|題號|正確選項文字) 前 12 碼。
注意：靜態網站無法真正隱藏答案（規劃 8.6 第 6 點）。
"""
import hashlib, re

META = re.compile(r"^@(\w+): (.*)$")
NORM_DROP = re.compile(r"[\s　「」『』“”\"'‘’（）()，,、：:；;。.！!？?…—–\-｜|/*\\n]")
TYPES = ("記憶", "理解", "應用")


def norm(s):
    return NORM_DROP.sub("", s)


def key_of(slug, qid, correct):
    return hashlib.sha256(f"{slug}|{qid}|{correct}".encode("utf-8")).hexdigest()[:12]


def parse(text):
    """回傳題目 list（每題為 dict）。"""
    qs = []
    parts = re.split(r"\n## (Q\d+)\n", "\n" + text)
    for qid, body in zip(parts[1::2], parts[2::2]):
        q = {"id": qid, "meta": {}, "options": [], "stars": 0, "stem": [], "hint": "", "explain": ""}
        for line in body.splitlines():
            s = line.rstrip()
            if not s:
                continue
            m = META.match(s)
            if m:
                q["meta"][m.group(1)] = m.group(2).strip()
            elif s.startswith("- "):
                opt = s[2:].strip()
                if opt.startswith("*"):
                    q["stars"] += 1
                    opt = opt[1:].strip()
                q["options"].append(opt)
                if s[2:].startswith("*"):
                    q["correct"] = opt
            elif s.startswith("> 提醒："):
                q["hint"] = s[len("> 提醒："):].strip()
            elif s.startswith("> 解說："):
                q["explain"] = s[len("> 解說："):].strip()
            elif not s.startswith(">"):
                q["stem"].append(s.strip())
        q["stem"] = " ".join(q["stem"])
        qs.append(q)
    return qs


def validate(text, units):
    """units：{單元檔名（不含 .md）: md 全文}。回傳 (題目, 問題清單)。"""
    qs = parse(text)
    probs = []
    if len(qs) != 15:
        probs.append(f"題數 {len(qs)}，應為 15")
    types = {t: 0 for t in TYPES}
    used = set()
    for q in qs:
        qid, m = q["id"], q["meta"]
        unit, sec, typ = m.get("unit", ""), m.get("section", ""), m.get("type", "")
        if unit not in units:
            probs.append(f"{qid} @unit 不存在：{unit}")
            continue
        used.add(unit)
        if typ not in types:
            probs.append(f"{qid} @type 不明：{typ}")
        else:
            types[typ] += 1
        if sec not in ("insights", "framework", "close", "quotes", "culture"):
            probs.append(f"{qid} @section 不明：{sec}")
        if len(q["options"]) != 4 or q["stars"] != 1:
            probs.append(f"{qid} 須有 4 個選項且只有 1 個 *")
            continue
        if not q["hint"] or not q["explain"]:
            probs.append(f"{qid} 缺提醒或解說")
            continue
        if norm(q["correct"]) and norm(q["correct"]) in norm(q["hint"]):
            probs.append(f"{qid} 提醒洩漏正確選項")
        src = norm(units[unit])
        for sent in re.split(r"[。！？；]", q["explain"]):
            if len(norm(sent)) >= 6 and norm(sent) not in src:
                probs.append(f"{qid} 解說找不到依據：{sent[:30]}")
        if re.search(r"以上皆是|以上皆非", " ".join(q["options"])):
            probs.append(f"{qid} 用了禁用選項")
        lens = [len(o) for o in q["options"]]
        if max(lens) > 2.5 * min(lens) + 10:
            probs.append(f"{qid} 選項長度相差太大")
    if types["記憶"] > 5 or types["理解"] < 5 or types["應用"] < 5:
        probs.append(f"題型比例不符：{types}")
    if len(used) * 2 < len(units):
        probs.append(f"只涵蓋 {len(used)}/{len(units)} 章，至少一半")
    return qs, probs


def public_data(slug, title, en, chapters, qs):
    """前端資料：不含正確選項明文。"""
    out = []
    for q in qs:
        out.append({"id": q["id"], "stem": q["stem"], "options": q["options"],
                    "unit": q["meta"]["unit"], "section": q["meta"]["section"],
                    "hint": q["hint"], "explain": q["explain"],
                    "key": key_of(slug, q["id"], q["correct"])})
    return {"slug": slug, "title": title, "en": en, "chapters": chapters, "questions": out}
