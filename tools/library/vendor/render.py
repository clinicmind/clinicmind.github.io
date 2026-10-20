# 複製自 clinicmind/clinicmind pipeline/（2026-10-20），不要在這裡修改。
"""共用渲染：單元資料 → 學術版 HTML、圖卡版 HTML。BOOK 由 build.py 依 book.json 設定。"""
import html, json, re, pathlib, subprocess, sys, shutil
HERE = pathlib.Path(__file__).parent
BOOK = ""   # build.py 設定
ASSETS = "../assets"   # 相對於 <book>/html/
E = html.escape

def plabel(p):
    return f"p. {p}" if not isinstance(p, tuple) else f"pp. {p[0]}–{p[1]}"

# ---------- SVG 工具 ----------
DARK = dict(bg="#1f2331", panel="#2a2f42", line="#454b63", text="#f3efe6", muted="#c4c0b6", acc="#f08a59", accfill="#3a2f33")
LIGHT = dict(bg="#fbf9f4", panel="#f1ede2", line="#d9d4c7", text="#1f2331", muted="#4f5568", acc="#a93f0e", accfill="#f6e6dc")

def _t(x, y, lines, fs, fill, anchor="middle", weight=None, lh=1.3):
    lines = lines.split("\n") if isinstance(lines, str) else lines
    y0 = y - (len(lines) - 1) * fs * lh / 2 + fs * 0.36
    w = f' font-weight="{weight}"' if weight else ""
    return "".join(f'<text x="{x}" y="{y0 + i * fs * lh:.1f}" font-size="{fs}" fill="{fill}" text-anchor="{anchor}"{w}>{E(l)}</text>' for i, l in enumerate(lines))

def _svg(w, h, body, label):
    return f'<svg class="fig" viewBox="0 0 {w} {h}" role="img" aria-label="{E(label)}">{body}</svg>'

def _arrow(x1, y1, x2, y2, c, sw=4):
    import math
    ang = math.atan2(y2 - y1, x2 - x1); L = 14
    ax = x2 - L * math.cos(ang - .45); ay = y2 - L * math.sin(ang - .45)
    bx = x2 - L * math.cos(ang + .45); by = y2 - L * math.sin(ang + .45)
    return f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{c}" stroke-width="{sw}" fill="none" stroke-linecap="round"/><path d="M{ax:.1f} {ay:.1f}L{x2} {y2}L{bx:.1f} {by:.1f}" stroke="{c}" stroke-width="{sw}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'

def svg_flow(items, hl=None, theme=DARK, w=936, fs=36, boxh=None, gap=54, label="流程圖", hmode=False):
    """垂直流程；items 為字串（可含 \\n）。hl 為要強調的索引。hmode=True 水平（學術版）。"""
    th = theme; n = len(items); out = []
    if hmode:
        gapx = 34; bw = (w - gapx * (n - 1)) / n; bh = boxh or 92
        for i, it in enumerate(items):
            x = i * (bw + gapx); h = i == hl
            out.append(f'<rect x="{x:.1f}" y="6" width="{bw:.1f}" height="{bh}" rx="10" fill="{th["accfill"] if h else th["panel"]}" stroke="{th["acc"] if h else th["line"]}" stroke-width="{3 if h else 1.5}"/>')
            out.append(_t(x + bw / 2, 6 + bh / 2, it, fs, th["text"], weight="700" if h else None))
            if i < n - 1: out.append(_arrow(x + bw + 4, 6 + bh / 2, x + bw + gapx - 4, 6 + bh / 2, th["muted"], 2.5))
        return _svg(w, bh + 12, "".join(out), label)
    bh = boxh or 104; y = 4
    for i, it in enumerate(items):
        h = i == hl; nl = it.count("\n") + 1; hh = max(bh, nl * fs * 1.3 + 36)
        out.append(f'<rect x="4" y="{y}" width="{w - 8}" height="{hh:.0f}" rx="22" fill="{th["accfill"] if h else th["panel"]}" stroke="{th["acc"] if h else th["line"]}" stroke-width="{4 if h else 2}"/>')
        out.append(_t(w / 2, y + hh / 2, it, fs, th["acc"] if h else th["text"], weight="700" if h else None))
        y += hh
        if i < n - 1:
            out.append(_arrow(w / 2, y + 6, w / 2, y + gap - 8, th["muted"], 4)); y += gap
    return _svg(w, y + 4, "".join(out), label)

def svg_layers(items, hl=None, theme=DARK, w=936, fs=36, label="層級圖", step=50):
    """巢狀矩形：items 由外到內（大 → 小）。每層標籤在該層頂端。"""
    th = theme; n = len(items); rowh = fs * 1.3 + 26
    H = (n - 1) * step + rowh * 1.0 + 70 + (n - 1) * 0
    inner_h = rowh + 90
    total = (n - 1) * (rowh + 14) + inner_h + 12
    out = []; y = 4
    for i, it in enumerate(items):
        h = i == hl; x = 4 + i * step; ww = w - 8 - 2 * i * step
        hh = total - 8 - i * (rowh + 14)
        out.append(f'<rect x="{x}" y="{y}" width="{ww}" height="{hh}" rx="24" fill="{th["accfill"] if h else (th["panel"] if i % 2 == 0 else th["bg"])}" stroke="{th["acc"] if h else th["line"]}" stroke-width="{4 if h else 2}"/>')
        out.append(_t(x + ww / 2, y + rowh / 2 + 8, it, fs, th["acc"] if h else th["text"], weight="700" if h else None))
        y += rowh + 14
    return _svg(w, total, "".join(out), label)

def svg_rows(items, theme=DARK, w=936, fs=34, label="清單圖", hl=None):
    """左側圓形字母／數字，右側說明；items=[(圓內字, 說明)]"""
    th = theme; out = []; y = 4
    for i, (k, t) in enumerate(items):
        nl = t.count("\n") + 1; hh = max(96, nl * fs * 1.3 + 24); h = i == hl
        out.append(f'<circle cx="52" cy="{y + hh / 2}" r="44" fill="{th["accfill"] if h else th["panel"]}" stroke="{th["acc"]}" stroke-width="3.5"/>')
        out.append(_t(52, y + hh / 2, k, 44, th["acc"], weight="700"))
        out.append(_t(124, y + hh / 2, t, fs, th["text"], anchor="start"))
        y += hh + 22
    return _svg(w, y, "".join(out), label)

def svg_hub(center, spokes, theme=DARK, w=936, fs=34, label="關係圖", hl=False):
    """中央圓 + 四到六個外圍框（上下排列在左右兩欄）。"""
    th = theme; n = len(spokes); half = (n + 1) // 2
    bw = 330; rowh = 120; H = half * rowh + 40
    cx, cy = w / 2, H / 2; out = []
    pos = []
    for i, s in enumerate(spokes):
        side = 0 if i < half else 1
        k = i if i < half else i - half
        cnt = half if side == 0 else n - half
        y = 20 + (H - 40) * (k + 0.5) / cnt - 46
        x = 4 if side == 0 else w - bw - 4
        pos.append((x, y, s))
    for x, y, s in pos:
        ex = x + bw if x < cx else x
        out.append(f'<path d="M{ex} {y + 46}L{cx + (-90 if x < cx else 90)} {cy}" stroke="{th["line"]}" stroke-width="3" fill="none"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="96" fill="{th["accfill"]}" stroke="{th["acc"]}" stroke-width="4"/>')
    out.append(_t(cx, cy, center, fs, th["acc"], weight="700"))
    for x, y, s in pos:
        out.append(f'<rect x="{x}" y="{y}" width="{bw}" height="92" rx="18" fill="{th["panel"]}" stroke="{th["line"]}" stroke-width="2"/>')
        out.append(_t(x + bw / 2, y + 46, s, fs - 2, th["text"]))
    return _svg(w, H, "".join(out), label)

def svg_bars(items, vmax=None, theme=DARK, w=936, fs=34, label="長條圖", hl=None, unit=""):
    """水平長條，從 0 起算；items=[(label, value)]。標籤在條上方。"""
    th = theme; vmax = vmax or max(v for _, v in items); out = []; y = 4; bh = 54
    for i, (lab, v) in enumerate(items):
        h = i == hl
        out.append(_t(4, y + fs * .6, lab, fs, th["text"], anchor="start"))
        y += fs * 1.2 + 6
        out.append(f'<rect x="4" y="{y}" width="{w - 8}" height="{bh}" rx="10" fill="{th["panel"]}"/>')
        out.append(f'<rect x="4" y="{y}" width="{max(8, (w - 8) * v / vmax):.0f}" height="{bh}" rx="10" fill="{th["acc"] if h else th["muted"]}"/>')
        out.append(_t(w - 16, y + bh / 2, f"{v}{unit}", fs - 4, th["text"] if not h else th["text"], anchor="end", weight="700"))
        y += bh + 30
    return _svg(w, y, "".join(out), label)

def svg_timeline(points, theme=DARK, w=936, fs=34, label="時間軸", hl=None):
    """垂直時間軸；points=[(標籤, 說明)]"""
    th = theme; out = []; y = 10; x0 = 36
    n = len(points)
    for i, (a, b) in enumerate(points):
        nl = (b.count("\n") + 1)
        hh = max(120, nl * fs * 1.3 + 56)
        h = i == hl
        if i < n - 1: out.append(f'<path d="M{x0} {y + 30}L{x0} {y + hh + 30}" stroke="{th["line"]}" stroke-width="5"/>')
        out.append(f'<circle cx="{x0}" cy="{y + 30}" r="20" fill="{th["acc"] if h else th["bg"]}" stroke="{th["acc"]}" stroke-width="5"/>')
        out.append(_t(x0 + 56, y + 30, a, fs, th["acc"], anchor="start", weight="700"))
        out.append(_t(x0 + 56, y + 30 + fs * 1.5 + (nl - 1) * fs * .65, b, fs - 2, th["text"], anchor="start"))
        y += hh
    return _svg(w, y, "".join(out), label)

def svg_vs(left, right, theme=DARK, w=936, fs=34, label="對照圖", hl=1):
    """左右兩欄；left/right=(標題, [列])"""
    th = theme; out = []; bw = (w - 36) / 2
    rows = max(len(left[1]), len(right[1])); H = 90 + rows * (fs * 1.3 * 2 + 20) + 20
    for k, (side, x) in enumerate(((left, 4), (right, 4 + bw + 28))):
        h = k == hl
        out.append(f'<rect x="{x}" y="4" width="{bw}" height="{H}" rx="22" fill="{th["accfill"] if h else th["panel"]}" stroke="{th["acc"] if h else th["line"]}" stroke-width="{4 if h else 2}"/>')
        out.append(_t(x + bw / 2, 56, side[0], fs + 4, th["acc"] if h else th["text"], weight="700"))
        yy = 124
        for r in side[1]:
            nl = r.count("\n") + 1
            out.append(_t(x + bw / 2, yy + (nl - 1) * fs * .65, r, fs - 2, th["text"]))
            yy += fs * 1.3 * 2 + 20
    return _svg(w, H + 8, "".join(out), label)

def svg_cycle(items, theme=DARK, w=936, fs=34, label="循環圖", hl=None):
    """3–4 個節點的循環；箭頭沿順時針方向。"""
    th = theme; n = len(items); H = 700; cx = w / 2; cy = H / 2
    bw, bh = 340, 110; rx = w - bw / 2 - 6; lx = bw / 2 + 6
    if n == 4:
        pts = [(cx, 70), (rx, cy), (cx, H - 70), (lx, cy)]
        arrows = [((cx + bw / 2 + 12, 82), (rx - 20, cy - bh / 2 - 10)), ((rx - 20, cy + bh / 2 + 10), (cx + bw / 2 + 12, H - 82)),
                  ((cx - bw / 2 - 12, H - 82), (lx + 20, cy + bh / 2 + 10)), ((lx + 20, cy - bh / 2 - 10), (cx - bw / 2 - 12, 82))]
    else:
        y3 = H - 120
        pts = [(cx, 70), (rx, y3), (lx, y3)]
        arrows = [((cx + bw / 2 + 12, 90), (rx - 20, y3 - bh / 2 - 10)), ((rx - bw / 2 - 12, y3), (lx + bw / 2 + 12, y3)),
                  ((lx + 20, y3 - bh / 2 - 10), (cx - bw / 2 - 12, 90))]
    out = [_arrow(round(a[0]), round(a[1]), round(b[0]), round(b[1]), th["muted"], 4) for a, b in arrows]
    for i, (x, y) in enumerate(pts):
        h = i == hl
        out.append(f'<rect x="{x - bw / 2}" y="{y - bh / 2}" width="{bw}" height="{bh}" rx="20" fill="{th["accfill"] if h else th["panel"]}" stroke="{th["acc"] if h else th["line"]}" stroke-width="{4 if h else 2}"/>')
        out.append(_t(x, y, items[i], fs, th["acc"] if h else th["text"], weight="700" if h else None))
    return _svg(w, H, "".join(out), label)

# ---------- 圖卡版 ----------
def s_cover(kicker, title, sub, svg=""):
    return f'<section class="slide cover"><div class="kicker">{E(kicker)}</div><h1>{title}</h1><p class="lead">{sub}</p><div class="grow"></div>{svg}<div class="swipe">滑動閱讀 →</div></section>'

def s_concept(kicker, title, lead, fig="", cap=""):
    c = f'<p class="cap" style="margin-top:20px">{cap}</p>' if cap else ""
    return f'<section class="slide"><div class="kicker">{E(kicker)}</div><h1>{title}</h1><p class="lead">{lead}</p><div class="grow"></div>{fig}{c}<div class="grow"></div></section>'

def s_steps(kicker, title, steps, lead=""):
    ld = f'<p class="lead">{lead}</p>' if lead else ""
    st = "".join(f'<div class="step"><div class="n">{i + 1}</div><div><h2>{a}</h2><p>{b}</p></div></div>' for i, (a, b) in enumerate(steps))
    return f'<section class="slide"><div class="kicker">{E(kicker)}</div><h1>{title}</h1>{ld}<div class="grow"></div><div class="stack">{st}</div><div class="grow"></div></section>'

def s_boxes(kicker, title, boxes, lead="", cap=""):
    """boxes=[(標題html, 說明html, hl)]"""
    ld = f'<p class="lead">{lead}</p>' if lead else ""
    bx = "".join(f'<div class="box{" hl" if h else ""}"><h2>{a}</h2><p style="margin-top:12px">{b}</p></div>' for a, b, h in boxes)
    c = f'<p class="cap" style="margin-top:28px">{cap}</p>' if cap else ""
    return f'<section class="slide"><div class="kicker">{E(kicker)}</div><h1>{title}</h1>{ld}<div class="grow"></div><div class="stack">{bx}</div>{c}<div class="grow"></div></section>'

def s_quote(kicker, title, en, zh, page, lead=""):
    ld = f'<p class="lead">{lead}</p>' if lead else ""
    return (f'<section class="slide"><div class="kicker">{E(kicker)}</div><h1>{title}</h1>{ld}<div class="grow"></div>'
            f'<div class="box hl"><p style="font-size:36px">{E(en)}</p><p class="cap" style="margin-top:22px;text-align:center">{E(zh)}</p></div>'
            f'<p class="cap" style="margin-top:22px">{BOOK}，{plabel(page)}。中譯為本包自譯。</p><div class="grow"></div></section>')

def s_summary(points, title="帶走這三件事"):
    bx = "".join(f'<div class="box{" hl" if i == 0 else ""}"><p>{p}</p></div>' for i, p in enumerate(points))
    return f'<section class="slide"><div class="kicker">摘要</div><h1>{title}</h1><div class="grow"></div><div class="stack">{bx}</div><div class="grow"></div></section>'

def s_action(text, lead="只做這一件事。"):
    return f'<section class="slide cover"><div class="kicker">下一步</div><h1>{text}</h1><p class="lead">{lead}</p></section>'

# ---------- 組頁 ----------
def infographic_html(u):
    return _doc("infographic", u["label"], u["label"], "".join(u["slides"]))

def academic_blocks(u):
    b = []
    b.append(f'<h1 class="brk">{E(u["title"])}</h1><p class="meta">{BOOK}｜{E(u.get("authors",""))}｜{E(u["en"])}｜{plabel(u["pages"])}｜章節 {u["no"]} / {u["total"]}</p>')
    b.append('<h2>學習目標</h2><ol>' + "".join(f"<li>{x}</li>" for x in u["objectives"]) + "</ol>")
    b.append(f'<h2>摘要</h2><p>{u["summary"]}</p>')
    b.append('<h2>關鍵洞見</h2><ul>' + "".join(f"<li><em>{a}</em>：{c}</li>" for a, c in u["insights"]) + "</ul>")
    b.append('<h2>原文引用</h2><p class="note">英文引文逐字查證，頁碼為原書印刷頁碼。中譯為本包自譯。</p>')
    for q in u["quotes"]:
        b.append(f'<blockquote>{E(q["en"])}<span class="zh">中譯：{E(q["zh"])}</span><cite>{BOOK}，{plabel(q["p"])}</cite></blockquote>')
    c = u.get("close")
    if c:
        b.append('<h2>精讀</h2>')
        b.append(f'<blockquote>{E(c["en"])}<span class="zh">中譯：{E(c["zh"])}</span><cite>{BOOK}，{plabel(c["p"])}</cite></blockquote>')
        b.append('<table class="cr">' + "".join(f'<tr><td>{E(a)}</td><td>{x}</td></tr>' for a, x in c["notes"]) + "</table>")
    f = u["framework"]
    b.append(f'<h2>實務推理框架</h2><p class="note">{f["intro"]}</p>')
    b.append(f["svg"])
    b.append("<ol>" + "".join(f"<li>{x}</li>" for x in f["steps"]) + "</ol>")
    if u.get("culture"):
        a, t = u["culture"]
        b.append(f'<h2>華人情境</h2><div class="box"><p><em>{a}</em></p><p style="margin-top:2mm">{t}</p></div>')
    b.append(f'<p class="note">限制：{u["limits"]}</p>')
    return b

def _doc(css, title, label, body):
    return (f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><title>{E(title)}</title>'
            f'<link rel="stylesheet" href="{ASSETS}/{css}.css"><script src="{ASSETS}/{css}.js"></script></head>'
            f'<body data-label="{E(label)}">{body}</body></html>')

def academic_html(u):
    return _doc("academic", u["title"], u["label"], f'<div id="flow">{"".join(academic_blocks(u))}</div>')

def _em(x): return re.sub(r"\*(.+?)\*", r"<em>\1</em>", E(x))

def book_academic_html(bk, units):
    """全書一份：封面＋目錄＋每章（每章從新頁開始）。bk = book.json。"""
    b = [f'<h1>{E(bk.get("title", BOOK))}</h1><p class="meta">{E(BOOK)}｜{E(bk.get("authors",""))}｜全書教學包・學術版</p>']
    if bk.get("intro"): b.append(f'<h2>導讀</h2><p>{bk["intro"]}</p>')
    b.append('<h2>目錄</h2><ol>' + "".join(f'<li>{E(u["title"])}（{plabel(u["pages"])}）</li>' for u in units) + '</ol>')
    for u in units: b += academic_blocks(u)
    if bk.get("summary"):
        b.append('<h1 class="brk">全書總結</h1><ol>' + "".join(f"<li>{_em(x)}</li>" for x in bk["summary"]) + '</ol>')
    return _doc("academic", bk.get("title", BOOK), bk.get("short", BOOK), f'<div id="flow">{"".join(b)}</div>')

def book_infographic_html(bk, units):
    """全書一份：書封＋章節地圖＋各章圖卡（每張帶章名）＋全書摘要與行動。"""
    s = [s_cover("全書教學包", E(bk.get("title", BOOK)), E(bk.get("authors", "")))]
    ch = [E(u["label"].split("｜")[-1]) for u in units]
    for i in range(0, len(ch), 4):
        s.append(s_boxes("章節地圖", f"本包涵蓋 <em>{len(ch)}</em> 章" if i == 0 else "章節地圖（續）", [(x, "", False) for x in ch[i:i + 4]]))
    for u in units:
        lab = E(u["label"])
        s += [x.replace('<section class="slide', f'<section data-label="{lab}" class="slide', 1) for x in u["slides"]]
    if bk.get("summary"): s.append(s_summary([_em(x) for x in bk["summary"][:3]], "全書帶走這三件事"))
    if bk.get("action"): s.append(s_action(_em(bk["action"])))
    return _doc("infographic", bk.get("title", BOOK), bk.get("short", BOOK), "".join(s))
