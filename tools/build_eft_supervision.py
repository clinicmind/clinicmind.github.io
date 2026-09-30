#!/usr/bin/env python3
"""把 EFT 督導教材（clinicmind/clinicmind 的 teaching/eft-supervision）轉成網站頁面。

用法：python3 tools/build_eft_supervision.py <teaching/eft-supervision 的路徑>
需要 python 套件 markdown。輸出到 eft-supervision/（會覆寫）。
教師版（解答與帶領指引）刻意不發布。
"""
import html, pathlib, re, shutil, sys
import markdown

SITE = pathlib.Path(__file__).resolve().parent.parent
OUT = SITE / 'eft-supervision'

UNITS = [
    ('1', 'EFT 督導的基礎：理論、原則與督導者角色', '叢書序＋第1章'),
    ('2', '督導模式的基本向度：能力、目標、督導者回應與事件本位模式', '第2章'),
    ('3', '督導的歷程：同盟、人際技能、個案概念化與介入技能', '第3章'),
    ('4', '常見督導議題（一）：同盟裂痕與人際技能', '第4章'),
    ('5', '常見督導議題（二）：技術面的困難', '第5章'),
    ('6', '證據基礎與未來方向', '第6–7章'),
]
PDFS = {
    '1': ['單元1_學術內容.pdf', '單元1_資訊圖_完整版_1080.pdf',
          '單元1_工作單A_概念整合_學生版.pdf', '單元1_工作單B_臨床應用_學生版.pdf'],
}
for n, *_ in UNITS[1:]:
    PDFS[n] = [f'單元{n}_學術內容.pdf', f'單元{n}_資訊圖_完整版_1080.pdf']

PDF_LABEL = {'學術內容': '學術內容 PDF', '資訊圖': '資訊圖 PDF', '工作單A': '工作單 A（概念整合）', '工作單B': '工作單 B（臨床應用）'}

HEADER = '''<header>
        <a class="logo" href="../index.html">ClinicMind</a>
        <nav aria-label="主要導覽">
            <ul>
                <li><a href="../eft.html">認識 EFT</a></li>
                <li><a href="index.html">EFT 督導學習系列</a></li>
                <li><a href="../trauma.html">認識創傷</a></li>
                <li><a href="../resources.html">自助資源</a></li>
                <li><a href="../index.html#booking" class="btn-reserve">預約諮詢</a></li>
            </ul>
        </nav>
    </header>'''

FOOTER = '''<footer>
        <div class="footer-links">
            <a href="../index.html">首頁</a>
            <a href="../eft.html">認識 EFT</a>
            <a href="index.html">EFT 督導學習系列</a>
            <a href="../trauma.html">認識創傷</a>
            <a href="../resources.html">自助資源</a>
        </div>
        <p>教學用途。內容依據 Greenberg, L. S., &amp; Tomescu, L. R. (2017). <i>Supervision Essentials for Emotion-Focused Therapy</i>. APA. 整理改寫，並非原書翻譯；所有案例皆為綜合改寫之假想情境。</p>
        <div class="copyright">&copy; 2026 ClinicMind 臨床心語. All Rights Reserved.</div>
    </footer>'''


def page(title, desc, body, extra_head=''):
    return f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)} | ClinicMind 臨床心理諮商</title>
    <meta name="description" content="{html.escape(desc)}">
    <meta property="og:locale" content="zh_TW">
    <link rel="stylesheet" href="../assets/pages.css">
    <link rel="stylesheet" href="../assets/eft-supervision.css">
{extra_head}</head>
<body>

    {HEADER}

{body}

    {FOOTER}

</body>
</html>
'''


def pdf_links(n):
    items = []
    for name in PDFS[n]:
        key = next(k for k in PDF_LABEL if k in name)
        items.append(f'<a class="dl" href="pdf/{name}" download>{PDF_LABEL[key]}</a>')
    return ' '.join(items)


def build_text(src, n, title, chapter):
    text = (src / 'build' / 'src' / f'U{n}_學術內容.md').read_text()
    text = re.sub(r'<!--.*?-->', '', text, count=1, flags=re.S)
    body = markdown.markdown(text, extensions=['tables', 'fenced_code', 'attr_list', 'md_in_html', 'toc'])
    nav = []
    if n != '1':
        nav.append(f'<a href="u{int(n) - 1}.html">← 單元{int(n) - 1}</a>')
    nav.append('<a href="index.html">回到系列目錄</a>')
    if n != '6':
        nav.append(f'<a href="u{int(n) + 1}.html">單元{int(n) + 1} →</a>')
    tools = f'''<div class="unit-tools">
            <a class="dl primary" href="u{n}-slides.html">看資訊圖</a> {pdf_links(n)}
        </div>'''
    main = f'''    <main class="article">
        <div class="inner">
        <p class="crumb"><a href="index.html">EFT 督導學習系列</a> ／ 單元{n}（原書{chapter}）</p>
        {tools}
{body}
        <nav class="unit-nav">{" ".join(nav)}</nav>
        </div>
    </main>'''
    return page(f'單元{n} {title}', f'EFT 督導學習系列單元{n}：{title}。', main)


def scope_deck_css(css):
    """把資訊圖的 CSS 限定在 .deck 裡，避免影響網站的頁首頁尾。"""
    # 網頁上沿用網站字型，不依賴排版機器上的字型
    css = css.replace('"WenQuanYi Zen Hei",sans-serif', '"PingFang TC","Heiti TC","Microsoft JhengHei","Noto Sans TC",sans-serif')
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    out = []
    for sel, rules in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
        sel = sel.strip()
        if sel.startswith('@page') or sel == 'html,body':
            continue
        if sel == ':root':
            out.append(f'.deck{{{rules}}}')
        elif sel == 'body':
            out.append(f'.deck{{{rules}}}')
        else:
            out.append(','.join(f'.deck {part.strip()}' for part in sel.split(',')) + f'{{{rules}}}')
    # 抵銷網站共用樣式在卡片與表格上的設定
    out.append('.deck .card{box-shadow:none}.deck th{white-space:normal}.deck .callout{margin-bottom:0}')
    return '\n'.join(out)


def build_slides(src, n, title):
    deck = src / 'build' / 'deck'
    css = scope_deck_css((deck / 'deck.css').read_text())
    slides = '\n'.join(p.read_text() for p in sorted(deck.glob(f'U{n}_slides_*.html')))
    label = f'單元{n}｜{title}'
    head = f'''    <style>
{css}
    </style>
'''
    body = f'''    <div class="deck-page">
        <div class="inner">
        <p class="crumb"><a href="index.html">EFT 督導學習系列</a> ／ 單元{n} 資訊圖</p>
        <h1 class="deck-title">單元{n}｜{html.escape(title)}</h1>
        <div class="unit-tools">
            <a class="dl primary" href="u{n}.html">看文字版</a> {pdf_links(n)}
        </div>
        </div>
        <div class="deck">
{slides}
        </div>
    </div>
    <script>
    // 每張資訊圖原本是 1080×1080，依螢幕寬度等比例縮放；頁碼在載入後補上
    (function () {{
        const slides = [...document.querySelectorAll('.deck .slide')];
        slides.forEach((el, i) => {{
            const f = document.createElement('div');
            f.className = 'foot';
            f.innerHTML = '<span>{html.escape(label)}</span><span>臨床心語 @clinicmind</span><span class="pg">' + (i + 1) + '／' + slides.length + '</span>';
            el.appendChild(f);
        }});
        const fit = () => {{
            const w = Math.min(1080, document.querySelector('.deck').clientWidth);
            slides.forEach((el) => {{ el.style.zoom = w / 1080; }});
        }};
        fit();
        addEventListener('resize', fit);
    }})();
    </script>'''
    return page(f'單元{n} 資訊圖', f'EFT 督導學習系列單元{n}資訊圖：{title}。', body, head)


def build_index():
    cards = []
    for n, title, chapter in UNITS:
        cards.append(f'''                <div class="card unit-card">
                    <p class="muted">單元{n}｜原書{chapter}</p>
                    <h3>{html.escape(title)}</h3>
                    <div class="unit-tools">
                        <a class="dl primary" href="u{n}.html">文字版</a>
                        <a class="dl primary" href="u{n}-slides.html">資訊圖</a>
                        {pdf_links(n)}
                    </div>
                </div>''')
    body = f'''    <div class="page-hero">
        <h1>EFT 督導學習系列</h1>
        <p>給臨床心理與諮商相關科系學生、實習生與臨床工作者的情緒焦點治療（EFT）學習資料，共六個單元，每個單元都有文字版與資訊圖。</p>
    </div>

    <main>
        <section>
            <div class="inner">
                <h2>關於這套教材</h2>
                <ul class="dots">
                    <li>依據 Greenberg, L. S., &amp; Tomescu, L. R. (2017). <i>Supervision Essentials for Emotion-Focused Therapy</i>. American Psychological Association 整理改寫，<strong>不是原書翻譯</strong>，也不能取代閱讀原書與正式訓練。</li>
                    <li>這裡的 EFT 指 Leslie Greenberg 發展的<strong>情緒焦點治療</strong>。它和 Sue Johnson 的伴侶「情緒取向治療」同名但不同，差別見<a href="../eft.html#two">認識 EFT</a>。</li>
                    <li>設計對象是碩士層級的臨床心理學學生，大多以「受督者」的角度學習：辨識情緒類型、標記與任務，並在督導中主動提出自己的困難。</li>
                    <li>文中「原教材指出」是原書的內容，「從臨床實務角度」是本教材的延伸詮釋。所有對話與案例都是綜合改寫的假想情境。</li>
                </ul>
                <p class="muted">如果您是想了解 EFT 能如何幫助自己的一般讀者，建議先看<a href="../eft.html">認識 EFT</a>。</p>
            </div>
        </section>

        <section>
            <div class="inner">
                <h2>六個單元</h2>
                <div class="card-grid">
{chr(10).join(cards)}
                </div>
            </div>
        </section>
    </main>'''
    return page('EFT 督導學習系列', '情緒焦點治療（EFT）督導學習資料，六個單元的文字版、資訊圖與 PDF。', body)


def main():
    src = pathlib.Path(sys.argv[1]).resolve()
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / 'pdf').mkdir(parents=True)
    for n, title, chapter in UNITS:
        (OUT / f'u{n}.html').write_text(build_text(src, n, title, chapter))
        (OUT / f'u{n}-slides.html').write_text(build_slides(src, n, title))
        for name in PDFS[n]:
            shutil.copy(src / 'pdf' / name, OUT / 'pdf' / name)
    (OUT / 'index.html').write_text(build_index())
    print('built', sorted(p.name for p in OUT.iterdir()))


if __name__ == '__main__':
    main()
