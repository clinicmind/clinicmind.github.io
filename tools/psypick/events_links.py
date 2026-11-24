#!/usr/bin/env python3
"""PsyPick 近期活動頁＋日曆檔（C-6）與 IG 連結頁（C-7）。

由 static_pages.generate() 呼叫，產生（建置產物，不入 repo）：
  psypick/events/index.html   近期培訓（ISO event_date ≥ 今日、未歸檔）＋近期會議
  psypick/events.ics          同上，RFC 5545 iCalendar，可訂閱
  psypick/links/index.html    IG「link in bio」頁：最新海報條目＋常用入口

只用 Python 標準函式庫。
"""

import re
from datetime import date, datetime, timedelta, timezone

from static_pages import PP, SITE, DEFAULT_OG, h, page, safe_url, jsonld

ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LINKS_POSTERS = 12


def iso(s):
    s = str(s or "")[:10]
    if not ISO.match(s):
        return None
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


# ---------------------------------------------------------------- 資料
def upcoming_trainings(entries, today):
    out = []
    for e in entries:
        tr = e.get("training") or {}
        d = iso(tr.get("event_date"))
        if d and d >= today and e.get("tier") != "archive":
            out.append((d, e))
    out.sort(key=lambda x: (x[0], x[1]["slug"]))
    return out


def upcoming_conferences(conferences, today):
    out = []
    for c in conferences.get("items") or []:
        start = iso(c.get("start"))
        end = iso(c.get("end")) or start
        if start and end and end >= today and c.get("slug"):
            out.append((start, end, c))
    out.sort(key=lambda x: (x[0], x[2]["slug"]))
    return out


# ---------------------------------------------------------------- iCalendar
def ics_text(s):
    s = str(s or "")
    s = s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
    return s.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")


def ics_fold(line):
    """RFC 5545 3.1：每行不超過 75 個八位元組，續行以一個空格開頭。
    按 UTF-8 位元組切，不切開多位元組字元。"""
    out, cur, size = [], "", 0
    limit = 75
    for ch in line:
        n = len(ch.encode("utf-8"))
        if size + n > limit:
            out.append(cur)
            cur, size, limit = " ", 1, 75
        cur += ch
        size += n
    out.append(cur)
    return "\r\n".join(out)


def vevent(uid, start, end_excl, summary, desc, url, stamp, location=None):
    lines = ["BEGIN:VEVENT",
             "UID:" + uid,
             "DTSTAMP:" + stamp,
             "DTSTART;VALUE=DATE:" + start.strftime("%Y%m%d"),
             "DTEND;VALUE=DATE:" + end_excl.strftime("%Y%m%d"),
             "SUMMARY:" + ics_text(summary),
             "DESCRIPTION:" + ics_text(desc),
             "URL:" + url]
    if location:
        lines.append("LOCATION:" + ics_text(location))
    lines.append("TRANSP:TRANSPARENT")
    lines.append("END:VEVENT")
    return lines


def events_ics(trainings, confs, built):
    stamp = built.strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0",
             "PRODID:-//ClinicMind//PsyPick Events//ZH",
             "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
             "X-WR-CALNAME:知心選 PsyPick 進修與會議",
             "X-WR-TIMEZONE:Asia/Macau",
             "REFRESH-INTERVAL;VALUE=DURATION:PT12H",
             "X-PUBLISHED-TTL:PT12H"]
    for d, e in trainings:
        tr = e.get("training") or {}
        url = PP + "p/" + e["slug"] + ".html"
        desc = " · ".join(x for x in [tr.get("provider"), tr.get("format"),
                                      tr.get("price") or tr.get("price_tier"),
                                      tr.get("language")] if x)
        desc += "\n時間以主辦單位公布為準（此為全日事件，未換算時區）。\n" + url
        lines += vevent("training-%s@clinicmind.github.io" % e["slug"], d,
                        d + timedelta(days=1), e.get("title_zh"), desc, url,
                        stamp, tr.get("format"))
    for start, end, c in confs:
        url = PP + "#/conferences/" + c["slug"]
        place = "，".join(x for x in [c.get("city"), c.get("country")] if x)
        desc = " · ".join(x for x in [c.get("organizer"), c.get("format"),
                                      c.get("fee_text")] if x)
        desc += "\n" + (c.get("url") if safe_url(c.get("url")) else url)
        lines += vevent("conf-%s@clinicmind.github.io" % c["slug"], start,
                        end + timedelta(days=1), c.get("name_zh") or c.get("name_en"),
                        desc, url, stamp,
                        " / ".join(x for x in [place, c.get("format")] if x))
    lines.append("END:VCALENDAR")
    return "\r\n".join(ics_fold(l) for l in lines) + "\r\n"


# ---------------------------------------------------------------- 活動頁
WEEKDAY = "一二三四五六日"


def fmt_day(d):
    return "%d 月 %d 日（週%s）" % (d.month, d.day, WEEKDAY[d.weekday()])


def events_page(trainings, confs, today):
    b = ['<nav class="ref" aria-label="麵包屑"><a href="../">知心選</a> › 近期活動</nav>',
         '<article class="detail-page">',
         '<h1 class="detail-title">近期進修與會議</h1>',
         '<p class="detail-summary">心理專業人員可參加的線上培訓與專業會議，按日期排列。'
         '資料每日自動更新，已過期的活動會自動移走。報名前請以主辦單位公布為準。</p>',
         '<p class="card-meta"><a class="chip" href="../events.ics">下載日曆檔（.ics）</a>'
         '<a class="chip" href="webcal://clinicmind.github.io/psypick/events.ics">'
         '訂閱日曆（Apple／Outlook）</a></p>',
         '<p class="ref">Google 日曆：「其他日曆」→「透過網址新增」，貼上 '
         'https://clinicmind.github.io/psypick/events.ics 。日曆內每項是全日事件，'
         '時間未換算時區，請按報名頁核對。</p>',
         '<h2 class="section-title">線上培訓（%d）</h2>' % len(trainings)]
    if not trainings:
        b.append('<p class="status-line">暫時未有已定日期的培訓。</p>')
    month = None
    for d, e in trainings:
        if (d.year, d.month) != month:
            if month is not None:
                b.append("</ul>")
            month = (d.year, d.month)
            b.append("<h3>%d 年 %d 月</h3><ul>" % month)
        tr = e.get("training") or {}
        extra = " · ".join(x for x in [tr.get("provider"), tr.get("format"),
                                       tr.get("price_tier")] if x)
        b.append('<li><time datetime="%s">%s</time>　<a href="../p/%s.html">%s</a>'
                 '<br><span class="ref">%s</span></li>' % (
                     d.isoformat(), h(fmt_day(d)), h(e["slug"]),
                     h(e.get("title_zh")), h(extra)))
    if month is not None:
        b.append("</ul>")
    b.append('<h2 class="section-title">專業會議（%d）</h2>' % len(confs))
    if not confs:
        b.append('<p class="status-line">暫時未有收錄的近期會議。</p>')
    else:
        b.append("<ul>")
        for start, end, c in confs:
            when = fmt_day(start) + ("" if end == start else " 至 " + fmt_day(end))
            place = "，".join(x for x in [c.get("city"), c.get("country")] if x)
            extra = " · ".join(x for x in [place, c.get("format")] if x)
            b.append('<li><time datetime="%s">%s</time>　<a href="../#/conferences/%s">'
                     '%s</a><br><span class="ref">%s</span></li>' % (
                         start.isoformat(), h(when), h(c["slug"]),
                         h(c.get("name_zh") or c.get("name_en")), h(extra)))
        b.append("</ul>")
    b.append('<p style="margin-top:18px"><a class="chip" href="../#/training">'
             '打開互動版（進修）→</a> <a class="chip" href="../#/conferences">'
             '打開互動版（會議）→</a></p>')
    b.append("</article>")
    items = []
    for i, (d, e) in enumerate(trainings[:50]):
        items.append({"@type": "ListItem", "position": i + 1,
                      "url": PP + "p/" + e["slug"] + ".html",
                      "name": e.get("title_zh")})
    ld = {"@context": "https://schema.org", "@type": "ItemList",
          "name": "知心選 PsyPick 近期進修", "itemListElement": items}
    return page(title="近期進修與會議（心理專業人員）｜知心選 PsyPick",
                desc="心理專業人員可參加的近期線上培訓與專業會議，按日期排列，"
                     "可下載或訂閱日曆。%d 個培訓、%d 個會議。"
                     % (len(trainings), len(confs)),
                canonical=PP + "events/", og_image=DEFAULT_OG, og_type="website",
                body="\n".join(b), ld=jsonld(ld), up="../")


# ---------------------------------------------------------------- IG 連結頁
def links_page(entries):
    posters = [e for e in entries if (e.get("poster") or {}).get("src")]
    posters.sort(key=lambda e: ((e["poster"].get("made") or ""),
                                e.get("first_seen_at") or ""), reverse=True)
    posters = posters[:LINKS_POSTERS]
    btn = ('display:block;padding:12px 16px;margin:8px 0;border:1px solid #CFDAD5;'
           'border-radius:12px;background:#fff;text-decoration:none;font-weight:600')
    b = ['<article class="detail-page" style="max-width:560px;margin:0 auto">',
         '<h1 class="detail-title" style="text-align:center">知心選 PsyPick</h1>',
         '<p class="detail-summary" style="text-align:center">AI × 心理學的案例訊號站：'
         '研究、臨床實務與免費進修，附心理專業視角的註解。</p>',
         '<nav aria-label="常用入口">',
         '<a style="%s" href="../">首頁：最新條目</a>' % btn,
         '<a style="%s" href="../events/">近期進修與會議（可訂閱日曆）</a>' % btn,
         '<a style="%s" href="../#/training">免費線上培訓</a>' % btn,
         '<a style="%s" href="../#/family">親子版</a>' % btn,
         '<a style="%s" href="../feed.xml">RSS 訂閱</a>' % btn,
         '<a style="%s" href="../about.html">編輯方針與免責聲明</a>' % btn,
         '<a style="%s" href="../../">臨床心語 ClinicMind 主站</a>' % btn,
         "</nav>"]
    if posters:
        b.append('<h2 class="section-title">IG 海報條目</h2>')
        b.append('<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px">')
        for e in posters:
            p = e["poster"]
            b.append('<a href="../p/%s.html" style="text-decoration:none">'
                     '<img src="../%s" alt="%s" loading="lazy" '
                     'style="width:100%%;border-radius:10px;display:block">'
                     '<span class="ref">%s</span></a>' % (
                         h(e["slug"]), h(p["src"]),
                         h(p.get("alt") or p.get("alt_zh") or e.get("title_zh")),
                         h(e.get("title_zh"))))
        b.append("</div>")
    b.append("</article>")
    return page(title="IG 連結｜知心選 PsyPick",
                desc="知心選 PsyPick 的 Instagram 連結頁：最新海報條目、近期進修、"
                     "RSS 與編輯方針。",
                canonical=PP + "links/", og_image=DEFAULT_OG, og_type="website",
                body="\n".join(b), ld="", up="../")
