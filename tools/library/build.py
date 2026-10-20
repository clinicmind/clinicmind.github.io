"""深度閱讀心理學：由 clinicmind/clinicmind 筆記產生 library/ 下的全部頁面。

用法（在網站 repo 根目錄執行）：
  python3 tools/library/build.py --notes /home/claude/clinicmind [--only SLUG] [--report /tmp/report.txt]

流程：挑分支 → 取出書 → 解析單元 → 寫 HTML → 更新 sitemap.xml、llms.txt → 自動檢查。
任何檢查失敗 → 結束碼 1。只會寫入 library/、sitemap.xml、llms.txt。
"""
import argparse, datetime, html, json, os, pathlib, re, shutil, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE / "vendor"))
import unitfmt  # noqa: E402  (來自 clinicmind/clinicmind pipeline/)
import quiz  # noqa: E402  (本目錄 quiz.py：測驗解析與出題規則)

SITE = "https://clinicmind.github.io"
CONFIG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
BLOCKED = ["教師版", "參考答案", "解答", "answer key"]


# ---------- git ----------
def git(notes, *args, text=True):
    return subprocess.run(["git", "-C", notes, *args], capture_output=True, text=text, check=False).stdout


def branches(notes):
    out = git(notes, "for-each-ref", "refs/remotes/origin", "--format=%(refname:short)")
    return [b for b in out.split() if b.startswith("origin/") and not b.endswith("/HEAD")]


def select_sources(notes, only=None):
    """每本書（資料夾）取最後修改時間最新的分支。回傳 {slug: (branch, date, complete)}。"""
    best = {}
    for b in branches(notes):
        for slug in CONFIG["books"]:
            if only and slug != only:
                continue
            if not git(notes, "ls-tree", b, f"{slug}/book.json").strip():
                continue
            t = git(notes, "log", "-1", "--format=%ct", b, "--", slug).strip()
            if not t:
                continue
            if slug not in best or int(t) > best[slug][0]:
                best[slug] = (int(t), b)
    result = {}
    for slug, (t, b) in best.items():
        bj = json.loads(git(notes, "show", f"{b}:{slug}/book.json") or "{}")
        pdf_ok = bool(git(notes, "ls-tree", b, f"{slug}/pdf/{slug}-academic.pdf").strip())
        complete = pdf_ok or bool(bj.get("complete"))
        result[slug] = (b, datetime.date.fromtimestamp(t).isoformat(), complete, bj)
    return result


def extract(notes, branch, slug, dest):
    p = subprocess.run(["git", "-C", notes, "archive", branch, slug], capture_output=True)
    subprocess.run(["tar", "-x", "-C", dest], input=p.stdout, check=True)
    return pathlib.Path(dest) / slug


# ---------- 文字處理 ----------
def esc(s):
    s = html.escape(str(s))
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return s.replace("\\n", "<br>")


def pages_str(p):
    if isinstance(p, tuple):
        return f"pp. {p[0]}–{p[1]}"
    return f"p. {p}" if p else ""


def first_sentence(s):
    s = re.sub(r"\*", "", str(s))
    return re.split(r"[。！？]", s)[0].strip() + "。"


def strip_practice(text):
    """移除 ## 練習 一節（unitfmt 不認得此節），另回傳練習題行。"""
    lines, out, prac, mode = text.splitlines(), [], [], False
    for l in lines:
        if l.startswith("## "):
            mode = l.strip() == "## 練習"
        if mode:
            if l.startswith("- ") and l.strip() != "## 練習":
                prac.append(l[2:].strip())
            continue
        out.append(l)
    return "\n".join(out) + "\n", prac


def parse_unit(md_path, no, total, tmpdir):
    text, prac = strip_practice(md_path.read_text(encoding="utf-8"))
    tmp = pathlib.Path(tmpdir) / md_path.name
    tmp.write_text(text, encoding="utf-8")
    U = unitfmt.parse(tmp, no, total)
    U["id"] = md_path.stem
    unitfmt.finalize(U)
    U["practice"] = prac
    return U


# ---------- 共用頁首頁尾 ----------
def rewrite_links(fragment):
    def fix(m):
        href = m.group(1)
        if href.startswith(("http", "mailto:", "#", "/", "tel:")):
            return m.group(0)
        if href == "index.html":
            href = "/"
        elif href.startswith("index.html#"):
            href = "/" + href[len("index.html"):]
        else:
            href = "/" + href
        return f'href="{href}"'
    return re.sub(r'href="([^"]+)"', fix, fragment)


def shared_parts():
    lines = (ROOT / "articles.html").read_text(encoding="utf-8").splitlines()
    hs = next(i for i, l in enumerate(lines) if l.strip() == "<header>")
    he = next(i for i, l in enumerate(lines) if l.strip() == "</header>")
    fs = next(i for i, l in enumerate(lines) if l.strip() == "<footer>")
    fe = next(i for i, l in enumerate(lines) if l.strip() == "</footer>")
    header = rewrite_links("\n".join(lines[hs:he + 1]))
    # 主選單：只有「深度閱讀心理學」標示為目前位置
    header = header.replace(' aria-current="page"', "")
    header = re.sub(r'<a href="/library/">深度閱讀心理學</a>', '<a href="/library/" aria-current="page">深度閱讀心理學</a>', header)
    footer = rewrite_links("\n".join(lines[fs:fe + 1]))
    beacon = next(l.strip() for l in lines if "static.cloudflareinsights.com" in l)
    return header, footer, beacon


def page(title, desc, canonical, body, parts, jsonld="", extra_head="", extra_body=""):
    header, footer, beacon = parts
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)}｜臨床心語 ClinicMind</title>
    <meta name="description" content="{html.escape(desc)}">
    <meta property="og:title" content="{html.escape(title)}｜臨床心語 ClinicMind">
    <meta property="og:description" content="{html.escape(desc)}">
    <meta property="og:type" content="article">
    <meta property="og:locale" content="zh_TW">
    <meta property="og:url" content="{canonical}">
    <meta property="og:site_name" content="臨床心語 ClinicMind">
    <meta property="og:image" content="{SITE}/assets/og-image.png">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="theme-color" content="#6B8E88">
    <link rel="stylesheet" href="/assets/pages.css">
    <link rel="stylesheet" href="/assets/site.css">
    <link rel="stylesheet" href="/assets/library.css">
    <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
    <link rel="canonical" href="{canonical}">
    {jsonld}
    {extra_head}
</head>
<body>
    <a class="skip-link" href="#main">跳到主要內容</a>
{header}
    <main id="main" class="lib">
{body}
    </main>
{footer}
    <script src="/assets/finder.js"></script>
    <script src="/assets/site.js"></script>
    <script src="/assets/library.js"></script>
    <script src="/assets/progress.js"></script>
    {extra_body}
    {beacon}
</body>
</html>
"""


def jsonld_article(name, url, unit, book, date, authors):
    obj = {"@context": "https://schema.org", "@type": "Article", "headline": name, "url": url,
           "dateModified": date, "inLanguage": "zh-Hant",
           "author": {"@type": "Person", "name": "臨床心語"},
           "publisher": {"@type": "Organization", "name": "臨床心語 ClinicMind"},
           "isPartOf": {"@type": "WebPage", "name": book["title"], "url": book["url"]},
           "about": {"@type": "Book", "name": book["en"], "author": authors}}
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "首頁", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "深度閱讀心理學", "item": SITE + "/library/"},
        {"@type": "ListItem", "position": 3, "name": book["title"], "item": book["url"]},
        {"@type": "ListItem", "position": 4, "name": name, "item": url}]}
    return ('<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>\n    "
            '<script type="application/ld+json">' + json.dumps(crumbs, ensure_ascii=False) + "</script>")


NOTICE = '<p class="lib-notice">專業書籍學習筆記：給心理健康專業人員與學生，不是診斷或治療建議。本頁引文為中譯，原書版權屬原作者與出版社。</p>'
RIGHTS = ('<div class="lib-rights"><p>本頁為臨床心語的學習筆記，不能取代原書，也不是原書的全文。'
          '如權利人認為內容不妥，請來信 <a href="mailto:clinicmind.inquire@gmail.com">clinicmind.inquire@gmail.com</a>，我們會儘快處理。</p></div>')


def unit_body(U, idx, units, book, date, prac):
    stem = U["id"]
    prev_, next_ = (units[idx - 1] if idx > 0 else None), (units[idx + 1] if idx + 1 < len(units) else None)
    out = [f'<nav class="crumbs" aria-label="麵包屑"><a href="/library/">深度閱讀心理學</a> › '
           f'<a href="/library/{book["slug"]}/">{esc(book["title"])}</a> › 第 {idx + 1} 章</nav>', NOTICE,
           f'<h1>{esc(U["title"])}</h1>',
           f'<p class="lib-meta">{esc(U.get("en", ""))}｜{pages_str(U.get("pages"))}｜{esc(U.get("authors", ""))}</p>',
           f'<p class="lib-credit">臨床心語 整理｜更新於 {date}</p>',
           f'<p class="lib-time">預估閱讀時間約 {U["minutes"]} 分鐘</p>']
    out.append("<h2>學習目標</h2><ol>" + "".join(f"<li>{esc(x)}</li>" for x in U["objectives"]) + "</ol>")
    out.append(f"<h2>摘要</h2><p>{esc(U['summary'])}</p>")
    out.append("<h2 id=\"insights\">關鍵洞見</h2><ul class=\"lib-insights\">" +
               "".join(f"<li><strong>{esc(k)}</strong>：{esc(d)}</li>" for k, d in U["insights"]) + "</ul>")
    if U["quotes"]:
        out.append("<h2 id=\"quotes\">原文重點（中譯）</h2><ul class=\"lib-quotes\">" +
                   "".join(f"<li>{esc(q['zh'])} <span class=\"cite\">（{pages_str(q['p'])}）</span></li>" for q in U["quotes"]) + "</ul>")
    c = U.get("close")
    if c:
        out.append(f"<h2 id=\"close\">精讀</h2><p class=\"lib-quote\">{esc(c['zh'])} <span class=\"cite\">（{pages_str(c['p'])}）</span></p>")
        rows = []
        for term, expl in c["notes"]:
            m = re.match(r"「(.+?)」[：:]?(.*)", expl)
            if m:
                left, right = f"{m.group(1)}（{term}）", m.group(2)
            else:
                left, right = term, expl
            rows.append(f"<tr><th scope=\"row\">{esc(left)}</th><td>{esc(right)}</td></tr>")
        out.append('<table class="lib-table"><tbody>' + "".join(rows) + "</tbody></table>")
    f = U.get("framework") or {}
    if f.get("intro") or f.get("steps"):
        out.append(f"<h2 id=\"framework\">實務推理框架</h2><p>{esc(f.get('intro', ''))}</p>")
        if f.get("svg"):
            out.append(f'<div class="lib-fig">{f["svg"]}</div>')
        if f.get("steps"):
            out.append("<ol>" + "".join(f"<li>{esc(x)}</li>" for x in f["steps"]) + "</ol>")
    if U.get("culture"):
        a, b = U["culture"]
        out.append(f'<div class="lib-box" id="culture"><p><strong>{esc(a)}</strong></p><p>{esc(b)}</p></div>')
    if prac:
        out.append("<h2>練習</h2><ol>" + "".join(f"<li>{esc(x)}</li>" for x in prac) + "</ol>")
    out.append(f'<p class="lib-limits"><strong>限制：</strong>{esc(U.get("limits", ""))}</p>')
    rid = f"recall-{U['id']}"
    out.append(f'<section class="lib-recall" aria-labelledby="{rid}-h"><h2 id="{rid}-h">回想練習</h2>'
               '<p>不往上看，寫下本章的兩個洞見。這段文字只留在此頁，不會保存或送出。</p>'
               f'<label for="{rid}" class="sr-only">寫下本章的兩個洞見</label>'
               f'<textarea id="{rid}" rows="5" class="lib-recall-box"></textarea>'
               '<details><summary>展開本章洞見對照</summary><ul>' +
               "".join(f"<li><strong>{esc(k)}</strong>：{esc(d)}</li>" for k, d in U["insights"]) +
               "</ul></details></section>")
    out.append(f'<p class="lib-done-row"><button type="button" class="btn" data-read-btn data-book="{book["slug"]}" '
               f'data-unit="{U["id"]}" aria-pressed="false">我讀完了</button></p>')
    out.append('<nav class="lib-pager" aria-label="章節導覽">' +
               (f'<a href="/library/{book["slug"]}/{prev_["id"]}.html">← 上一章</a>' if prev_ else "<span></span>") +
               f'<a href="/library/{book["slug"]}/">回書頁</a>' +
               (f'<a href="/library/{book["slug"]}/{next_["id"]}.html">下一章 →</a>' if next_ else
                (f'<a href="/library/{book["slug"]}/quiz.html">全書測驗 →</a>' if book.get("quiz") else "<span></span>")) +
               "</nav>")
    out.append(RIGHTS)
    return "\n".join(out)


def book_body(book, units, date):
    out = [f'<nav class="crumbs" aria-label="麵包屑"><a href="/library/">深度閱讀心理學</a> › {esc(book["title"])}</nav>', NOTICE,
           f'<h1>{esc(book["title"])}</h1>',
           f'<p class="lib-meta">{esc(book["en"])}｜{esc(book["authors"])}</p>',
           f'<p class="lib-credit">臨床心語 整理｜更新於 {date}</p>',
           f'<p>{esc(book["intro"])}</p>',
           '<section class="lib-start" aria-labelledby="start-h"><h2 id="start-h">開始前</h2><ul>'
           f'<li>共 {len(units)} 章，預估閱讀約 {book["minutes"]} 分鐘（全書中文字數 ÷ 300）。</li>'
           '<li>建議每次讀 1 到 2 章，章末做回想練習，再按「我讀完了」。</li>'
           '<li>讀完後可做 15 題測驗。答錯會有提醒，可以重答；全部答對才能取得閱讀完成證明。</li>'
           '<li>進度只存在您的瀏覽器，網站不會收到。</li></ul>'
           f'<p><a class="btn" href="/library/{book["slug"]}/{units[0]["id"]}.html">開始第 1 章</a> '
           '<a href="/library/guide.html">閱讀指引</a></p></section>' if units else "",
           "<h2>全書三個重點</h2><ol>" + "".join(f"<li>{esc(x)}</li>" for x in book["summary"]) + "</ol>",
           "<h2>章節地圖</h2>"
           f'<div class="lib-progress"><progress id="book-progress" value="0" max="{len(units) or 1}"></progress>'
           '<p id="book-progress-text" class="lib-meta">已標記讀完 0 章</p></div>'
           f'<ol class="lib-map" data-book-map="{book["slug"]}">' +
           "".join(f'<li data-unit="{u["id"]}"><a href="/library/{book["slug"]}/{u["id"]}.html">{esc(u["title"])}</a>'
                   f'<span class="cite">（{pages_str(u.get("pages"))}）</span><br>{esc(first_sentence(u["summary"]))}</li>'
                   for u in units) + "</ol>",
           '<section class="lib-quiz-entry" aria-labelledby="quiz-h"><h2 id="quiz-h">全書測驗</h2>' +
           (f'<p>15 題，四選一。讀完全部章節後再做，全部答對即可取得閱讀完成證明。</p>'
            f'<p id="book-quiz-tip" hidden>您已標記讀完全部章節，可以開始測驗。</p>'
            f'<p><a class="btn" href="/library/{book["slug"]}/quiz.html">開始測驗</a></p>' if book.get("quiz") else
            '<p>測驗準備中。</p>') + '</section>',
           f'<div class="lib-box"><h2>一個行動</h2><p>{esc(book["action"])}</p></div>',
           RIGHTS]
    return "\n".join(out)


def library_body(cards, other_block):
    out = ['<nav class="crumbs" aria-label="麵包屑"><a href="/">首頁</a> › 深度閱讀心理學</nav>',
           '<h1>深度閱讀心理學</h1>',
           '<p class="lib-intro">把心理學專業書籍整理成中文學習筆記，每章含學習目標、摘要、洞見、原文重點（中譯）、精讀、實務推理框架與華人情境。主要給心理健康專業人員與學生；一般讀者可看<a href="/articles.html">其他心理知識</a>。</p>',
           NOTICE,
           '<div class="lib-box lib-guide-tip"><p><strong>閱讀前請先看</strong>：每章先看學習目標，再讀摘要與精讀，章末做回想練習。'
           '每本書讀完後可做 15 題測驗，全部答對即可取得閱讀完成證明。<a href="/library/guide.html">閱讀指引</a></p></div>',
           '<div class="finder lib-finder" data-finder data-items="main .lib-ch a" data-groups="main .lib-cat" hidden>'
           '<label for="lib-q">搜尋書名或章名</label><input id="lib-q" type="search" maxlength="40" autocomplete="off" placeholder="例如：創傷、分心、依附">'
           '<select data-topic class="sr-only" aria-hidden="true" tabindex="-1"></select>'
           '<p class="finder-count" data-count role="status" aria-live="polite"></p>'
           '<div class="finder-empty" data-empty hidden><p>沒有找到相符的內容。</p><button type="button" data-clear>清除搜尋</button></div></div>']
    for cat_name, items in cards:
        out.append(f'<div class="lib-cat" id="cat-{items[0]["catid"]}"><h2>{esc(cat_name)}</h2><div class="lib-grid">')
        for b in items:
            out.append(f'<article class="lib-card"><h3><a href="/library/{b["slug"]}/">{esc(b["title"])}</a></h3>'
                       f'<p class="lib-meta">{esc(b["en"])}｜{b["n"]} 章｜更新於 {b["date"]}</p>'
                       f'<p>{esc(b["short_intro"])}</p>'
                       f'<details class="lib-ch-wrap"><summary>章節清單</summary><ol class="lib-ch">' +
                       "".join(f'<li><a href="/library/{b["slug"]}/{u["id"]}.html">{esc(u["title"])}</a></li>' for u in b["units"]) +
                       "</ol></details></article>")
        out.append("</div></div>")
    out.append(other_block)
    out.append(RIGHTS)
    return "\n".join(out)


CERT_HEAD = '<link rel="stylesheet" href="/assets/certificate.css">'
QUIZ_JS = ('<script src="/assets/certificate.js"></script>\n    <script src="/assets/quiz.js"></script>')


def quiz_body(book, qd):
    blob = json.dumps(qd, ensure_ascii=False).replace("</", "<\\/")
    return "\n".join([
        f'<nav class="crumbs" aria-label="麵包屑"><a href="/library/">深度閱讀心理學</a> › '
        f'<a href="/library/{book["slug"]}/">{esc(book["title"])}</a> › 全書測驗</nav>',
        f'<h1>全書測驗：{esc(book["title"])}</h1>',
        f'<p class="lib-meta">{esc(book["en"])}｜15 題，四選一</p>',
        '<p>答錯會有提醒，可以重答。15 題全部答對後，可以輸入名字取得閱讀完成證明。題目與選項每次順序都不同。'
        '作答紀錄只存在您的瀏覽器。</p>',
        '<div id="quiz"><p id="quiz-live" class="sr-only" aria-live="polite"></p>',
        '<form id="quiz-form" novalidate><div id="quiz-list"></div>'
        '<p><button type="submit" class="btn">交卷</button></p></form>',
        '<section id="quiz-result" hidden></section>',
        '<p><button type="button" id="cert-start" class="btn" hidden>輸入名字，取得閱讀完成證明</button></p>',
        '<form id="cert-form" hidden><label for="cert-name">名字（會印在證明上）</label> '
        '<input id="cert-name" type="text" maxlength="40" autocomplete="name" required> '
        '<button type="submit" class="btn">產生證明</button></form>',
        '<div id="cert-out" hidden></div></div>',
        f'<script type="application/json" id="quiz-data">{blob}</script>',
        RIGHTS,
    ])


def guide_body():
    steps = ["先看「學習目標」，問自己：我現在答得出幾項？",
             "讀「摘要」與「關鍵洞見」。",
             "讀「精讀」，停下來想一想作者為什麼這樣用詞。",
             "用「實務推理框架」想一個您遇過的情境（不寫入任何個案資料）。",
             "讀「華人情境」，想一想它在您的工作脈絡裡是否成立。",
             "不看內容，做章末「回想練習」，再按「我讀完了」。"]
    return "\n".join([
        '<nav class="crumbs" aria-label="麵包屑"><a href="/library/">深度閱讀心理學</a> › 閱讀指引</nav>',
        '<h1>閱讀指引</h1>',
        '<p class="lib-intro">這裡的每一章都是學習筆記，不是速讀摘要。慢慢讀、停下來想，記得會比較久。'
        '下面說明每章怎麼讀、怎麼做測驗，以及閱讀完成證明的規則。</p>',
        '<h2>每章怎麼讀</h2><ol>' + "".join(f"<li>{x}</li>" for x in steps) + "</ol>",
        '<h2>讀完一本書之後：15 題測驗</h2>',
        '<ul><li>每本書 15 題，四選一。</li>'
        '<li>答錯會有提醒，並附「回到相關段落」的連結。正確答案不會顯示，請您回到章節再想一次。</li>'
        '<li>答對的題目會保留，您只需重答錯的題目。</li>'
        '<li>15 題全部答對後，才會顯示每題解說（附原書頁碼），並可輸入名字取得證明。</li></ul>',
        '<h2>閱讀完成證明</h2>',
        '<ul><li>證明在您的瀏覽器裡產生。名字不會傳到網站，也不會被記錄。</li>'
        '<li>可以用瀏覽器「列印／存成 PDF」（A4 橫式），也可以下載 1080×1350 的分享圖。</li>'
        '<li>證明上的驗證碼只用來核對證明上的資料是否一致，不能防偽。</li>'
        '<li>證明上寫明：「' + STATEMENT_TEXT + '」</li></ul>',
        '<h2>私隱</h2>',
        '<ul><li>閱讀進度、測驗紀錄與回想練習的文字，只存在您的瀏覽器。</li>'
        '<li>網站沒有後台，不收集個人資料，也無法統計誰完成了哪一本書。</li>'
        '<li>清除瀏覽器資料，進度會一併消失。</li></ul>',
        '<h2>需要知道的事</h2>',
        '<ul><li>學習筆記用來協助理解，不能取代原書。</li>'
        '<li>閱讀完成證明是自我激勵的紀念，不是學分、執照或專業認證，也不能當作任何正式訓練時數。</li></ul>',
        RIGHTS,
    ])


STATEMENT_TEXT = "本證明表示持有人已讀完本書的學習筆記，並通過 15 題理解測驗。本證明不是學分、執照或專業認證。"


# ---------- 主流程 ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--notes", required=True)
    ap.add_argument("--only")
    ap.add_argument("--report", default="/tmp/library-report.txt")
    a = ap.parse_args()
    notes = os.path.abspath(a.notes)
    srcs = select_sources(notes, a.only)
    parts = shared_parts()
    lib = ROOT / "library"
    report, problems, cards, all_urls = [], [], {}, []
    tmp = tempfile.mkdtemp()

    for slug in CONFIG["books"]:
        if slug not in srcs:
            if not a.only:
                report.append(f"略過 {slug}：找不到分支中的 book.json")
            continue
        branch, bdate, complete, bj = srcs[slug]
        if not complete:
            report.append(f"略過 {slug}：未完成（分支 {branch}）")
            continue
        cfg = CONFIG["books"][slug]
        d = extract(notes, branch, slug, tmp)
        md_files = sorted((d / "units").glob("*.md"))
        units = []
        for i, f in enumerate(md_files):
            udate = git(notes, "log", "-1", "--format=%cs", branch, "--", f"{slug}/units/{f.name}").strip() or bdate
            U = parse_unit(f, i + 1, len(md_files), tmp)
            U["date"] = udate
            units.append(U)
        for U in units:
            chars = len(re.findall(r"[\u3400-\u9fff]", json.dumps(U, ensure_ascii=False)))
            U["minutes"] = max(1, round(chars / 300))
            U["chars"] = chars
        book = {"slug": slug, "title": cfg.get("title", bj.get("title", slug)), "en": bj.get("name", ""),
                "authors": bj.get("authors", ""), "intro": bj.get("intro", ""), "summary": bj.get("summary", []),
                "action": bj.get("action", ""), "url": f"{SITE}/library/{slug}/", "short_intro": bj.get("short", "")}
        book_date = max(u["date"] for u in units) if units else bdate
        book["minutes"] = max(10, round(sum(u["chars"] for u in units) / 300 / 10) * 10)
        bdir = lib / slug
        bdir.mkdir(parents=True, exist_ok=True)
        # 全書測驗：有 quiz.md 且通過規則才產生；不合格只在報告列出，書照樣上線
        book["quiz"] = False
        qd = None
        qfile = pathlib.Path(d) / "quiz.md"
        units_text = {f.stem: f.read_text(encoding="utf-8") for f in md_files}
        if qfile.exists():
            qs, qprobs = quiz.validate(qfile.read_text(encoding="utf-8"), units_text)
            if any(U["id"] != f.stem for U, f in zip(units, md_files)):
                qprobs.append("單元 id 與檔名不一致，測驗連結可能失效")
            if qprobs:
                report.append(f"測驗未產生 {slug}：" + "；".join(qprobs))
            else:
                qd = quiz.public_data(slug, book["title"], book["en"], len(units), qs)
                book["quiz"] = True
        if not qd and (bdir / "quiz.html").exists():
            (bdir / "quiz.html").unlink()
        (bdir / "index.html").write_text(page(book["title"], book["intro"][:110], book["url"],
                                              book_body(book, units, book_date), parts), encoding="utf-8")
        if qd:
            qurl = f"{SITE}/library/{slug}/quiz.html"
            (bdir / "quiz.html").write_text(
                page(f"{book['title']}：全書測驗", f"{book['title']} 15 題四選一測驗，全部答對即可取得閱讀完成證明。",
                     qurl, quiz_body(book, qd), parts, extra_head=CERT_HEAD, extra_body=QUIZ_JS),
                encoding="utf-8")
            all_urls.append((qurl, book_date))
        all_urls.append((book["url"], book_date))
        for i, U in enumerate(units):
            url = f"{SITE}/library/{slug}/{U['id']}.html"
            desc = first_sentence(U["summary"])[:110]
            body = unit_body(U, i, units, book, U["date"], U["practice"])
            ld = jsonld_article(U["title"], url, U, book, U["date"], book["authors"])
            (bdir / f"{U['id']}.html").write_text(page(U["title"], desc, url, body, parts, ld), encoding="utf-8")
            all_urls.append((url, U["date"]))
        cat = cfg.get("category", "new")
        catname = next((c["name"] for c in CONFIG["categories"] if c["id"] == cat), "新加入")
        book["catid"] = cat
        book["n"] = len(units)
        book["date"] = book_date
        book["units"] = units
        book["order"] = cfg.get("order", 99)
        book["catname"] = catname
        cards[(cat, slug)] = book
        report.append(f"{slug}\t分支 {branch}\t{book_date}\t{len(units)} 章")

    # 本區首頁
    grouped = []
    for c in CONFIG["categories"]:
        items = sorted([v for k, v in cards.items() if isinstance(v, dict) and v["catid"] == c["id"]], key=lambda b: b["order"])
        if items:
            grouped.append((c["name"], items))
    other = ('<div class="lib-cat lib-other"><h2>其他心理知識</h2><p>安放系列、創傷、關係、成癮、照顧自己等衛教文章與專欄，'
             '依問題分類。</p><p><a href="/articles.html">前往其他心理知識</a></p></div>')
    (lib).mkdir(exist_ok=True)
    home_desc = "把心理學專業書籍整理成中文學習筆記，依主題分類，附章節地圖與華人情境。主要給心理健康專業人員與學生。"
    home_url = f"{SITE}/library/"
    (lib / "index.html").write_text(page("深度閱讀心理學", home_desc, home_url,
                                         library_body(grouped, other), parts), encoding="utf-8")
    all_urls.insert(0, (home_url, datetime.date.today().isoformat()))
    guide_url = f"{SITE}/library/guide.html"
    (lib / "guide.html").write_text(page("閱讀指引", "深度閱讀心理學的閱讀方法、15 題測驗與閱讀完成證明規則。",
                                         guide_url, guide_body(), parts), encoding="utf-8")
    all_urls.insert(1, (guide_url, datetime.date.today().isoformat()))
    (lib / ".generated").write_text("此資料夾由 tools/library/build.py 產生，請勿手改。\n", encoding="utf-8")

    # sitemap（只換 /library/ 項目）
    sm = ROOT / "sitemap.xml"
    s = sm.read_text(encoding="utf-8")
    s = re.sub(r"\s*<url><loc>https://clinicmind\.github\.io/library/[^<]*</loc>.*?</url>", "", s, flags=re.S)
    add = "".join(f"\n  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in all_urls)
    sm.write_text(s.replace("</urlset>", add + "\n</urlset>"), encoding="utf-8")

    # llms.txt（只換「深度閱讀心理學」段）
    lt = ROOT / "llms.txt"
    text = lt.read_text(encoding="utf-8")
    lines = ["## 深度閱讀心理學", f"- [深度閱讀心理學]({home_url})：專業書籍學習筆記，依主題分類",
             f"- [閱讀指引]({guide_url})：每章怎麼讀、15 題測驗與閱讀完成證明的規則"]
    for name, items in grouped:
        for b in items:
            lines.append(f"- [{b['title']}]({b['url']})：{b['short_intro'] or '學習筆記'}")
    block = "\n".join(lines) + "\n\n"
    text = re.sub(r"## 深度閱讀心理學\n.*?(?=\n## )", "", text, flags=re.S)
    text = text.replace("## 心理衛教", block + "## 心理衛教", 1) if "## 心理衛教" in text else text + "\n" + block
    lt.write_text(text, encoding="utf-8")

    # 自動檢查
    problems += check(lib, all_urls)
    report.append(f"檢查：{'全部通過' if not problems else '失敗 ' + str(len(problems)) + ' 項'}")
    report += problems
    pathlib.Path(a.report).write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))
    shutil.rmtree(tmp, ignore_errors=True)
    return 1 if problems else 0


def check(lib, urls):
    probs = []
    for p in lib.rglob("*.html"):
        t = p.read_text(encoding="utf-8")
        rel = p.relative_to(ROOT)
        for need, label in [(r"<title>", "title"), (r'name="description"', "description"), (r'rel="canonical"', "canonical")]:
            if not re.search(need, t):
                probs.append(f"{rel} 缺 {label}")
        for href in re.findall(r'href="(/[^"#?]*)', t):
            target = ROOT / href.lstrip("/")
            if href.endswith("/"):
                target = target / "index.html"
            if not target.exists() and not href.startswith("/library/.generated"):
                probs.append(f"{rel} 壞連結 {href}")
        visible = re.sub(r'<p class="lib-meta">.*?</p>|<script.*?</script>|<style.*?</style>|<[^>]+>|https?://\S+', " ", t, flags=re.S)
        if re.search(r"(?:[A-Za-z]+[ ,.;:'\-]+){11,}[A-Za-z]+", visible):
            probs.append(f"{rel} 含連續 12 個以上英文字（可能是原文）")
        if p.name == "quiz.html" and re.search(r'"(correct|answer)"', t):
            probs.append(f"{rel} 測驗資料含明文答案欄位")
        if ".pdf" in t:
            probs.append(f"{rel} 含 PDF 連結")
        for w in BLOCKED:
            if w in visible:
                probs.append(f"{rel} 含禁用字「{w}」")
    return probs


if __name__ == "__main__":
    sys.exit(main())
