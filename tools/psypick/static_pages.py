#!/usr/bin/env python3
"""PsyPick 靜態頁（C-3）、sitemap（C-4）與 RSS（C-4）產生器。

由 build.py 呼叫，不用單獨跑。產生：
  psypick/p/<slug>.html     每則在架 case（include != false，即 index.json 內每則）
  psypick/fig/<slug>.html   figures.json 每位人物
  psypick/feed.xml          RSS 2.0，最新 50 則（按 first_seen_at）
  sitemap.xml（根目錄）     保留非 PsyPick 靜態頁的網址，加入全部靜態頁

p/、fig/、feed.xml 是建置產物，不入 repo（.gitignore），由 CI 部署時產生。
根目錄 sitemap.xml 是已追蹤檔，只在 CI（GITHUB_ACTIONS=true）或 build.py
加 --sitemap 時改寫，避免例行上架誤改。

只用 Python 標準函式庫。
"""

import json
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape

SITE = "https://clinicmind.github.io"
PP = SITE + "/psypick/"
DEFAULT_OG = SITE + "/assets/og-image.png"
ADSENSE = ('<script async src="https://pagead2.googlesyndication.com/pagead/js/'
           'adsbygoogle.js?client=ca-pub-4718403536098373" '
           'crossorigin="anonymous"></script>')
SLUG_OK = re.compile(r"^[a-z0-9][a-z0-9-]*$")
FEED_N = 50
SM_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
GENERATED_PREFIXES = (PP + "p/", PP + "fig/")

KIND_ZH = {"research": "研究發現", "practice": "臨床實務", "product": "產品動態",
           "incident": "事件與爭議", "training": "培訓課程"}

# 港澳／台灣用詞並列：條目內文出現任一寫法，就在頁底列出對照（不改原文）
TERM_GROUPS = [
    [("臨床心理學家", "港澳"), ("臨床心理師", "台灣")],
    [("輔導員", "港澳"), ("諮商心理師", "台灣")],
    [("ADHD", ""), ("專注力不足／過度活躍症", "港澳"), ("過動症", "台灣")],
    [("親職教育", ""), ("親子教養", "")],
    [("精神科醫生", "港澳"), ("精神科醫師", "台灣")],
    [("抑鬱", "港澳"), ("憂鬱", "台灣")],
    [("自閉症譜系障礙", "港澳"), ("自閉症類群障礙", "台灣")],
]
TERM_ALIASES = {"過度活躍症": 2, "過動": 2, "諮商師": 1,
                "親職": 3, "教養": 3, "抑鬱症": 5, "憂鬱症": 5,
                "自閉症": 6}


def h(s):
    return escape(str(s if s is not None else ""), quote=True)


def day(s):
    s = str(s or "")
    return s[:10] if re.match(r"^\d{4}-\d{2}-\d{2}", s) else ""


def clip(s, n):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def safe_url(u):
    return isinstance(u, str) and re.match(r"^https?://", u.strip()) is not None


def jsonld(obj):
    txt = json.dumps(obj, ensure_ascii=False, indent=1)
    return ('<script type="application/ld+json">'
            + txt.replace("</", "<\\/") + "</script>")


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def term_note(text):
    hit = set()
    for gi, group in enumerate(TERM_GROUPS):
        if any(t in text for t, _ in group):
            hit.add(gi)
    for alias, gi in TERM_ALIASES.items():
        if alias in text:
            hit.add(gi)
    if not hit:
        return ""
    parts = []
    for gi in sorted(hit):
        parts.append("／".join(t + ("（%s）" % r if r else "")
                              for t, r in TERM_GROUPS[gi]))
    return ('<p class="ref">地區用詞對照：' + h("；".join(parts)) + "</p>")


# ---------------------------------------------------------------- 版面
def page(*, title, desc, canonical, og_image, og_type, body, ld, up):
    """up = 回到 psypick/ 的相對路徑前綴（例如 "../"）。"""
    return """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="知心選 PsyPick">
<meta property="og:locale" content="zh_HK">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{og_image}">
<meta name="theme-color" content="#F7F5F0">
<link rel="icon" type="image/svg+xml" href="{up}brand/favicon.svg">
<link rel="alternate" type="application/rss+xml" title="知心選 PsyPick" href="{up}feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=Noto+Serif+TC:wght@500;600&display=swap">
<link rel="stylesheet" href="{up}style.css">
{adsense}
{ld}
</head>
<body>
<div class="parent-bar" style="background:#244A42;color:#F7F5F0;padding:6px 16px;font-size:14px;"><a href="{up}../" style="color:#F7F5F0;text-decoration:none;">← 臨床心語 ClinicMind</a><span style="float:right;">知心選 PsyPick 是臨床心語的資訊整理站</span></div>
<header class="site-header">
  <div class="row">
    <a class="brand" href="{up}"><img class="brand-mark mark-light" src="{up}brand/mark.svg" alt="" width="30" height="30"><img class="brand-mark mark-dark" src="{up}brand/mark-dark.svg" alt="" width="30" height="30"><span class="wordmark">知心選 PsyPick</span></a>
    <div class="header-right">
      <nav class="header-nav" style="display:flex">
        <a href="{up}">首頁</a>
        <a href="{up}#/training">進修</a>
        <a href="{up}#/figures">動向</a>
      </nav>
    </div>
  </div>
</header>
<div class="container"><main id="app">
{body}
</main>
<footer class="site-footer">
  <span class="footer-brand">臨床心語 ClinicMind</span>
  <span>知心選 PsyPick：AI × 心理學的案例訊號站</span>
  <span>內容版權屬原作者；本站提供導讀與專業註解，不構成醫療或治療建議。</span>
  <span><a href="{up}privacy.html">私隱政策 Privacy Policy</a></span>
  <span><a href="{up}feed.xml">RSS</a></span>
</footer></div>
</body>
</html>
""".format(title=h(title), desc=h(desc), canonical=h(canonical),
           og_type=h(og_type), og_image=h(og_image), up=up, adsense=ADSENSE,
           ld=ld, body=body)


# ---------------------------------------------------------------- case 頁
def related_for(case, entry, entries, live):
    out, seen = [], {case.get("slug")}
    for r in case.get("related") or []:
        s = r.get("slug") if isinstance(r, dict) else r
        if s in live and s not in seen:
            out.append(live[s])
            seen.add(s)
    if len(out) < 5:
        tags = set(case.get("tags") or [])
        cands = []
        for e in entries:
            if e["slug"] in seen or e.get("category") != case.get("category"):
                continue
            overlap = len(tags & set(e.get("tags") or []))
            if overlap:
                cands.append((overlap, e.get("first_seen_at") or "", e))
        cands.sort(key=lambda x: (x[0], x[1]), reverse=True)
        for _, _, e in cands[: 5 - len(out)]:
            out.append(e)
    return out[:5]


def case_ld(case, entry, url, og_image):
    p0 = (case.get("posts") or [{}])[0]
    published = day(p0.get("posted_at")) or day(entry.get("date")) \
        or day(case.get("first_seen_at"))
    base = {
        "@context": "https://schema.org",
        "name": case.get("title_zh"),
        "alternateName": case.get("title_en"),
        "description": clip(case.get("summary_zh"), 300),
        "url": url,
        "inLanguage": "zh-Hant",
        "image": og_image,
    }
    tr = case.get("training") or {}
    if case.get("kind") == "training" and tr:
        base["@type"] = "Event"
        ev = str(tr.get("event_date") or "")
        if re.match(r"^\d{4}-\d{2}-\d{2}$", ev):
            base["startDate"] = ev
        fmt = tr.get("format") or ""
        base["eventAttendanceMode"] = (
            "https://schema.org/OnlineEventAttendanceMode"
            if "線上" in fmt or "online" in fmt.lower()
            else "https://schema.org/MixedEventAttendanceMode")
        base["eventStatus"] = "https://schema.org/EventScheduled"
        loc = tr.get("signup_url") if safe_url(tr.get("signup_url")) \
            else p0.get("url")
        base["location"] = {"@type": "VirtualLocation", "url": loc}
        if tr.get("provider"):
            base["organizer"] = {"@type": "Organization",
                                 "name": tr["provider"]}
        if tr.get("price_tier") == "免費":
            base["isAccessibleForFree"] = True
        return base
    base["@type"] = "ScholarlyArticle" if case.get("kind") == "research" \
        else "Article"
    base["headline"] = clip(case.get("title_zh"), 110)
    if published:
        base["datePublished"] = published
    base["dateModified"] = day(case.get("first_seen_at")) or published
    if safe_url(p0.get("url")):
        base["isBasedOn"] = p0["url"]
    if p0.get("author_name"):
        base["sourceOrganization"] = {"@type": "Organization",
                                      "name": p0["author_name"]}
    base["publisher"] = {"@type": "Organization", "name": "臨床心語 ClinicMind",
                         "url": SITE + "/"}
    base["keywords"] = ", ".join(case.get("tags") or [])
    return base


def case_page(case, entry, entries, live, levels):
    slug = case["slug"]
    url = PP + "p/" + slug + ".html"
    poster = case.get("poster") or {}
    og_image = (PP + poster["src"]) if poster.get("src") else DEFAULT_OG
    tr = case.get("training") or {}
    is_training = case.get("kind") == "training" and tr
    d = day(entry.get("date")) or day(case.get("first_seen_at"))

    meta = ['<span style="font-weight:600">%s</span>' % h(case.get("category"))]
    if KIND_ZH.get(case.get("kind")):
        meta.append('<span class="badge">%s</span>' % h(KIND_ZH[case["kind"]]))
    if d:
        meta.append('<time datetime="%s">%s</time>' % (h(d), h(d)))
    if entry.get("tier") == "archive":
        meta.append('<span class="badge badge-muted">已結束／歸檔</span>')
    elif case.get("verify_needed"):
        meta.append('<span class="badge badge-warn">待查證</span>')
    else:
        meta.append('<span class="badge badge-ok">已核對來源</span>')

    b = []
    b.append('<nav class="ref" aria-label="麵包屑"><a href="../">知心選</a> › '
             '%s</nav>' % h(case.get("category")))
    b.append('<article class="detail-page"><div class="detail-layout"><div>')
    b.append('<h1 class="detail-title">%s</h1>' % h(case.get("title_zh")))
    if case.get("title_en"):
        b.append('<p class="conf-en" lang="en">%s</p>' % h(case["title_en"]))
    b.append('<div class="card-meta">%s</div>' % "".join(meta))
    if case.get("verify_needed") and case.get("verify_reason"):
        b.append('<p class="badge badge-warn" style="display:inline-block;'
                 'margin-top:12px">待查證：%s</p>' % h(case["verify_reason"]))
    b.append('<p class="detail-summary">%s</p>' % h(case.get("summary_zh")))
    brief = [x for x in case.get("brief_zh") or [] if x]
    if brief:
        b.append('<h2 class="section-title">重點</h2><ul>%s</ul>'
                 % "".join("<li>%s</li>" % h(x) for x in brief))
    if case.get("evidence_quote"):
        p0 = (case.get("posts") or [{}])[0]
        cite = (' cite="%s"' % h(p0["url"])) if safe_url(p0.get("url")) else ""
        b.append('<h2 class="section-title">原文引述</h2>'
                 '<blockquote class="conf-note"%s>「%s」</blockquote>'
                 '<p class="ref">以上為來源原文逐字摘錄，未經翻譯。</p>'
                 % (cite, h(case["evidence_quote"])))
    if is_training:
        rows = [("主辦", tr.get("provider")), ("形式", tr.get("format")),
                ("費用", tr.get("price") or tr.get("price_tier")),
                ("學分", tr.get("ce_credits")), ("語言", tr.get("language")),
                ("日期", tr.get("event_date")), ("截止", tr.get("deadline")),
                ("程度", tr.get("audience_level")), ("主題", tr.get("topic"))]
        b.append('<h2 class="section-title">培訓資料</h2><div class="panel">'
                 '<dl class="kv">%s</dl>' % "".join(
                     "<dt>%s</dt><dd>%s</dd>" % (h(k), h(v))
                     for k, v in rows if v))
        if safe_url(tr.get("signup_url")):
            b.append('<p><a href="%s" target="_blank" rel="noopener noreferrer">'
                     '前往報名頁 ↗</a></p>' % h(tr["signup_url"]))
        b.append("</div>")
    b.append('<h2 class="section-title">來源</h2>')
    for p in case.get("posts") or []:
        who = " · ".join(x for x in [p.get("author_name"), day(p.get("posted_at"))]
                         if x)
        b.append('<div class="source-post"><div class="handle">%s</div>' % h(who))
        if p.get("title"):
            b.append("<b>%s</b>" % h(p["title"]))
        if p.get("content"):
            b.append("<p>%s</p>" % h(p["content"]))
        if safe_url(p.get("url")):
            b.append('<a href="%s" target="_blank" rel="noopener noreferrer">'
                     '開啟原文 ↗</a>' % h(p["url"]))
        b.append("</div>")
    if case.get("summary_en"):
        b.append('<h2 class="section-title">English summary</h2>'
                 '<p lang="en">%s</p>' % h(case["summary_en"]))
    b.append('<p style="margin-top:18px"><a class="chip" href="../#/case/%s">'
             '打開互動版（收藏、搜尋、篩選）→</a></p>' % h(slug))
    b.append("</div><aside>")
    if not is_training and case.get("evidence_level") is not None:
        lv = levels.get(str(case["evidence_level"]), {})
        b.append('<div class="panel"><h2 class="section-title">證據強度</h2>'
                 '<dl class="kv"><dt>等級</dt><dd>E%s %s%s</dd>%s</dl></div>' % (
                     h(case["evidence_level"]), h(lv.get("zh", "")),
                     ('<div class="ref">%s</div>' % h(case["evidence_note"]))
                     if case.get("evidence_note") else "",
                     ("<dt>對象</dt><dd>%s</dd>" % h("、".join(case["population"])))
                     if case.get("population") else ""))
    for f in case.get("ethics_flags") or []:
        if isinstance(f, dict):
            b.append('<div class="panel"><div class="flag"><b>%s</b><div>%s</div>'
                     '</div></div>' % (h(f.get("flag")), h(f.get("note"))))
    if case.get("supervision_questions"):
        b.append('<div class="panel"><h2 class="section-title">督導思考問題</h2>'
                 '<ol>%s</ol></div>' % "".join(
                     "<li>%s</li>" % h(q) for q in case["supervision_questions"]))
    if case.get("caution"):
        b.append('<div class="panel"><h2 class="section-title">注意事項</h2>'
                 '<p>%s</p></div>' % h(case["caution"]))
    if poster.get("src"):
        b.append('<img class="detail-hero" src="../%s" alt="%s" loading="lazy">'
                 % (h(poster["src"]), h(poster.get("alt") or "")))
    b.append("</aside></div>")
    rel = related_for(case, entry, entries, live)
    if rel:
        b.append('<h2 class="section-title">相關條目</h2><ul>%s</ul>' % "".join(
            '<li><a href="%s.html">%s</a></li>' % (h(e["slug"]), h(e.get("title_zh")))
            for e in rel))
    if case.get("tags"):
        b.append('<p class="card-meta">%s</p>' % "".join(
            '<span class="badge">%s</span>' % h(t) for t in case["tags"]))
    text = " ".join([case.get("title_zh") or "", case.get("summary_zh") or "",
                     " ".join(brief), " ".join(case.get("tags") or []),
                     case.get("title_en") or ""])
    b.append(term_note(text))
    b.append("</article>")

    title = "%s｜知心選 PsyPick" % (case.get("title_zh") or slug)
    return page(title=title, desc=clip(case.get("summary_zh"), 150),
                canonical=url, og_image=og_image, og_type="article",
                body="\n".join(x for x in b if x),
                ld=jsonld(case_ld(case, entry, url, og_image)), up="../")


# ---------------------------------------------------------------- 人物頁
def fig_name(p):
    zh, en = p.get("name_zh"), p.get("name_en") or p.get("slug")
    return "%s（%s）" % (en, zh) if zh and zh != en else en


def fig_page(p, updates):
    slug = p["slug"]
    url = PP + "fig/" + slug + ".html"
    name = fig_name(p)
    accs = [a for a in p.get("accounts") or [] if safe_url(a.get("url"))]
    b = ['<nav class="ref" aria-label="麵包屑"><a href="../">知心選</a> › '
         '<a href="../#/figures">人物動向</a></nav>',
         '<article class="detail-page">',
         '<h1 class="detail-title">%s</h1>' % h(name),
         '<div class="card-meta">%s%s</div>' % (
             ('<span class="badge">%s</span>' % h(p["role_zh"]))
             if p.get("role_zh") else "",
             ('<span class="badge">%s</span>' % h(p["subgroup"]))
             if p.get("subgroup") else "")]
    if p.get("focus_zh"):
        b.append('<p class="detail-summary">%s</p>' % h(p["focus_zh"]))
    if p.get("list_note"):
        b.append('<p class="conf-note">%s</p>' % h(p["list_note"]))
    if accs:
        b.append('<h2 class="section-title">公開帳戶</h2><p class="card-meta">%s'
                 '</p>' % " ".join(
                     '<a class="chip" href="%s" target="_blank" rel="noopener '
                     'noreferrer">%s%s</a>' % (h(a["url"]), h(a.get("platform")),
                                               " ✓" if a.get("verified") else "")
                     for a in accs))
    b.append('<h2 class="section-title">最新動態</h2>')
    if not updates:
        b.append('<p class="status-line">暫時未有收錄的動態。</p>')
    for u in updates:
        b.append('<div class="source-post"><div class="handle">%s</div>' % h(
            " · ".join(x for x in [u.get("page_date"), u.get("kind"),
                                   u.get("platform")] if x)))
        b.append("<p>%s</p>" % h(u.get("summary_zh")))
        if u.get("quote_en"):
            b.append('<blockquote class="conf-note" lang="en">“%s”</blockquote>'
                     '<p class="ref">原文引述</p>' % h(u["quote_en"]))
        if safe_url(u.get("url")):
            b.append('<a href="%s" target="_blank" rel="noopener noreferrer">'
                     '開啟原文 ↗</a>' % h(u["url"]))
        b.append("</div>")
    b.append('<p style="margin-top:18px"><a class="chip" href="../#/figures">'
             '打開互動版（人物動向）→</a></p>')
    b.append('<p class="fam-disclaimer">動態為摘要及短句引述，版權屬原作者；'
             '職位或帳戶可能已有變動。</p>')
    b.append(term_note(" ".join([p.get("focus_zh") or "", p.get("role_zh") or ""]
                                + [u.get("summary_zh") or "" for u in updates])))
    b.append("</article>")
    ld = {"@context": "https://schema.org", "@type": "Person",
          "name": p.get("name_en") or slug, "url": url}
    if p.get("name_zh") and p.get("name_zh") != p.get("name_en"):
        ld["alternateName"] = p["name_zh"]
    if p.get("role_zh"):
        ld["jobTitle"] = p["role_zh"]
    if p.get("focus_zh"):
        ld["description"] = p["focus_zh"]
    if accs:
        ld["sameAs"] = [a["url"] for a in accs]
    desc = clip("%s：%s" % (p.get("role_zh") or "", p.get("focus_zh") or ""), 150)
    return page(title="%s｜人物動向｜知心選 PsyPick" % name, desc=desc,
                canonical=url, og_image=DEFAULT_OG, og_type="profile",
                body="\n".join(x for x in b if x), ld=jsonld(ld), up="../")


# ---------------------------------------------------------------- RSS / sitemap
def rfc822(s):
    try:
        dt = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except Exception:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return format_datetime(dt)


def feed_xml(entries, built):
    items = sorted(entries, key=lambda e: e.get("first_seen_at") or "",
                   reverse=True)[:FEED_N]
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
           "<channel>",
           "<title>知心選 PsyPick</title>",
           "<link>%s</link>" % PP,
           '<atom:link href="%sfeed.xml" rel="self" type="application/rss+xml"/>'
           % PP,
           "<description>AI × 心理學的案例訊號站：研究、臨床實務、倫理與免費進修，"
           "附心理專業視角的註解</description>",
           "<language>zh-Hant</language>",
           "<lastBuildDate>%s</lastBuildDate>" % format_datetime(built)]
    for e in items:
        link = PP + "p/" + e["slug"] + ".html"
        out.append("<item>")
        out.append("<title>%s</title>" % h(e.get("title_zh")))
        out.append("<link>%s</link>" % h(link))
        out.append('<guid isPermaLink="true">%s</guid>' % h(link))
        pd = rfc822(e.get("first_seen_at"))
        if pd:
            out.append("<pubDate>%s</pubDate>" % pd)
        if e.get("category"):
            out.append("<category>%s</category>" % h(e["category"]))
        out.append("<description>%s</description>" % h(e.get("summary_zh")))
        out.append("</item>")
    out += ["</channel>", "</rss>", ""]
    return "\n".join(out)


def sitemap_xml(base_path, generated):
    """保留 base_path 內非產生頁的 <url>（原樣），再加 generated [(loc, lastmod)]。"""
    kept = []
    if os.path.exists(base_path):
        root = ET.parse(base_path).getroot()
        for u in root.findall("{%s}url" % SM_NS):
            loc = (u.findtext("{%s}loc" % SM_NS) or "").strip()
            if not loc or loc.startswith(GENERATED_PREFIXES) \
                    or loc == PP + "feed.xml":
                continue
            lm = (u.findtext("{%s}lastmod" % SM_NS) or "").strip()
            kept.append((loc, lm))
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="%s">' % SM_NS]
    for loc, lm in kept + list(generated):
        out.append("  <url><loc>%s</loc>%s</url>" % (
            h(loc), ("<lastmod>%s</lastmod>" % h(lm)) if lm else ""))
    out += ["</urlset>", ""]
    return "\n".join(out), len(kept)


def clean_dir(path):
    if os.path.isdir(path):
        for fn in os.listdir(path):
            if fn.endswith(".html"):
                os.remove(os.path.join(path, fn))


# ---------------------------------------------------------------- 入口
def generate(data_dir, index, figures, site_root, write_sitemap):
    psypick_dir = os.path.dirname(os.path.abspath(data_dir))
    entries = [e for e in index.get("cases") or []
               if SLUG_OK.match(e.get("slug") or "")]
    live = {e["slug"]: e for e in entries}
    levels = (index.get("config") or {}).get("evidence_levels") or {}
    built = datetime.now(timezone.utc)

    p_dir = os.path.join(psypick_dir, "p")
    f_dir = os.path.join(psypick_dir, "fig")
    clean_dir(p_dir)
    clean_dir(f_dir)
    sm = []
    for e in entries:
        case_path = os.path.join(data_dir, "cases", e["slug"] + ".json")
        with open(case_path, encoding="utf-8") as f:
            case = json.load(f)
        write(os.path.join(p_dir, e["slug"] + ".html"),
              case_page(case, e, entries, live, levels))
        lm = max(day(case.get("first_seen_at")), day(e.get("date")))
        sm.append((PP + "p/" + e["slug"] + ".html", lm))

    people = [p for p in figures.get("people") or []
              if SLUG_OK.match(p.get("slug") or "")]
    by = {}
    for u in figures.get("updates") or []:
        by.setdefault(u.get("person"), []).append(u)
    for p in people:
        ups = sorted(by.get(p["slug"], []), key=lambda u: u.get("page_date") or "",
                     reverse=True)
        write(os.path.join(f_dir, p["slug"] + ".html"), fig_page(p, ups))
        dates = [day(u.get("page_date")) for u in ups if day(u.get("page_date"))]
        lm = max(dates) if dates else day(figures.get("updated"))
        sm.append((PP + "fig/" + p["slug"] + ".html", lm))

    write(os.path.join(psypick_dir, "feed.xml"), feed_xml(entries, built))

    kept = None
    if write_sitemap and site_root:
        path = os.path.join(site_root, "sitemap.xml")
        text, kept = sitemap_xml(path, sm)
        write(path, text)
    print("static: case pages %d | figure pages %d | feed %d | sitemap %s"
          % (len(entries), len(people), min(FEED_N, len(entries)),
             ("kept %d + %d" % (kept, len(sm))) if kept is not None
             else "skipped（只在 CI 或 --sitemap 時改寫）"))
    return {"cases": len(entries), "figures": len(people), "sitemap": sm}
