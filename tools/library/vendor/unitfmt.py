# 複製自 clinicmind/clinicmind pipeline/（2026-10-20），不要在這裡修改。
"""單元文字檔（units/*.md）→ 單元資料 U；圖卡 DSL → 投影片 HTML。格式見 README.md。"""
import re, html
import render as R
from render import E

SECS = {"目標": "objectives", "摘要": "summary", "洞見": "insights", "引文": "quotes", "精讀": "close",
        "框架": "framework", "華人": "culture", "限制": "limits", "圖卡": "slides"}

def em(s):  # *重點* → <em>
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", E(s).replace("\\n", "<br>"))

def pg(s):
    s = s.strip().replace("–", "-")
    a, _, b = s.partition("-")
    return (int(a), int(b)) if b else int(a)

def parse(path, no=1, total=1):
    txt = path.read_text(encoding="utf-8")
    U = dict(id=path.stem, no=no, total=total, authors="", objectives=[], insights=[], quotes=[], close=None,
             framework=dict(intro="", diag=None, steps=[]), culture=None, limits="", slides=None, summary="")
    sec = None; buf = []
    def flush():
        if sec is None: return
        body = [l for l in buf]
        if sec == "summary": U["summary"] = " ".join(l.strip() for l in body if l.strip())
        elif sec == "limits": U["limits"] = " ".join(l.strip() for l in body if l.strip())
        elif sec == "objectives": U["objectives"] = [l[2:].strip() for l in body if l.startswith("- ")]
        elif sec == "insights":
            for l in body:
                if l.startswith("- "):
                    k, _, d = l[2:].partition("：" if "：" in l else ":"); U["insights"].append((k.strip(), d.strip()))
        elif sec == "quotes":
            for l in body:
                if l.startswith("- "):
                    p, en, zh = [x.strip() for x in l[2:].split("|", 2)]; U["quotes"].append(dict(p=pg(p), en=en, zh=zh))
        elif sec == "close":
            head = next(l for l in body if "|" in l and not l.startswith("- "))
            p, en, zh = [x.strip() for x in head.split("|", 2)]
            notes = [tuple(x.strip() for x in l[2:].split("|", 1)) for l in body if l.startswith("- ")]
            U["close"] = dict(p=pg(p), en=en, zh=zh, notes=notes)
        elif sec == "framework":
            f = U["framework"]
            for l in body:
                if l.startswith("@"): f["diag"] = l[1:].strip()
                elif l.startswith("- "): f["steps"].append(l[2:].strip())
                elif l.strip(): f["intro"] += l.strip()
        elif sec == "culture":
            t = " ".join(l.strip() for l in body if l.strip()); a, _, b = t.partition("|"); U["culture"] = (a.strip(), b.strip())
        elif sec == "slides": U["slides"] = [l.strip() for l in body if l.strip() and not l.startswith("#")]
    for line in txt.splitlines():
        if line.startswith("# "): U["title"] = line[2:].strip(); continue
        m = re.match(r"@(\w+):\s*(.*)", line)
        if m and sec is None:
            k, v = m.groups()
            if k == "pages": U["pages"] = pg(v)
            else: U[k] = v
            continue
        m = re.match(r"## (\S+)", line)
        if m and m.group(1) in SECS:
            flush(); sec = SECS[m.group(1)]; buf = []; continue
        buf.append(line)
    flush()
    U.setdefault("label", U["title"]); U.setdefault("en", "")
    U["id"] = U.get("id") or path.stem
    return U

# ---------- 圖 DSL ----------
def _items(s): return [x.strip().replace("\\n", "\n") for x in s.split(";") if x.strip()]
def _hl(items):
    hl = None; out = []
    for i, x in enumerate(items):
        if x.startswith("!"): hl = i; x = x[1:]
        out.append(x)
    return out, hl

def diagram(spec, theme, academic=False):
    """spec 例：flow: a;!b;c ｜ vs: 左標: x,y ~ 右標: z,w ｜ rows: A:說明;B:說明 ｜ bars: a=12;b=5 ｜ hub: 中心: a;b;c"""
    if not spec: return ""
    kind, _, rest = spec.partition(":"); kind = kind.strip(); rest = rest.strip()
    kw = dict(theme=theme)
    if academic: kw.update(w=640, fs=14)
    if kind == "flow":
        items, hl = _hl(_items(rest))
        if academic: kw.update(hmode=True, boxh=96)
        return R.svg_flow(items, hl=hl, label="流程圖", **kw)
    if kind in ("layers", "cycle"):
        items, hl = _hl(_items(rest)); return getattr(R, "svg_" + kind)(items, hl=hl, **kw)
    if kind == "rows":
        items, hl = _hl(_items(rest)); return R.svg_rows([tuple(x.split(":", 1)) for x in items], hl=hl, **kw)
    if kind == "timeline":
        items, hl = _hl(_items(rest)); return R.svg_timeline([tuple(x.split(":", 1)) for x in items], hl=hl, **kw)
    if kind == "bars":
        items, hl = _hl(_items(rest)); return R.svg_bars([(a, float(b)) for a, b in (x.split("=", 1) for x in items)], hl=hl, **kw)
    if kind == "hub":
        c, _, sp = rest.partition(":"); return R.svg_hub(c.strip(), _items(sp), **kw)
    if kind == "vs":
        sides = []
        for part in rest.split("~"):
            h, _, rows = part.partition(":"); sides.append((h.strip(), [r.strip().replace("\\n", "\n") for r in rows.split(",") if r.strip()]))
        return R.svg_vs(sides[0], sides[1], **kw)
    raise ValueError("未知圖型: " + kind)

# ---------- 圖卡 DSL ----------
def _cite(U, i): return ""

def slide(U, line):
    f = [x.strip() for x in line.split("|")] + [""] * 5
    kind, kick, title, lead, extra = f[:5]
    d = lambda s: diagram(s, R.DARK)
    ld = em(lead)
    if kind == "cover":
        return R.s_cover(kick, em(title), ld, d(extra))
    if kind == "c":
        return R.s_concept(kick, em(title), ld, d(extra))
    if kind == "q":
        q = U["quotes"][int(extra) - 1]; return R.s_quote(kick, em(title), q["en"], q["zh"], q["p"], ld)
    if kind == "steps":
        return R.s_steps(kick, em(title), [tuple(em(y) for y in x.split(":", 1)) for x in _items(extra)], ld)
    if kind == "box":
        its = _items(extra); return R.s_boxes(kick, em(title), [(em(x.split(":", 1)[0]), em(x.split(":", 1)[1]) if ":" in x else "", i == 0) for i, x in enumerate(its)], ld)
    if kind == "sum":
        return R.s_summary([em(x) for x in _items(extra)], title or "帶走這三件事")
    if kind == "act":
        return R.s_action(em(title), ld or "只做這一件事。")
    raise ValueError("未知頁型: " + kind)

def _strip_p(s): return re.sub(r"[（(]p+\.[^)）]*[)）]\s*[。.]?$", "", s).strip()

def auto(U, what):
    """@insights／@quotes：每個洞見一頁、每句引文一頁。"""
    out = []
    if what == "insights":
        for k, dsc in U["insights"]:
            out.append(R.s_concept("洞見", f"<em>{E(k)}</em>", em(dsc)))
    elif what == "quotes":
        for i, q in enumerate(U["quotes"]):
            out.append(R.s_quote("原文", f"原書的<em>說法</em>", q["en"], q["zh"], q["p"]))
    return out

def slides_html(U):
    lines = U["slides"]
    if lines is None:  # 全自動版型：封面→洞見→引文→框架→華人→摘要→行動
        f = U["framework"]; lines = [f"cover | {U['label'].split('｜')[-1]} | {U['title']} | {U.get('en','')} | {f['diag'] or ''}", "@insights", "@quotes"]
        if f["diag"]: lines.append(f"c | 框架 | 實務*推理* | {f['intro']} | {f['diag']}")
        if U["culture"]: lines.append(f"box | 華人情境 | {U['culture'][0]} | 臨床詮釋，非原書結論 | 臨床詮釋:{U['culture'][1]}")
        lines.append("sum |  |  |  | " + ";".join(k + "：" + _strip_p(d) for k, d in U["insights"][:3]))
        lines.append("act |  | " + (f["steps"][-1] if f["steps"] else "回到臨床") + " | |")
    out = []
    for l in lines:
        if l.startswith("@"): out += auto(U, l[1:].strip())
        else: out.append(slide(U, l))
    return out

def finalize(U):
    """補上 render.py 需要的欄位：framework.svg、slides（HTML 清單）、插入 em 的標題。"""
    f = U["framework"]; f["svg"] = diagram(f["diag"], R.LIGHT, academic=True) if f["diag"] else ""
    U["slides"] = slides_html(U)
    return U
