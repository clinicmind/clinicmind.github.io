/* 知心選 PsyPick 前端：讀 data/index.json 與 data/cases/<slug>.json，全部在瀏覽器渲染。 */
(function () {
  "use strict";

  var STR = {
    zh: {
      appName: "知心選", tagline: "AI × 心理學的案例訊號站", navHome: "首頁", navFeatured: "精選", navTraining: "進修", navSaved: "★ 收藏",
      langLabel: "EN", loading: "載入中…", loadError: "資料載入失敗", retry: "重試", empty: "還沒有案例。",
      search: "搜尋標題、摘要、標籤…", all: "全部", heat: "熱度", collection: "合集 · {n} 篇", verify: "待查證", ethics: "⚑ 倫理提醒",
      free: "免費", lowCost: "低價", deadline: "截止", soon: "即將截止", anytime: "隨時可上", ce: "有學分",
      archive: "歸檔（{n}）", noMatches: "沒有符合條件的案例", back: "← 返回", save: "收藏", saved: "已收藏",
      brief: "看點", psych: "心理學視角", evidence: "證據等級", population: "適用對象", flags: "倫理旗標", concepts: "相關概念",
      questions: "督導討論題", caution: "使用提醒", source: "來源", related: "相關案例", openSource: "開啟原文 ↗", prompt: "原文 Prompt",
      trainingInfo: "培訓資訊", provider: "主辦", format: "形式", price: "費用", credits: "學分", language: "語言", eventDate: "上課日期",
      audience: "適合對象", topic: "主題", signup: "報名連結 ↗", ref: "出處", verifyNote: "這則內容的部分資訊尚未查證，使用前請自行確認。",
      featuredTitle: "歷屆精選", featuredSub: "熱度夠高的案例會自動晉升，每週最多 {n} 篇。", featuredEmpty: "還沒有精選案例。",
      trainingTitle: "免費與低價進修", trainingSub: "心理專業人員可參加的線上課程、工作坊與網上研討會，依截止日排序。",
      trainingEmpty: "目前沒有開放中的培訓。", savedTitle: "我的收藏", savedEmpty: "還沒有收藏。看到想留著的案例，按卡片右上的 ☆。",
      onlyFree: "只看免費", helpTitle: "卡片上的數字與標記",
      helpHeat: "綜合分數的四捨五入值，不是按讚數。由編輯評的吸引力分（0–3）、同一件事被幾篇來源提到（取對數）、證據等級達對照試驗以上加 1 分、編輯加星加 3 分組成；分數每 {d} 天減半。原始分數達 {m} 分且在全站前 {n} 名就進入精選。培訓不衰減，截止前 7 天加分。",
      helpCollection: "多個來源講同一件事時合併成一個案例，顯示「合集 · N 篇」。",
      helpEvidence: "0 個人經驗或評論、1 產品宣稱、2 前導或質性研究、3 對照試驗、4 系統性回顧或統合分析。",
      helpVerify: "資訊不完整或來自社群平台、尚未查證的內容。", footerRights: "內容版權屬原作者；本站提供導讀與專業註解，不構成醫療或治療建議。",
      week: "週", notFound: "找不到這一頁，可能已移除或網址有誤。", toHome: "回首頁",
      intro: "AI × 心理學的案例訊號站：研究、倫理事件與進修資訊，每則附心理專業註解。按右上「?」看卡片標記的意思。"
    },
    en: {
      appName: "PsyPick", tagline: "A signal station for AI × psychology", navHome: "Home", navFeatured: "Featured", navTraining: "Training", navSaved: "★ Saved",
      langLabel: "中文", loading: "Loading…", loadError: "Failed to load data", retry: "Retry", empty: "No cases yet.",
      search: "Search titles, summaries, tags…", all: "All", heat: "Heat", collection: "Collection · {n} posts", verify: "Unverified", ethics: "⚑ Ethics note",
      free: "Free", lowCost: "Low cost", deadline: "Deadline", soon: "Closing soon", anytime: "Self-paced", ce: "CE credits",
      archive: "Archive ({n})", noMatches: "No matching cases", back: "← Back", save: "Save", saved: "Saved",
      brief: "Highlights", psych: "Psychology lens", evidence: "Evidence", population: "Population", flags: "Ethics flags", concepts: "Concepts",
      questions: "Supervision questions", caution: "Caution", source: "Sources", related: "Related cases", openSource: "Open source ↗", prompt: "Original prompt",
      trainingInfo: "Training details", provider: "Provider", format: "Format", price: "Price", credits: "Credits", language: "Language", eventDate: "Date",
      audience: "Audience", topic: "Topic", signup: "Sign up ↗", ref: "Source", verifyNote: "Some details have not been verified yet. Please check before relying on them.",
      featuredTitle: "Featured history", featuredSub: "Hot cases are promoted automatically, up to {n} per week.", featuredEmpty: "No featured cases yet.",
      trainingTitle: "Free & low-cost training", trainingSub: "Online courses, workshops and webinars for mental health professionals, sorted by deadline.",
      trainingEmpty: "No open trainings right now.", savedTitle: "Saved cases", savedEmpty: "Nothing saved yet. Tap ☆ on a card to keep it.",
      onlyFree: "Free only", helpTitle: "What the numbers mean",
      helpHeat: "A rounded composite score, not a like count: an editor appeal score (0–3), how many sources mention it (log-scaled), +1 for controlled-trial evidence or better, +3 for an editor star. It halves every {d} days. Raw score ≥ {m} and inside the top {n} → Featured. Trainings don't decay and get a boost in their last 7 days.",
      helpCollection: "When several sources cover the same thing they are merged into one case, shown as \"Collection · N posts\".",
      helpEvidence: "0 opinion, 1 vendor claim, 2 pilot/qualitative, 3 controlled trial, 4 systematic review/meta-analysis.",
      helpVerify: "Incomplete or social-media-sourced details not yet verified.", footerRights: "All content belongs to its original creators. Commentary here is not medical or treatment advice.",
      week: "Week", notFound: "This page could not be found. It may have been removed or the link is wrong.", toHome: "Back to home",
      intro: "Signals from AI × psychology: research, ethics cases and training, each with a note from a psychology perspective. Tap \"?\" for what the card labels mean."
    }
  };

  // ---------- 本機偏好（收藏、已讀、語言）；讀寫失敗時照常運作 ----------
  var STORE_KEY = "psypick:v1";
  var prefs = { lang: null, favorites: [], readMarks: {} };
  try {
    var raw = JSON.parse(localStorage.getItem(STORE_KEY) || "null");
    if (raw && typeof raw === "object") {
      prefs.lang = raw.lang === "en" || raw.lang === "zh" ? raw.lang : null;
      prefs.favorites = Array.isArray(raw.favorites) ? raw.favorites : [];
      prefs.readMarks = raw.readMarks && typeof raw.readMarks === "object" ? raw.readMarks : {};
    }
  } catch (e) { /* ignore */ }
  if (!prefs.lang) {
    var langs = (navigator.languages || [navigator.language || ""]).join(",").toLowerCase();
    prefs.lang = /(^|,)zh|-(hk|mo|tw)(,|$)/.test(langs) ? "zh" : "en";
  }
  function persist() { try { localStorage.setItem(STORE_KEY, JSON.stringify(prefs)); } catch (e) { /* ignore */ } }
  function t(k, vars) {
    var s = (STR[prefs.lang] && STR[prefs.lang][k]) || STR.zh[k] || k;
    if (vars) Object.keys(vars).forEach(function (v) { s = s.split("{" + v + "}").join(String(vars[v])); });
    return s;
  }
  function isFav(slug) { return prefs.favorites.indexOf(slug) >= 0; }
  function toggleFav(slug) {
    var i = prefs.favorites.indexOf(slug);
    if (i >= 0) prefs.favorites.splice(i, 1); else prefs.favorites.push(slug);
    persist();
  }

  // ---------- 工具 ----------
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function safeUrl(u) { return /^https?:\/\//i.test(u || "") ? u : ""; }
  function linkify(text) {
    return esc(text).replace(/https?:\/\/[^\s<]+/g, function (u) { return '<a href="' + u + '" target="_blank" rel="noopener noreferrer">' + u + "</a>"; });
  }
  function pick(obj, base) { return prefs.lang === "en" ? (obj[base + "_en"] || obj[base + "_zh"]) : (obj[base + "_zh"] || obj[base + "_en"]); }
  function when(c) {
    if (c.date) return c.date;
    var d = (c.posts || []).map(function (p) { return p.posted_at; }).filter(Boolean).sort();
    return d[0] || c.first_seen_at;
  }
  function day(s) { return (s || "").slice(0, 10); }
  var DATA = null, CATS = {}, app = document.getElementById("app");
  function catInfo(name) { return CATS[name] || { name: name, en: name, color: "var(--ink-3)" }; }
  function catLabel(name) { var c = catInfo(name); return prefs.lang === "en" ? c.en : c.name; }

  function getJSON(path) {
    return fetch(path, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    });
  }
  function loadIndex() {
    if (DATA) return Promise.resolve(DATA);
    return getJSON("data/index.json").then(function (d) {
      DATA = d;
      (d.config.categories || []).forEach(function (c) { CATS[c.name] = c; });
      return d;
    });
  }

  // ---------- 卡片 ----------
  function trainingBadges(c) {
    var tr = c.training || {}, out = [];
    if (tr.price_tier === "免費") out.push('<span class="badge badge-free">' + t("free") + "</span>");
    else if (tr.price_tier === "低價") out.push('<span class="badge">' + t("lowCost") + (tr.price ? " " + esc(tr.price) : "") + "</span>");
    if (tr.ce_credits && !/^(無|否|no|none)$/i.test(tr.ce_credits)) out.push('<span class="badge">' + t("ce") + "</span>");
    if (c.deadline_soon) out.push('<span class="badge badge-soon">' + t("soon") + "</span>");
    return out.join("");
  }
  function trainingLine(c) {
    var tr = c.training || {};
    var when = tr.deadline ? t("deadline") + " " + esc(tr.deadline) : (tr.event_date ? esc(tr.event_date) : t("anytime"));
    return '<div class="training-line">' + [esc(tr.provider), when, esc(tr.language)].filter(Boolean).join(" · ") + "</div>";
  }
  function cardHTML(c) {
    var cat = catInfo(c.category), title = pick(c, "title"), read = prefs.readMarks[c.slug] ? " card-read" : "";
    var isTraining = c.category === DATA.config.training_category;
    var meta = ['<span class="card-stat">' + t("heat") + " " + Math.round(c.hot_score || 0) + "</span>"];
    if (c.mention_count > 1) meta.push('<span class="card-stat">' + t("collection", { n: c.mention_count }) + "</span>");
    if (!isTraining && c.evidence_level != null) {
      var ev = DATA.config.evidence_levels[String(c.evidence_level)];
      meta.push('<span class="badge" title="' + t("evidence") + '">E' + c.evidence_level + (ev ? " " + esc(ev[prefs.lang]) : "") + "</span>");
    }
    if (isTraining) meta.push(trainingBadges(c));
    if (c.has_ethics_flags) meta.push('<span class="badge-ethics">' + t("ethics") + "</span>");
    if (c.verify_needed) meta.push('<span class="badge badge-warn">' + t("verify") + "</span>");
    (c.model_names || []).slice(0, 3).forEach(function (m) { meta.push('<span class="badge">' + esc(m) + "</span>"); });
    return '<article class="card' + read + '" style="--cat:' + esc(cat.color) + '">' +
      '<div class="card-author"><span class="cat-avatar" aria-hidden="true">' + esc(catLabel(c.category).charAt(0)) + "</span>" +
      '<div class="card-author-names"><span class="card-author-name">' + esc(catLabel(c.category)) + '</span><time datetime="' + esc(when(c)) + '">' + esc(day(when(c))) + "</time></div>" +
      '<button class="fav-star" data-fav="' + esc(c.slug) + '" aria-pressed="' + isFav(c.slug) + '" aria-label="' + t("save") + '">' + (isFav(c.slug) ? "★" : "☆") + "</button></div>" +
      '<h3 class="card-title"><a href="#/case/' + encodeURIComponent(c.slug) + '">' + esc(title) + "</a></h3>" +
      (isTraining ? trainingLine(c) : "") +
      '<p class="card-summary">' + esc(pick(c, "summary")) + "</p>" +
      '<div class="card-meta">' + meta.join("") + "</div></article>";
  }
  function rowHTML(c) {
    return '<div class="card-row" style="--cat:' + esc(catInfo(c.category).color) + '"><span class="cat-dot"></span><a href="#/case/' +
      encodeURIComponent(c.slug) + '">' + esc(pick(c, "title")) + "</a><time>" + esc(day(when(c))) + "</time></div>";
  }
  function grid(list) { return '<div class="masonry">' + list.map(cardHTML).join("") + "</div>"; }

  // ---------- 頁面 ----------
  var homeState = { cat: null, dom: null, q: "" };
  function inDomain(c, name) {
    var d = (DATA.config.domains || []).filter(function (x) { return x.name === name; })[0];
    if (!d) return true;
    return (c.tags || []).some(function (t) { return d.tags.indexOf(t) >= 0; });
  }
  function matches(c, q) {
    if (!q) return true;
    var hay = [c.title_zh, c.title_en, c.summary_zh, c.summary_en].concat(c.tags || [], c.model_names || []).join(" ").toLowerCase();
    return q.toLowerCase().split(/\s+/).filter(Boolean).every(function (w) { return hay.indexOf(w) >= 0; });
  }
  function renderHome() {
    var cases = DATA.cases, counts = {};
    cases.forEach(function (c) { counts[c.category] = (counts[c.category] || 0) + 1; });
    var chips = '<button class="chip' + (homeState.cat ? "" : " on") + '" data-cat="">' + t("all") + ' <span class="count">' + cases.length + "</span></button>" +
      DATA.config.categories.map(function (c) {
        return '<button class="chip' + (homeState.cat === c.name ? " on" : "") + '" data-cat="' + esc(c.name) + '" style="--dot:' + esc(c.color) + '"><span class="dot"></span>' +
          esc(prefs.lang === "en" ? c.en : c.name) + ' <span class="count">' + (counts[c.name] || 0) + "</span></button>";
      }).join("");
    var doms = (DATA.config.domains || []).map(function (d) {
      var n = cases.filter(function (c) { return inDomain(c, d.name); }).length;
      if (!n) return "";
      return '<button class="chip' + (homeState.dom === d.name ? " on" : "") + '" data-dom="' + esc(d.name) + '">' +
        esc(prefs.lang === "en" ? d.en : d.name) + ' <span class="count">' + n + "</span></button>";
    }).join("");
    app.innerHTML = '<p class="home-intro">' + esc(t("intro")) + '</p><div class="toolbar"><input class="search" id="search" type="search" aria-label="' + t("search") + '" placeholder="' + t("search") + '" value="' + esc(homeState.q) + '">' +
      '<div class="chip-row">' + chips + '</div>' + (doms ? '<div class="chip-row chip-row-domain">' + doms + '</div>' : '') + '</div><div id="results"></div>';
    renderResults();
    document.getElementById("search").addEventListener("input", function (e) { homeState.q = e.target.value; renderResults(); });
  }
  function renderResults() {
    if (!DATA.cases.length) { document.getElementById("results").innerHTML = '<div class="status-line">' + t("empty") + "</div>"; return; }
    var list = DATA.cases.filter(function (c) { return (!homeState.cat || c.category === homeState.cat) && (!homeState.dom || inDomain(c, homeState.dom)) && matches(c, homeState.q); });
    var live = list.filter(function (c) { return c.tier !== "archive"; }), arch = list.filter(function (c) { return c.tier === "archive"; });
    var html = list.length ? grid(live) : '<div class="status-line">' + t("noMatches") + "</div>";
    if (arch.length) html += '<details class="archive-fold"><summary>' + t("archive", { n: arch.length }) + "</summary>" + arch.map(rowHTML).join("") + "</details>";
    document.getElementById("results").innerHTML = html;
  }

  function isoWeek(s) {
    var d = new Date(s); d = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
    var dayNum = d.getUTCDay() || 7; d.setUTCDate(d.getUTCDate() + 4 - dayNum);
    var y = new Date(Date.UTC(d.getUTCFullYear(), 0, 1)), w = Math.ceil(((d - y) / 86400000 + 1) / 7);
    var mon = new Date(d); mon.setUTCDate(d.getUTCDate() - 3); var sun = new Date(mon); sun.setUTCDate(mon.getUTCDate() + 6);
    function md(x) { return (x.getUTCMonth() + 1) + "/" + x.getUTCDate(); }
    return { key: d.getUTCFullYear() + "-W" + (w < 10 ? "0" : "") + w, label: d.getUTCFullYear() + " " + t("week") + " " + w + " · " + md(mon) + "–" + md(sun) };
  }
  function renderFeatured() {
    var n = DATA.config.featured_top_n, groups = {}, order = [];
    DATA.cases.filter(function (c) { return c.featured_at; }).forEach(function (c) {
      var w = isoWeek(c.featured_at);
      if (!groups[w.key]) { groups[w.key] = { label: w.label, list: [] }; order.push(w.key); }
      groups[w.key].list.push(c);
    });
    order.sort().reverse();
    var body = order.map(function (k) {
      var g = groups[k]; g.list.sort(function (a, b) { return b.hot_score - a.hot_score; });
      return '<h3 class="week-title">' + esc(g.label) + "</h3>" + grid(g.list.slice(0, n));
    }).join("");
    app.innerHTML = '<h2 class="page-title">' + t("featuredTitle") + '</h2><p class="page-sub">' + t("featuredSub", { n: n }) + "</p>" +
      (body || '<div class="status-line">' + t("featuredEmpty") + "</div>");
  }

  var trainingFree = false;
  function renderTraining() {
    var tc = DATA.config.training_category;
    var list = DATA.cases.filter(function (c) { return c.category === tc && c.tier !== "archive" && (!trainingFree || (c.training || {}).price_tier === "免費"); });
    list.sort(function (a, b) {
      var ta = a.training || {}, tb = b.training || {};
      var da = ta.deadline || ta.event_date || "9999", db = tb.deadline || tb.event_date || "9999";
      return da < db ? -1 : da > db ? 1 : b.hot_score - a.hot_score;
    });
    app.innerHTML = '<h2 class="page-title">' + t("trainingTitle") + '</h2><p class="page-sub">' + t("trainingSub") + "</p>" +
      '<div class="chip-row" style="margin-bottom:14px"><button class="chip' + (trainingFree ? " on" : "") + '" id="only-free">' + t("onlyFree") + "</button></div>" +
      (list.length ? grid(list) : '<div class="status-line">' + t("trainingEmpty") + "</div>");
    document.getElementById("only-free").addEventListener("click", function () { trainingFree = !trainingFree; renderTraining(); });
  }

  function renderSaved() {
    var list = DATA.cases.filter(function (c) { return isFav(c.slug); });
    app.innerHTML = '<h2 class="page-title">' + t("savedTitle") + "</h2>" + (list.length ? grid(list) : '<div class="status-line">' + t("savedEmpty") + "</div>");
  }

  function renderCase(slug) {
    app.innerHTML = '<div class="status-line">' + t("loading") + "</div>";
    return getJSON("data/cases/" + encodeURIComponent(slug) + ".json").then(function (c) {
      prefs.readMarks[slug] = new Date().toISOString(); persist();
      var cat = catInfo(c.category), isTraining = c.category === DATA.config.training_category, brief = prefs.lang === "en" ? (c.brief_en || c.brief_zh) : (c.brief_zh || c.brief_en);
      var kind = DATA.config.kinds[c.kind], ev = DATA.config.evidence_levels[String(c.evidence_level)];
      var meta = '<div class="card-meta"><span style="color:' + esc(cat.color) + ';font-weight:600">' + esc(catLabel(c.category)) + "</span>" +
        (kind ? '<span class="badge">' + esc(kind[prefs.lang]) + "</span>" : "") +
        '<time datetime="' + esc(when(c)) + '">' + esc(day(when(c))) + "</time>" +
        '<span class="card-stat">' + t("heat") + " " + Math.round(c.hot_score || 0) + "</span>" +
        ((c.posts || []).length > 1 ? '<span class="card-stat">' + t("collection", { n: c.posts.length }) + "</span>" : "") +
        (c.model_names || []).map(function (m) { return '<span class="badge">' + esc(m) + "</span>"; }).join("") +
        (isTraining ? trainingBadges(c) : "") +
        '<button class="fav-star" data-labeled="1" data-fav="' + esc(c.slug) + '" aria-pressed="' + isFav(c.slug) + '">' + (isFav(c.slug) ? "★ " + t("saved") : "☆ " + t("save")) + "</button></div>";

      var main = '<h2 class="detail-title">' + esc(pick(c, "title")) + "</h2>" + meta +
        (c.verify_needed ? '<p class="badge badge-warn" style="display:inline-block;margin-top:12px">' + t("verifyNote") + "</p>" : "") +
        '<p class="detail-summary">' + esc(pick(c, "summary")) + "</p>";
      if (brief && brief.length) main += '<h3 class="section-title">' + t("brief") + "</h3><ul>" + brief.map(function (b) { return "<li>" + esc(b) + "</li>"; }).join("") + "</ul>";
      if (c.original_prompt) main += '<h3 class="section-title">' + t("prompt") + '</h3><pre class="prompt-block">' + esc(c.original_prompt) + "</pre>";

      if (isTraining && c.training) {
        var tr = c.training, rows = [["provider", tr.provider], ["format", tr.format], ["price", tr.price || tr.price_tier], ["credits", tr.ce_credits],
          ["language", tr.language], ["eventDate", tr.event_date], ["deadline", tr.deadline], ["audience", tr.audience_level], ["topic", tr.topic]];
        main += '<h3 class="section-title">' + t("trainingInfo") + '</h3><div class="panel"><dl class="kv">' +
          rows.filter(function (r) { return r[1]; }).map(function (r) { return "<dt>" + t(r[0]) + "</dt><dd>" + esc(r[1]) + "</dd>"; }).join("") + "</dl>" +
          (safeUrl(tr.signup_url) ? '<p><a href="' + esc(tr.signup_url) + '" target="_blank" rel="noopener noreferrer">' + t("signup") + "</a></p>" : "") + "</div>";
      }

      main += '<h3 class="section-title">' + t("source") + "</h3>" + (c.posts || []).map(function (p) {
        var who = [p.author_handle ? "@" + p.author_handle : "", p.author_name, p.platform, day(p.posted_at)].filter(Boolean).join(" · ");
        return '<div class="source-post"><div class="handle">' + esc(who) + "</div>" + (p.title ? "<b>" + esc(p.title) + "</b>" : "") +
          "<p>" + linkify(p.content) + "</p>" + (safeUrl(p.url) ? '<a href="' + esc(p.url) + '" target="_blank" rel="noopener noreferrer">' + t("openSource") + "</a>" : "") + "</div>";
      }).join("");

      var aside = "";
      if (!isTraining && ev) {
        aside += '<div class="panel"><h4>' + t("psych") + "</h4>";
        aside += '<dl class="kv"><dt>' + t("evidence") + "</dt><dd>E" + esc(c.evidence_level) + " " + esc(ev[prefs.lang]) + (c.evidence_note ? '<div class="ref">' + esc(c.evidence_note) + "</div>" : "") + "</dd>" +
          ((c.population || []).length ? "<dt>" + t("population") + "</dt><dd>" + esc(c.population.join("、")) + "</dd>" : "") + "</dl>";
        aside += "</div>";
      }
      if ((c.ethics_flags || []).length) aside += '<div class="panel"><h4>' + t("flags") + "</h4>" + c.ethics_flags.map(function (f) {
        return '<div class="flag"><b>' + esc(f.flag) + "</b><div>" + esc(f.note) + "</div>" + ((f.refs || []).length ? '<div class="ref">' + t("ref") + "：" + esc(f.refs.join("；")) + "</div>" : "") + "</div>";
      }).join("") + "</div>";
      if ((c.psych_concepts || []).length) aside += '<div class="panel"><h4>' + t("concepts") + "</h4>" + c.psych_concepts.map(function (x) {
        return "<p><b>" + esc(x.name) + "</b>：" + esc(x.note) + (x.ref ? '<br><span class="ref">' + t("ref") + "：" + esc(x.ref) + "</span>" : "") + "</p>";
      }).join("") + "</div>";
      if ((c.supervision_questions || []).length) aside += '<div class="panel"><h4>' + t("questions") + "</h4><ol>" + c.supervision_questions.map(function (q) { return "<li>" + esc(q) + "</li>"; }).join("") + "</ol></div>";
      if (c.caution) aside += '<div class="panel"><h4>' + t("caution") + "</h4><p>" + esc(c.caution) + "</p></div>";
      if (safeUrl(c.hero_media)) aside += '<img class="detail-hero" src="' + esc(c.hero_media) + '" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()">';

      var rel = (c.related || []).length ? '<h3 class="section-title">' + t("related") + "</h3>" + grid(c.related) : "";
      app.innerHTML = '<div class="detail-page"><p style="margin-top:16px"><a href="#/" id="back">' + t("back") + '</a></p><div class="detail-layout"><div>' + main + "</div><aside>" + aside + "</aside></div>" + rel + "</div>";
      document.getElementById("back").addEventListener("click", goBack);
      window.scrollTo(0, 0);
    }).catch(function (err) {
      var gone = /404/.test(String(err && err.message));
      app.innerHTML = '<div class="status-line">' + t(gone ? "notFound" : "loadError") + ' <a href="#/">' + t("toHome") + "</a></div>";
    });
  }

  // ---------- 親子版 ----------
  var FSTR = {
    zh: {
      navFamily: "親子", famTitle: "親子版", famSub: "給港澳家長的親職、兒童發展與親子活動資訊，整理自政府、專業機構和大學的公開資料。",
      famTabHome: "精選", famTabRead: "親職文章", famTabEvents: "親子活動", famTabHelp: "發展與求助",
      famThisWeek: "本週和近期活動", famLatest: "最新文章", famByAge: "按年齡看", famMore: "看全部 →",
      famAllAges: "全部年齡", famAllTopics: "全部主題", famAllRegions: "全部地區", famSearch: "搜尋文章…",
      famWhenAll: "全部日期", famWeek: "本週", famNextWeek: "下週", famMonth: "本月", famFreeOnly: "只看免費",
      famEnded: "已結束（{n}）", famNoItems: "沒有符合條件的內容", famNoEvents: "這段時間沒有收錄的活動。",
      famTips: "實用做法", famSeekHelp: "何時該求助", famAct: "活動資訊", famDate: "日期", famTime: "時間", famVenue: "地點",
      famPrice: "費用", famAge: "年齡", famSignup: "報名方式", famDeadline: "截止", famOrganizer: "主辦", famChecked: "最後核對",
      famAI: "AI 協助整理，內容以原文為準", famDisclaimer: "本版只供參考，不能取代醫生、心理學家或其他專業人員的評估。擔心孩子的情況，請聯絡家庭醫生、母嬰健康院（香港）或衛生中心（澳門）。活動資料可能有變，報名前請以主辦單位公布為準。",
      famStages: "各年齡發展重點", famPhysical: "生理", famPsych: "心理與社交", famWatch: "值得留意的警號", famChecklists: "發展檢核表",
      famHelpWhere: "港澳求助與評估途徑", famPhone: "電話", famUnverified: "待查證", famNoHelp: "發展與求助資料準備中。", famSources: "資料來源"
    },
    en: {
      navFamily: "Parents", famTitle: "For Parents", famSub: "Parenting, child development and family activities for Hong Kong and Macau, drawn from public sources by governments, professional bodies and universities.",
      famTabHome: "Highlights", famTabRead: "Articles", famTabEvents: "Activities", famTabHelp: "Development & help",
      famThisWeek: "Activities this week and soon", famLatest: "Latest articles", famByAge: "Browse by age", famMore: "See all →",
      famAllAges: "All ages", famAllTopics: "All topics", famAllRegions: "All regions", famSearch: "Search articles…",
      famWhenAll: "Any date", famWeek: "This week", famNextWeek: "Next week", famMonth: "This month", famFreeOnly: "Free only",
      famEnded: "Ended ({n})", famNoItems: "Nothing matches", famNoEvents: "No activities listed for this period.",
      famTips: "What you can do", famSeekHelp: "When to get help", famAct: "Activity details", famDate: "Date", famTime: "Time", famVenue: "Venue",
      famPrice: "Fee", famAge: "Ages", famSignup: "How to sign up", famDeadline: "Deadline", famOrganizer: "Organiser", famChecked: "Last checked",
      famAI: "Summarised with AI help; the original source prevails", famDisclaimer: "For reference only and not a substitute for assessment by a doctor, psychologist or other professional. Activity details may change; check with the organiser before signing up.",
      famStages: "Development by age", famPhysical: "Physical", famPsych: "Psychological & social", famWatch: "Signs to watch", famChecklists: "Milestone checklists",
      famHelpWhere: "Where to get help in Hong Kong and Macau", famPhone: "Phone", famUnverified: "Unverified", famNoHelp: "Development and help info is coming soon.", famSources: "Sources"
    }
  };
  Object.keys(FSTR).forEach(function (l) { Object.keys(FSTR[l]).forEach(function (k) { STR[l][k] = FSTR[l][k]; }); });

  var FAM = null, famState = { age: null, topic: null, region: null, q: "", when: null, free: false, eregion: null, eage: null, plat: null, dcat: null };
  function loadFamily() {
    if (FAM) return Promise.resolve(FAM);
    return getJSON("data/family.json").then(function (d) { FAM = d; return d; });
  }
  function addDays(iso, n) { var d = new Date(iso + "T00:00:00Z"); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); }
  function actRange(it) { var a = it.activity || {}; return [a.date_start || "", a.date_end || a.date_start || ""]; }
  function overlaps(it, from, to) { var r = actRange(it); return r[0] <= to && r[1] >= from; }
  function famWhenRange(key) {
    var today = FAM.today;
    if (key === "week") return [today, addDays(today, 6)];
    if (key === "next") return [addDays(today, 7), addDays(today, 13)];
    if (key === "month") { var d = new Date(today + "T00:00:00Z"); var end = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 0)); return [today, end.toISOString().slice(0, 10)]; }
    return null;
  }
  function famDateText(it) {
    var r = actRange(it); return r[1] && r[1] !== r[0] ? r[0] + " – " + r[1] : r[0];
  }
  function famCard(it) {
    if (it.bounty) return bountyCard(it);
    var a = it.activity, badges = [];
    badges.push('<span class="badge">' + esc(it.region) + "</span>");
    if (a && a.free) badges.push('<span class="badge badge-free">' + t("free") + "</span>");
    (it.ages || []).slice(0, 3).forEach(function (x) { badges.push('<span class="badge">' + esc(x) + "</span>"); });
    if (it.verify_needed) badges.push('<span class="badge badge-warn">' + t("verify") + "</span>");
    var head = a ? famDateText(it) : (it.posted_at || "");
    return '<article class="card fam-card' + (a ? " fam-act" : "") + '">' +
      '<div class="card-author"><span class="cat-avatar fam-avatar" aria-hidden="true">' + esc((it.topic || "").charAt(0)) + "</span>" +
      '<div class="card-author-names"><span class="card-author-name">' + esc(it.topic) + "</span><time>" + esc(head) + "</time></div></div>" +
      '<h3 class="card-title"><a href="#/family/item/' + encodeURIComponent(it.slug) + '">' + esc(pick(it, "title")) + "</a></h3>" +
      (a ? '<div class="training-line">' + [esc(a.venue), esc(a.time), esc(a.organizer || it.org)].filter(Boolean).join(" · ") + "</div>" : '<div class="training-line">' + esc(it.org) + "</div>") +
      '<p class="card-summary">' + esc(pick(it, "summary")) + "</p>" +
      '<div class="card-meta">' + badges.join("") + "</div></article>";
  }
  function famGrid(list) { return '<div class="masonry">' + list.map(famCard).join("") + "</div>"; }
  function famChips(name, values, cur, allLabel, label) {
    return '<div class="chip-row">' + '<button class="chip' + (cur ? "" : " on") + '" data-fam="' + name + '" data-v="">' + esc(allLabel) + "</button>" +
      values.map(function (v) {
        var val = Array.isArray(v) ? v[0] : v, lab = Array.isArray(v) ? v[1] : v;
        return '<button class="chip' + (cur === val ? " on" : "") + '" data-fam="' + name + '" data-v="' + esc(val) + '">' + esc(label ? label(lab) : lab) + "</button>";
      }).join("") + "</div>";
  }
  function famShell(tab, body) {
    var tabs = [["", "famTabHome"], ["read", "famTabRead"], ["events", "famTabEvents"], ["help", "famTabHelp"]];
    app.innerHTML = '<h2 class="page-title">' + t("famTitle") + '</h2><p class="page-sub">' + t("famSub") + "</p>" +
      '<nav class="fam-tabs">' + tabs.map(function (x) {
        return '<a href="#/family' + (x[0] ? "/" + x[0] : "") + '" class="' + (tab === x[0] ? "on" : "") + '">' + t(x[1]) + "</a>";
      }).join("") + "</nav>" + body + '<p class="fam-disclaimer">' + t("famDisclaimer") + "</p>";
  }
  function famArticles() { return FAM.items.filter(function (it) { return it.kind === "article"; }); }
  function famEvents() { return FAM.items.filter(function (it) { return it.kind === "activity"; }); }
  function byStart(a, b) { var x = actRange(a)[0], y = actRange(b)[0]; return x < y ? -1 : x > y ? 1 : 0; }
  function byPosted(a, b) { var x = a.posted_at || a.created_at || "", y = b.posted_at || b.created_at || ""; return x < y ? 1 : x > y ? -1 : 0; }

  function renderFamilyHome() {
    var soon = famEvents().filter(function (it) { return !it.ended && actRange(it)[0] <= addDays(FAM.today, 13); }).sort(byStart).slice(0, 6);
    if (soon.length < 3) soon = famEvents().filter(function (it) { return !it.ended; }).sort(byStart).slice(0, 6);
    var latest = famArticles().sort(byPosted).slice(0, 8);
    var ages = '<div class="chip-row">' + FAM.ages.map(function (a) {
      return '<a class="chip" href="#/family/read" data-fam-age="' + esc(a) + '">' + esc(a) + "</a>";
    }).join("") + "</div>";
    famShell("", '<h3 class="week-title">' + t("famByAge") + "</h3>" + ages +
      '<h3 class="week-title">' + t("famThisWeek") + ' <a class="fam-more" href="#/family/events">' + t("famMore") + "</a></h3>" +
      (soon.length ? famGrid(soon) : '<div class="status-line">' + t("famNoEvents") + "</div>") +
      '<h3 class="week-title">' + t("famLatest") + ' <a class="fam-more" href="#/family/read">' + t("famMore") + "</a></h3>" +
      (latest.length ? famGrid(latest) : '<div class="status-line">' + t("famNoItems") + "</div>"));
  }
  function famMatch(it, q) {
    if (!q) return true;
    var hay = [it.title_zh, it.title_en, it.summary_zh, it.summary_en, it.org].concat(it.tags || [], it.tips || []).join(" ").toLowerCase();
    return q.toLowerCase().split(/\s+/).filter(Boolean).every(function (w) { return hay.indexOf(w) >= 0; });
  }
  function renderFamilyRead() {
    famShell("read", '<div class="toolbar"><input class="search" id="fam-search" type="search" placeholder="' + t("famSearch") + '" value="' + esc(famState.q) + '">' +
      famChips("age", FAM.ages, famState.age, t("famAllAges")) +
      famChips("topic", FAM.topics.filter(function (x) { return x !== "親子活動"; }), famState.topic, t("famAllTopics")) +
      famChips("region", FAM.regions, famState.region, t("famAllRegions")) + '</div><div id="fam-results"></div>');
    famReadResults();
    document.getElementById("fam-search").addEventListener("input", function (e) { famState.q = e.target.value; famReadResults(); });
  }
  function famReadResults() {
    var list = famArticles().filter(function (it) {
      return (!famState.age || (it.ages || []).indexOf(famState.age) >= 0) && (!famState.topic || it.topic === famState.topic) &&
        (!famState.region || it.region === famState.region) && famMatch(it, famState.q);
    }).sort(byPosted);
    document.getElementById("fam-results").innerHTML = list.length ? famGrid(list) : '<div class="status-line">' + t("famNoItems") + "</div>";
  }
  function renderFamilyEvents() {
    var all = famEvents(), rng = famWhenRange(famState.when);
    var list = all.filter(function (it) {
      return !it.ended && (!famState.eregion || it.region === famState.eregion) && (!famState.free || (it.activity || {}).free) &&
        (!famState.eage || (it.ages || []).indexOf(famState.eage) >= 0) && (!rng || overlaps(it, rng[0], rng[1]));
    }).sort(byStart);
    var ended = all.filter(function (it) { return it.ended; }).sort(byStart).reverse();
    famShell("events", '<div class="toolbar">' +
      famChips("eregion", ["香港", "澳門"], famState.eregion, t("famAllRegions")) +
      famChips("when", [["week", t("famWeek")], ["next", t("famNextWeek")], ["month", t("famMonth")]], famState.when, t("famWhenAll")) +
      famChips("eage", FAM.ages.filter(function (a) { return a !== "孕期"; }), famState.eage, t("famAllAges")) +
      '<div class="chip-row"><button class="chip' + (famState.free ? " on" : "") + '" data-fam="free" data-v="1">' + t("famFreeOnly") + "</button></div></div>" +
      (list.length ? famGrid(list) : '<div class="status-line">' + t("famNoEvents") + "</div>") +
      (ended.length ? '<details class="archive-fold"><summary>' + t("famEnded", { n: ended.length }) + "</summary>" + ended.map(function (it) {
        return '<div class="card-row"><span class="cat-dot"></span><a href="#/family/item/' + encodeURIComponent(it.slug) + '">' + esc(pick(it, "title")) + "</a><time>" + esc(famDateText(it)) + "</time></div>";
      }).join("") + "</details>" : ""));
  }
  function linkList(list) {
    return (list || []).filter(function (s) { return safeUrl(s.url); }).map(function (s) {
      return '<a href="' + esc(s.url) + '" target="_blank" rel="noopener noreferrer">' + esc(s.title || s.url) + "</a>";
    }).join("、");
  }
  function renderFamilyHelp() {
    var d = FAM.devhelp;
    if (!d) return famShell("help", '<div class="status-line">' + t("famNoHelp") + "</div>");
    var ul = function (xs) { return (xs || []).length ? "<ul>" + xs.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>" : ""; };
    var stages = (d.stages || []).map(function (s) {
      return '<details class="panel fam-stage"><summary><b>' + esc(s.age) + "</b></summary>" +
        ((s.physical || []).length ? "<h4>" + t("famPhysical") + "</h4>" + ul(s.physical) : "") +
        ((s.psychological || []).length ? "<h4>" + t("famPsych") + "</h4>" + ul(s.psychological) : "") +
        ((s.watch || []).length ? '<h4 class="fam-watch">' + t("famWatch") + "</h4>" + ul(s.watch) : "") +
        ((s.sources || []).length ? '<p class="ref">' + t("famSources") + "：" + linkList(s.sources) + "</p>" : "") + "</details>";
    }).join("");
    var checks = (d.checklists || []).filter(function (c) { return safeUrl(c.url); }).map(function (c) {
      return '<li><a href="' + esc(c.url) + '" target="_blank" rel="noopener noreferrer">' + esc(c.title) + "</a>" +
        '<span class="ref"> · ' + esc([c.org, c.lang].filter(Boolean).join(" · ")) + "</span>" + (c.note ? "<div>" + esc(c.note) + "</div>" : "") + "</li>";
    }).join("");
    var regions = ["香港", "澳門"].map(function (r) {
      var rows = (d.help || []).filter(function (h) { return h.region === r; }).map(function (h) {
        return '<div class="fam-help-item"><b>' + (safeUrl(h.url) ? '<a href="' + esc(h.url) + '" target="_blank" rel="noopener noreferrer">' + esc(h.name) + "</a>" : esc(h.name)) + "</b>" +
          (h.verified === false ? ' <span class="badge badge-warn">' + t("famUnverified") + "</span>" : "") +
          "<div>" + esc(h.what) + "</div>" + (h.how ? '<div class="ref">' + esc(h.how) + "</div>" : "") +
          (h.phone ? "<div>" + t("famPhone") + '：<a href="tel:' + esc(String(h.phone).replace(/[^0-9+]/g, "")) + '">' + esc(h.phone) + "</a></div>" : "") + "</div>";
      }).join("");
      return rows ? '<div class="panel"><h4>' + esc(r) + "</h4>" + rows + "</div>" : "";
    }).join("");
    var disc = prefs.lang === "en" ? (d.disclaimer_en || d.disclaimer_zh) : (d.disclaimer_zh || d.disclaimer_en);
    famShell("help", (disc ? '<p class="fam-help-note">' + esc(disc) + "</p>" : "") +
      '<h3 class="section-title">' + t("famStages") + "</h3>" + stages +
      (checks ? '<h3 class="section-title">' + t("famChecklists") + '</h3><ul class="fam-checks">' + checks + "</ul>" : "") +
      '<h3 class="section-title">' + t("famHelpWhere") + '</h3><div class="fam-help-grid">' + regions + "</div>");
  }
  function renderFamilyItem(slug) {
    var it = FAM.items.filter(function (x) { return x.slug === slug; })[0];
    if (!it) { app.innerHTML = '<div class="status-line">' + t("famNoItems") + ' <a href="#/family">' + t("back") + "</a></div>"; return; }
    var a = it.activity;
    var meta = '<div class="card-meta"><span style="font-weight:600">' + esc(it.topic) + '</span><span class="badge">' + esc(it.region) + "</span>" +
      (it.ages || []).map(function (x) { return '<span class="badge">' + esc(x) + "</span>"; }).join("") +
      (a && a.free ? '<span class="badge badge-free">' + t("free") + "</span>" : "") +
      (it.posted_at ? "<time>" + esc(it.posted_at) + "</time>" : "") + "</div>";
    var main = '<h2 class="detail-title">' + esc(pick(it, "title")) + "</h2>" + meta +
      (it.verify_needed ? '<p class="badge badge-warn" style="display:inline-block;margin-top:12px">' + t("verifyNote") + (it.verify_reason ? "（" + esc(it.verify_reason) + "）" : "") + "</p>" : "") +
      '<p class="detail-summary">' + esc(pick(it, "summary")) + "</p>";
    if (a) {
      var rows = [["famDate", famDateText(it)], ["famTime", a.time], ["famVenue", a.venue], ["famPrice", a.price], ["famAge", a.age_range],
        ["famSignup", a.signup], ["famDeadline", a.deadline], ["famOrganizer", a.organizer || it.org], ["famChecked", a.last_checked]];
      main += '<h3 class="section-title">' + t("famAct") + '</h3><div class="panel"><dl class="kv">' +
        rows.filter(function (r) { return r[1]; }).map(function (r) { return "<dt>" + t(r[0]) + "</dt><dd>" + linkify(r[1]) + "</dd>"; }).join("") + "</dl></div>";
    }
    if ((it.tips || []).length) main += '<h3 class="section-title">' + t("famTips") + "</h3><ul>" + it.tips.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>";
    if (it.when_to_seek_help) main += '<h3 class="section-title">' + t("famSeekHelp") + '</h3><div class="panel fam-seek">' + linkify(it.when_to_seek_help) + "</div>";
    main += '<h3 class="section-title">' + t("source") + '</h3><div class="source-post"><div class="handle">' + esc([it.org, it.source_type].filter(Boolean).join(" · ")) + "</div>" +
      (it.source_title ? "<b>" + esc(it.source_title) + "</b><br>" : "") +
      (safeUrl(it.url) ? '<a href="' + esc(it.url) + '" target="_blank" rel="noopener noreferrer">' + t("openSource") + "</a>" : "") + "</div>" +
      '<p class="ref">' + t("famAI") + "</p>";
    var back = a ? "#/family/events" : "#/family/read";
    app.innerHTML = '<div class="detail-page"><p style="margin-top:16px"><a href="' + back + '" id="back">' + t("back") + "</a></p><div class=\"fam-detail\">" + main + "</div>" +
      '<p class="fam-disclaimer">' + t("famDisclaimer") + "</p></div>";
    document.getElementById("back").addEventListener("click", goBack);
    window.scrollTo(0, 0);
  }
  function renderFamily(sub) {
    return loadFamily().then(function () {
      var m = sub.match(/^item\/(.+)$/);
      if (m) return renderFamilyItem(decodeURIComponent(m[1]));
      if (sub === "read") return renderFamilyRead();
      if (sub === "events") return renderFamilyEvents();
      if (sub === "help") return renderFamilyHelp();
      renderFamilyHome();
    });
  }


  // ---------- 賞金獵人：有報酬的研究項目 ----------
  var BSTR = {
    zh: { navBounty: "賞金獵人", bTitle: "賞金獵人", bSub: "香港、澳門、美國的大學和機構正在招募參加者、有現金或禮券報酬的研究問卷、訪談和實驗。本站只整理公開資料，沒有參與招募；參加前請細閱主辦方的說明和私隱條款，不要提供銀行密碼，也不需要先付任何費用。",
      bAllRegions: "全部地區", bAllTypes: "全部報酬", bSure: "人人有份", bLucky: "抽獎", bOnline: "網上參加", bReward: "報酬", bOrganizer: "主辦", bFunder: "資助／贊助",
      bMethod: "形式", bElig: "參加資格", bDuration: "所需時間", bDeadline: "截止", bHow: "參加方法", bContact: "查詢", bLocation: "地點", bCaution: "注意",
      bInfo: "項目資訊", bNoDeadline: "未列截止日", bEnded: "已截止（{n}）", bEmpty: "目前沒有收錄的項目。", bNoMatch: "沒有符合條件的項目" },
    en: { navBounty: "Paid studies", bTitle: "Paid research studies", bSub: "Surveys, interviews and experiments by universities and organisations in Hong Kong, Macau and the US that pay participants in cash or vouchers. We only list public information and are not involved in recruitment. Read the organiser's information and privacy terms first; never give bank passwords or pay anything to take part.",
      bAllRegions: "All regions", bAllTypes: "All rewards", bSure: "Everyone paid", bLucky: "Lucky draw", bOnline: "Online", bReward: "Reward", bOrganizer: "Organiser", bFunder: "Funded / sponsored by",
      bMethod: "Format", bElig: "Eligibility", bDuration: "Time needed", bDeadline: "Deadline", bHow: "How to join", bContact: "Enquiries", bLocation: "Where", bCaution: "Note",
      bInfo: "Study details", bNoDeadline: "No deadline listed", bEnded: "Closed ({n})", bEmpty: "No studies listed right now.", bNoMatch: "No matching studies" }
  };
  Object.keys(BSTR).forEach(function (l) { Object.keys(BSTR[l]).forEach(function (k) { STR[l][k] = BSTR[l][k]; }); });
  var bState = { region: null, type: null, sure: false, online: false };
  function bountyCard(it) {
    var b = it.bounty, badges = ['<span class="badge">' + esc(it.region) + "</span>"];
    if (b.method) badges.push('<span class="badge">' + esc(b.method) + "</span>");
    badges.push('<span class="badge ' + (b.guaranteed ? "badge-free" : "") + '">' + (b.guaranteed ? t("bSure") : t("bLucky")) + "</span>");
    if (it.verify_needed) badges.push('<span class="badge badge-warn">' + t("verify") + "</span>");
    return '<article class="card fam-card fam-bounty">' +
      '<div class="card-author"><span class="cat-avatar fam-avatar" aria-hidden="true">' + esc((b.organizer || it.org || "?").charAt(0)) + "</span>" +
      '<div class="card-author-names"><span class="card-author-name">' + esc(b.organizer || it.org) + "</span><time>" +
      esc(b.deadline ? t("bDeadline") + " " + b.deadline : t("bNoDeadline")) + "</time></div></div>" +
      '<h3 class="card-title"><a href="#/bounty/' + encodeURIComponent(it.slug) + '">' + esc(pick(it, "title")) + "</a></h3>" +
      '<div class="reward-amount">' + esc(b.reward) + "</div>" +
      '<div class="training-line">' + [esc(b.eligibility), esc(b.duration)].filter(Boolean).join(" · ") + "</div>" +
      '<p class="card-summary">' + esc(pick(it, "summary")) + "</p>" +
      '<div class="card-meta">' + badges.join("") + "</div></article>";
  }
  function renderBounty() {
    var all = FAM.items.filter(function (it) { return it.kind === "bounty"; });
    var types = []; all.forEach(function (it) { var x = it.bounty.reward_type; if (x && types.indexOf(x) < 0) types.push(x); });
    var list = all.filter(function (it) {
      var b = it.bounty;
      return !it.ended && (!bState.region || it.region === bState.region) && (!bState.type || b.reward_type === bState.type) &&
        (!bState.sure || b.guaranteed) && (!bState.online || /網上|online/i.test(b.location || b.method || ""));
    }).sort(function (a, b) { var x = a.bounty.deadline || "9999", y = b.bounty.deadline || "9999"; return x < y ? -1 : x > y ? 1 : 0; });
    var ended = all.filter(function (it) { return it.ended; });
    app.innerHTML = '<h2 class="page-title">' + t("bTitle") + '</h2><p class="page-sub">' + t("bSub") + '</p><div class="toolbar">' +
      famChips("b:region", FAM.bounty_regions || ["香港", "澳門", "美國"], bState.region, t("bAllRegions")) +
      (types.length > 1 ? famChips("b:type", types, bState.type, t("bAllTypes")) : "") +
      '<div class="chip-row"><button class="chip' + (bState.sure ? " on" : "") + '" data-fam="b:sure" data-v="1">' + t("bSure") + '</button>' +
      '<button class="chip' + (bState.online ? " on" : "") + '" data-fam="b:online" data-v="1">' + t("bOnline") + "</button></div></div>" +
      (list.length ? famGrid(list) : '<div class="status-line">' + (all.length ? t("bNoMatch") : t("bEmpty")) + "</div>") +
      (ended.length ? '<details class="archive-fold"><summary>' + t("bEnded", { n: ended.length }) + "</summary>" + ended.map(function (it) {
        return '<div class="card-row"><span class="cat-dot"></span><a href="#/bounty/' + encodeURIComponent(it.slug) + '">' + esc(pick(it, "title")) + "</a><time>" + esc(it.bounty.deadline) + "</time></div>";
      }).join("") + "</details>" : "");
  }
  function renderBountyItem(slug) {
    var it = FAM.items.filter(function (x) { return x.slug === slug && x.bounty; })[0];
    if (!it) { app.innerHTML = '<div class="status-line">' + t("bNoMatch") + ' <a href="#/bounty">' + t("back") + "</a></div>"; return; }
    var b = it.bounty;
    var rows = [["bReward", b.reward + (b.guaranteed ? "（" + t("bSure") + "）" : "（" + t("bLucky") + "）")], ["bOrganizer", b.organizer || it.org], ["bFunder", b.funder],
      ["bMethod", b.method], ["bElig", b.eligibility], ["bDuration", b.duration], ["bDeadline", b.deadline || t("bNoDeadline")], ["bLocation", b.location],
      ["bHow", b.how_to_join], ["bContact", b.contact], ["famChecked", b.last_checked]];
    var main = '<h2 class="detail-title">' + esc(pick(it, "title")) + '</h2><div class="card-meta"><span class="badge">' + esc(it.region) + "</span>" +
      (it.posted_at ? "<time>" + esc(it.posted_at) + "</time>" : "") + "</div>" +
      (it.verify_needed ? '<p class="badge badge-warn" style="display:inline-block;margin-top:12px">' + t("verifyNote") + (it.verify_reason ? "（" + esc(it.verify_reason) + "）" : "") + "</p>" : "") +
      '<p class="detail-summary">' + esc(pick(it, "summary")) + '</p><h3 class="section-title">' + t("bInfo") + '</h3><div class="panel"><dl class="kv">' +
      rows.filter(function (r) { return r[1]; }).map(function (r) { return "<dt>" + t(r[0]) + "</dt><dd>" + linkify(r[1]) + "</dd>"; }).join("") + "</dl></div>";
    if ((it.tips || []).length) main += '<h3 class="section-title">' + t("famTips") + "</h3><ul>" + it.tips.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>";
    if (b.caution) main += '<h3 class="section-title">' + t("bCaution") + '</h3><div class="panel fam-seek">' + esc(b.caution) + "</div>";
    main += '<h3 class="section-title">' + t("source") + '</h3><div class="source-post"><div class="handle">' + esc([it.org, it.source_type].filter(Boolean).join(" · ")) + "</div>" +
      (it.source_title ? "<b>" + esc(it.source_title) + "</b><br>" : "") +
      (safeUrl(it.url) ? '<a href="' + esc(it.url) + '" target="_blank" rel="noopener noreferrer">' + t("openSource") + "</a>" : "") + "</div>" +
      '<p class="ref">' + t("famAI") + "</p>";
    app.innerHTML = '<div class="detail-page"><p style="margin-top:16px"><a href="#/bounty" id="back">' + t("back") + '</a></p><div class="fam-detail">' + main + "</div>" +
      '<p class="fam-disclaimer">' + t("bSub") + "</p></div>";
    document.getElementById("back").addEventListener("click", goBack);
    window.scrollTo(0, 0);
  }

  // ---------- 會議：全球心理健康／輔導／心理治療會議 ----------
  var CSTR = {
    zh: { navConf: "會議", cTitle: "會議", cSub: "全球英文及華語區心理健康、輔導與心理治療會議：即將舉行與近期已舉行。每場附摘要、費用、報名連結、講者背景與代表作，以及對你的領域的看點。資料取自官方頁面，查不到的標「待查證」。",
      cUpcoming: "即將舉行", cPast: "已舉行", cAllRegions: "全部地區", cAllDomains: "全部領域", cOnline: "含網上參與", cEmpty: "沒有符合條件的會議",
      cWhen: "日期", cWhere: "地點", cFormat: "形式", cLang: "語言", cOrg: "主辦", cFee: "費用", cDeadline: "報名截止", cSite: "官方網頁 ↗", cReg: "報名 ↗",
      cSummary: "會議摘要", cInterest: "你可能感興趣的點", cInfo: "會議資訊", cSpeakers: "講者與代表作", cNoSpeakers: "官方尚未公布講者名單（或本站未能取得）。",
      cWorks: "代表作", cSession: "場次", cNoWorks: "代表作待查證", cVerified: "已核對", cUnverified: "待查證", cVerifyNote: "核對說明", cChecked: "資料查核日",
      cDays: "{n} 天後開始", cToday: "進行中", cEnded: "已結束", cNote: "會議資訊以官方頁面為準；講者簡介與代表作由 Claude 從公開資料整理，標「待查證」者尚未核對。內容以繁體中文提供。" },
    en: { navConf: "Conferences", cTitle: "Conferences", cSub: "Mental health, counselling and psychotherapy conferences in the English- and Chinese-speaking world, upcoming and recent. Each has a summary, fees, sign-up link, speaker backgrounds with key works, and why it may interest you. Content is in Traditional Chinese; unverified items are flagged.",
      cUpcoming: "Upcoming", cPast: "Recent", cAllRegions: "All regions", cAllDomains: "All fields", cOnline: "Online option", cEmpty: "No matching conferences",
      cWhen: "Dates", cWhere: "Where", cFormat: "Format", cLang: "Language", cOrg: "Organiser", cFee: "Fee", cDeadline: "Deadline", cSite: "Official site ↗", cReg: "Register ↗",
      cSummary: "Summary", cInterest: "Why it may interest you", cInfo: "Details", cSpeakers: "Speakers & key works", cNoSpeakers: "No speaker list published (or not retrievable).",
      cWorks: "Key works", cSession: "Session", cNoWorks: "Key works unverified", cVerified: "Verified", cUnverified: "Unverified", cVerifyNote: "Verification notes", cChecked: "Last checked",
      cDays: "starts in {n} days", cToday: "In progress", cEnded: "Ended", cNote: "Event details: check the official page. Speaker bios and key works are compiled by Claude from public sources; items marked unverified are not yet checked." }
  };
  Object.keys(CSTR).forEach(function (l) { Object.keys(CSTR[l]).forEach(function (k) { STR[l][k] = CSTR[l][k]; }); });
  var CONF = null, cState = { when: "upcoming", region: null, domain: null, online: false };
  function loadConf() {
    if (CONF) return Promise.resolve(CONF);
    return getJSON("data/conferences.json").then(function (d) { CONF = d; return d; });
  }
  function confSpan(c) { return c.start === c.end ? c.start : c.start + " – " + c.end; }
  function confNote(c) {
    var today = CONF.today || new Date().toISOString().slice(0, 10);
    if (c.end < today) return t("cEnded");
    if (c.start <= today) return t("cToday");
    var n = Math.round((new Date(c.start + "T00:00:00Z") - new Date(today + "T00:00:00Z")) / 86400000);
    return t("cDays", { n: n });
  }
  function confCard(c) {
    var badges = ['<span class="badge">' + esc(c.region) + "</span>"];
    (c.domains || []).slice(0, 3).forEach(function (d) { badges.push('<span class="badge">' + esc(d) + "</span>"); });
    if (c.verify_needed) badges.push('<span class="badge badge-warn">' + t("cUnverified") + "</span>");
    return '<article class="card fam-card conf-card"><div class="card-author"><span class="cat-avatar fam-avatar" aria-hidden="true">' + esc(c.country.charAt(0)) + "</span>" +
      '<div class="card-author-names"><span class="card-author-name">' + esc(c.city + "，" + c.country) + "</span><time>" + esc(confSpan(c)) + " · " + esc(confNote(c)) + "</time></div></div>" +
      '<h3 class="card-title"><a href="#/conferences/' + encodeURIComponent(c.slug) + '">' + esc(pick(c, "name")) + "</a></h3>" +
      '<div class="training-line">' + [esc(c.format), esc(c.fee_text)].filter(Boolean).join(" · ") + "</div>" +
      '<p class="card-summary">' + esc(c.summary_zh) + "</p>" +
      '<div class="card-meta">' + badges.join("") + "</div></article>";
  }
  function renderConferences() {
    var today = CONF.today, all = CONF.items;
    var list = all.filter(function (c) {
      var past = c.end < today;
      return (cState.when === "past" ? past : !past) && (!cState.region || c.region === cState.region) &&
        (!cState.domain || (c.domains || []).indexOf(cState.domain) >= 0) && (!cState.online || /網上|混合|online|hybrid/i.test(c.format));
    }).sort(function (a, b) { return cState.when === "past" ? (a.start < b.start ? 1 : -1) : (a.start < b.start ? -1 : 1); });
    app.innerHTML = '<h2 class="page-title">' + t("cTitle") + '</h2><p class="page-sub">' + t("cSub") + '</p><div class="toolbar">' +
      '<div class="chip-row"><button class="chip' + (cState.when === "upcoming" ? " on" : "") + '" data-conf="when" data-v="upcoming">' + t("cUpcoming") + '</button>' +
      '<button class="chip' + (cState.when === "past" ? " on" : "") + '" data-conf="when" data-v="past">' + t("cPast") + '</button>' +
      '<button class="chip' + (cState.online ? " on" : "") + '" data-conf="online" data-v="1">' + t("cOnline") + "</button></div>" +
      famChips("c:region", CONF.regions, cState.region, t("cAllRegions")) + famChips("c:domain", CONF.domains, cState.domain, t("cAllDomains")) + "</div>" +
      (list.length ? '<div class="masonry">' + list.map(confCard).join("") + "</div>" : '<div class="status-line">' + t("cEmpty") + "</div>") +
      '<p class="fam-disclaimer">' + t("cNote") + "</p>";
  }
  function speakerBlock(s) {
    var works = (s.works || []).length ? "<ol class=\"conf-works\">" + s.works.map(function (w) {
      var label = esc(w.title) + (w.year ? "（" + esc(w.year) + "）" : "") + (w.type ? " · " + esc(w.type) : "");
      return "<li>" + (safeUrl(w.url) ? '<a href="' + esc(w.url) + '" target="_blank" rel="noopener noreferrer">' + label + "</a>" : label) + "</li>";
    }).join("") + "</ol>" : '<p class="conf-nowork">' + t("cNoWorks") + "</p>";
    return '<div class="panel conf-speaker"><h4>' + esc(s.name) + ' <span class="badge ' + (s.verified ? "badge-free" : "badge-warn") + '">' + (s.verified ? t("cVerified") : t("cUnverified")) + "</span></h4>" +
      '<div class="conf-role">' + esc([s.role, s.affiliation].filter(Boolean).join(" · ")) + "</div>" +
      (s.session ? '<div class="conf-session"><b>' + t("cSession") + "：</b>" + esc(s.session) + "</div>" : "") +
      (s.bio_zh ? "<p>" + esc(s.bio_zh) + "</p>" : "") + '<div class="conf-worksh">' + t("cWorks") + "</div>" + works +
      (s.note ? '<p class="conf-note">' + esc(s.note) + "</p>" : "") + "</div>";
  }
  function renderConference(slug) {
    var c = CONF.items.filter(function (x) { return x.slug === slug; })[0];
    if (!c) { app.innerHTML = '<div class="status-line">' + t("cEmpty") + ' <a href="#/conferences">' + t("back") + "</a></div>"; return; }
    var rows = [["cWhen", confSpan(c) + "（" + confNote(c) + "）"], ["cWhere", [c.venue, c.city, c.country].filter(Boolean).join("，")], ["cFormat", c.format], ["cLang", c.language],
      ["cOrg", c.organizer], ["cFee", c.fee_text], ["cDeadline", c.deadline], ["cChecked", c.last_checked]];
    var links = (safeUrl(c.url) ? '<a class="chip" href="' + esc(c.url) + '" target="_blank" rel="noopener noreferrer">' + t("cSite") + "</a> " : "") +
      (safeUrl(c.register_url) ? '<a class="chip" href="' + esc(c.register_url) + '" target="_blank" rel="noopener noreferrer">' + t("cReg") + "</a>" : "");
    var main = '<h2 class="detail-title">' + esc(c.name_zh) + '</h2><p class="conf-en">' + esc(c.name_en) + '</p><div class="card-meta"><span class="badge">' + esc(c.region) + "</span>" +
      (c.themes || []).map(function (x) { return '<span class="badge">' + esc(x) + "</span>"; }).join("") + (c.verify_needed ? '<span class="badge badge-warn">' + t("cUnverified") + "</span>" : "") + "</div>" +
      '<div class="chip-row" style="margin-top:12px">' + links + "</div>" +
      '<h3 class="section-title">' + t("cSummary") + '</h3><p class="detail-summary">' + esc(c.summary_zh) + "</p>" +
      '<h3 class="section-title">' + t("cInterest") + '</h3><div class="panel conf-interest">' + esc(c.interest_zh) + "</div>" +
      '<h3 class="section-title">' + t("cInfo") + '</h3><div class="panel"><dl class="kv">' + rows.filter(function (r) { return r[1]; }).map(function (r) { return "<dt>" + t(r[0]) + "</dt><dd>" + esc(r[1]) + "</dd>"; }).join("") + "</dl></div>" +
      (c.verify_notes ? '<div class="panel fam-seek"><b>' + t("cVerifyNote") + "：</b>" + esc(c.verify_notes) + "</div>" : "") +
      '<h3 class="section-title">' + t("cSpeakers") + "</h3>" + ((c.speakers || []).length ? c.speakers.map(speakerBlock).join("") : '<div class="status-line">' + t("cNoSpeakers") + "</div>");
    app.innerHTML = '<div class="detail-page"><p style="margin-top:16px"><a href="#/conferences" id="back">' + t("back") + '</a></p><div class="fam-detail">' + main + "</div>" + '<p class="fam-disclaimer">' + t("cNote") + "</p></div>";
    document.getElementById("back").addEventListener("click", goBack);
    window.scrollTo(0, 0);
  }
  document.addEventListener("click", function (e) {
    var ch = e.target.closest("[data-conf], [data-fam^='c:']");
    if (!ch) return;
    e.stopPropagation();
    var k = ch.getAttribute("data-conf") || ch.getAttribute("data-fam").slice(2), v = ch.getAttribute("data-v") || null;
    if (k === "online") cState.online = !cState.online; else if (k === "when") cState.when = v; else cState[k] = cState[k] === v ? null : v;
    renderConferences();
  }, true);

  // ---------- 動向：AI 名人／心理大師 ----------
  var FSTR = {
    zh: { navFig: "動向", fTitle: "名人動向", fSub: "AI 領域與臨床心理領域代表人物的最新動態與發言。只收錄本人帳號、官方頁面或其親自接受的訪談，附原文連結；名單職位與帳號持續核對，查不到的標「待查證」。",
      fAi: "AI 名人動向", fPsy: "心理大師動向", fAllP: "全部人物", fUpdates: "最新動態", fRoster: "人物名單", fNoUp: "尚未有動態收錄，待 Muse 首次整理後出現。",
      fSrc: "原文 ↗", fVerified: "帳號已核對", fUnverified: "帳號待查證", fAcc: "帳號", fNote: "動態內容為摘要與短引述，版權屬原作者；請以原文為準。名單來自 Gu 提供的清單，職位可能已變動。" },
    en: { navFig: "Voices", fTitle: "Voices", fSub: "Latest activity and statements from leading figures in AI and clinical psychology, from their own accounts, official pages or interviews, with source links. Roster positions and accounts are verified on a rolling basis.",
      fAi: "AI voices", fPsy: "Clinical voices", fAllP: "Everyone", fUpdates: "Latest", fRoster: "Roster", fNoUp: "No updates yet; they appear after Muse's first run.",
      fSrc: "Source ↗", fVerified: "Account verified", fUnverified: "Account unverified", fAcc: "Accounts", fNote: "Updates are summaries and short quotes; copyright belongs to the authors. Positions may have changed since the roster was compiled." }
  };
  Object.keys(FSTR).forEach(function (l) { Object.keys(FSTR[l]).forEach(function (k) { STR[l][k] = FSTR[l][k]; }); });
  var FIG = null, fState = { grp: "ai", person: null };
  function loadFig() {
    if (FIG) return Promise.resolve(FIG);
    return getJSON("data/figures.json").then(function (d) { FIG = d; return d; });
  }
  function figName(p) { return p.name_zh && p.name_zh !== p.name_en ? p.name_en + "（" + p.name_zh + "）" : p.name_en; }
  function figUpdateCard(u, p) {
    return '<article class="card fam-card"><div class="card-author"><span class="cat-avatar fam-avatar" aria-hidden="true">' + esc((p ? p.name_en : "?").charAt(0)) + "</span>" +
      '<div class="card-author-names"><span class="card-author-name">' + esc(p ? figName(p) : u.person) + "</span><time>" + esc(u.page_date || "") + (u.platform ? " · " + esc(u.platform) : "") + "</time></div></div>" +
      '<p class="card-summary">' + esc(u.summary_zh) + "</p>" +
      (u.quote_en ? '<blockquote class="conf-note">“' + esc(u.quote_en) + "”</blockquote>" : "") +
      '<div class="card-meta">' + (u.kind ? '<span class="badge">' + esc(u.kind) + "</span>" : "") + (u.topics || []).slice(0, 3).map(function (x) { return '<span class="badge">' + esc(x) + "</span>"; }).join("") +
      (safeUrl(u.url) ? ' <a class="chip" href="' + esc(u.url) + '" target="_blank" rel="noopener noreferrer">' + t("fSrc") + "</a>" : "") + "</div></article>";
  }
  function figPersonCard(p) {
    var accs = (p.accounts || []).filter(function (a) { return safeUrl(a.url); }).map(function (a) {
      return '<a class="chip" href="' + esc(a.url) + '" target="_blank" rel="noopener noreferrer">' + esc(a.platform) + (a.verified ? " ✓" : "") + "</a>";
    }).join(" ");
    return '<article class="card fam-card"><h3 class="card-title"><a href="#" data-fig="person" data-v="' + esc(p.slug) + '">' + esc(figName(p)) + "</a></h3>" +
      '<div class="training-line">' + esc(p.role_zh) + "</div><p class=\"card-summary\">" + esc(p.focus_zh) + "</p>" +
      (p.list_note ? '<p class="conf-note">' + esc(p.list_note) + "</p>" : "") +
      '<div class="card-meta"><span class="badge ' + (p.verified_by_muse ? "badge-free" : "badge-warn") + '">' + (p.verified_by_muse ? t("fVerified") : t("fUnverified")) + "</span> " + accs + "</div></article>";
  }
  function renderFigures() {
    var people = FIG.people.filter(function (p) { return p.group === fState.grp; });
    var by = {}; FIG.people.forEach(function (p) { by[p.slug] = p; });
    var ups = (FIG.updates || []).filter(function (u) { return by[u.person] && by[u.person].group === fState.grp && (!fState.person || u.person === fState.person); })
      .sort(function (a, b) { return (a.page_date || "") < (b.page_date || "") ? 1 : -1; });
    var shown = fState.person ? people.filter(function (p) { return p.slug === fState.person; }) : people;
    app.innerHTML = '<h2 class="page-title">' + t("fTitle") + '</h2><p class="page-sub">' + t("fSub") + '</p><div class="toolbar"><div class="chip-row">' +
      '<button class="chip' + (fState.grp === "ai" ? " on" : "") + '" data-fig="grp" data-v="ai">' + t("fAi") + "</button>" +
      '<button class="chip' + (fState.grp === "psy" ? " on" : "") + '" data-fig="grp" data-v="psy">' + t("fPsy") + "</button>" +
      (fState.person ? '<button class="chip on" data-fig="person" data-v="">' + t("fAllP") + " ✕</button>" : "") + "</div></div>" +
      '<h3 class="section-title">' + t("fUpdates") + "</h3>" +
      (ups.length ? '<div class="masonry">' + ups.map(function (u) { return figUpdateCard(u, by[u.person]); }).join("") + "</div>" : '<div class="status-line">' + t("fNoUp") + "</div>") +
      '<h3 class="section-title">' + t("fRoster") + "（" + shown.length + "）</h3>" +
      '<div class="masonry">' + shown.map(figPersonCard).join("") + "</div>" +
      '<p class="fam-disclaimer">' + t("fNote") + "</p>";
  }
  document.addEventListener("click", function (e) {
    var ch = e.target.closest("[data-fig]");
    if (!ch) return;
    e.preventDefault(); e.stopPropagation();
    var k = ch.getAttribute("data-fig"), v = ch.getAttribute("data-v") || null;
    if (k === "grp") { fState.grp = v; fState.person = null; } else fState.person = v;
    renderFigures(); afterRender(); window.scrollTo(0, 0);
  }, true);

  // ---------- 外框、路由 ----------
  function applyChrome() {
    document.documentElement.lang = prefs.lang === "en" ? "en" : "zh-Hant";
    document.querySelectorAll("[data-t]").forEach(function (el) { el.textContent = t(el.getAttribute("data-t")); });
    document.getElementById("lang-toggle").textContent = t("langLabel");
    renderSupport();
    document.title = t("appName") + (prefs.lang === "en" ? "" : " PsyPick");
    var c = DATA ? DATA.config : { half_life_days: 14, featured_min_score: 4, featured_top_n: 8 };
    document.getElementById("help-pop").innerHTML = "<b>" + t("helpTitle") + "</b><dl>" +
      "<dt>" + t("heat") + "</dt><dd>" + esc(t("helpHeat", { d: c.half_life_days, m: c.featured_min_score, n: c.featured_top_n })) + "</dd>" +
      "<dt>" + esc(t("collection", { n: "N" })) + "</dt><dd>" + esc(t("helpCollection")) + "</dd>" +
      "<dt>" + t("evidence") + " E0–E4</dt><dd>" + esc(t("helpEvidence")) + "</dd>" +
      "<dt>" + t("verify") + "</dt><dd>" + esc(t("helpVerify")) + "</dd></dl>";
  }
  // ---------- 返回、捲動位置、每次渲染後的整理 ----------
  var navCount = 0, linkNav = false, scrollMem = {}, pendingY = null;
  function goBack(e) { if (navCount > 0) { e.preventDefault(); linkNav = false; history.back(); } }
  document.addEventListener("click", function (e) { var a = e.target.closest && e.target.closest('a[href^="#"]'); if (a) linkNav = true; }, true);
  window.addEventListener("hashchange", function (e) {
    navCount++;
    try { scrollMem[new URL(e.oldURL).hash || "#/"] = window.scrollY; } catch (x) { /* ignore */ }
    pendingY = linkNav ? 0 : (scrollMem[location.hash || "#/"] || 0);
    linkNav = false;
    route();
  });
  function layoutMasonry() {
    document.querySelectorAll("#app .masonry").forEach(function (m) {
      var n = Math.max(1, Math.min(3, Math.floor((m.clientWidth + 14) / 314)));
      var laid = m.hasAttribute("data-cols");
      if (laid ? m.getAttribute("data-cols") === String(n) : n === 1) return;
      var items = laid ? [].slice.call(m.querySelectorAll(":scope > .mcol > [data-mi]")) : [].slice.call(m.children);
      if (laid) items.sort(function (a, b) { return a.getAttribute("data-mi") - b.getAttribute("data-mi"); });
      else items.forEach(function (el, i) { el.setAttribute("data-mi", i); });
      m.innerHTML = "";
      if (n === 1) { m.classList.remove("mlaid"); m.removeAttribute("data-cols"); items.forEach(function (el) { m.appendChild(el); }); return; }
      m.classList.add("mlaid"); m.setAttribute("data-cols", n);
      var cols = []; for (var i = 0; i < n; i++) { cols.push(document.createElement("div")); cols[i].className = "mcol"; m.appendChild(cols[i]); }
      items.forEach(function (el) {
        var c = cols.reduce(function (a, b) { return b.offsetHeight < a.offsetHeight ? b : a; });
        c.appendChild(el);
      });
    });
  }
  function afterRender() {
    layoutMasonry();
    document.querySelectorAll("#app button.chip").forEach(function (b) { b.setAttribute("aria-pressed", b.classList.contains("on")); });
    document.querySelectorAll("#app .fam-tabs a").forEach(function (a) { if (a.classList.contains("on")) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current"); });
    var h2 = document.querySelector("#app h2"), base = prefs.lang === "en" ? t("appName") : t("appName") + " PsyPick";
    var name = h2 && (location.hash || "#/") !== "#/" ? h2.textContent.trim() : "";
    document.title = name ? name.slice(0, 60) + " · " + t("appName") : base;
  }
  var afterQueued = false;
  new MutationObserver(function () {
    if (afterQueued) return; afterQueued = true;
    requestAnimationFrame(function () { afterQueued = false; afterRender(); });
  }).observe(document.getElementById("app"), { childList: true, subtree: true });
  var resizeT = null;
  window.addEventListener("resize", function () { clearTimeout(resizeT); resizeT = setTimeout(layoutMasonry, 150); });
  function closePopups() {
    var nav = document.getElementById("site-nav"), pop = document.getElementById("help-pop");
    nav.classList.remove("open"); document.getElementById("nav-toggle").setAttribute("aria-expanded", "false");
    pop.hidden = true; document.getElementById("help-btn").setAttribute("aria-expanded", "false");
  }
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closePopups(); });
  document.addEventListener("click", function (e) { if (!e.target.closest(".site-header")) closePopups(); });

  function route() {
    var h = location.hash.replace(/^#/, "") || "/";
    var y = pendingY === null ? window.scrollY : pendingY; pendingY = null;
    document.querySelectorAll(".header-nav a").forEach(function (a) {
      var href = a.getAttribute("href");
      var on = href === "#" + h || (href === "#/family" && h.indexOf("/family") === 0) || (href === "#/bounty" && h.indexOf("/bounty") === 0) || (href === "#/conferences" && h.indexOf("/conferences") === 0) || (href === "#/figures" && h.indexOf("/figures") === 0);
      a.classList.toggle("active", on);
      if (on) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
    closePopups();
    loadIndex().then(function () {
      applyChrome();
      if (h.indexOf("/figures") === 0) return loadFig().then(renderFigures);
      var cm = h.match(/^\/conferences(?:\/(.+))?$/);
      if (cm) return loadConf().then(function () { return cm[1] ? renderConference(decodeURIComponent(cm[1])) : renderConferences(); });
      var bm = h.match(/^\/bounty(?:\/(.+))?$/);
      if (bm) return loadFamily().then(function () { return bm[1] ? renderBountyItem(decodeURIComponent(bm[1])) : renderBounty(); });
      var fm = h.match(/^\/family(?:\/(.*))?$/);
      if (fm) return renderFamily(fm[1] || "");
      var m = h.match(/^\/case\/(.+)$/);
      if (m) return renderCase(decodeURIComponent(m[1]));
      if (h === "/featured") return renderFeatured();
      if (h === "/training") return renderTraining();
      if (h === "/saved") return renderSaved();
      renderHome();
    }).then(function () {
      requestAnimationFrame(function () { afterRender(); window.scrollTo(0, y); });
    }).catch(function () {
      app.innerHTML = '<div class="status-line">' + t("loadError") + ' <button class="lang-toggle" id="retry">' + t("retry") + "</button></div>";
      document.getElementById("retry").addEventListener("click", function () { DATA = null; route(); });
    });
  }

  document.addEventListener("click", function (e) {
    var fav = e.target.closest("[data-fav]");
    if (fav) {
      e.preventDefault();
      var slug = fav.getAttribute("data-fav"); toggleFav(slug);
      var on = isFav(slug);
      document.querySelectorAll("[data-fav]").forEach(function (b) {
        if (b.getAttribute("data-fav") !== slug) return;
        b.setAttribute("aria-pressed", on);
        b.textContent = b.hasAttribute("data-labeled") ? (on ? "★ " + t("saved") : "☆ " + t("save")) : (on ? "★" : "☆");
      });
      if (location.hash === "#/saved") renderSaved();
      return;
    }
    var chip = e.target.closest("[data-cat]");
    if (chip) { homeState.cat = chip.getAttribute("data-cat") || null; renderHome(); }
    var cp = e.target.closest("[data-copy]");
    if (cp) {
      var code = cp.getAttribute("data-copy"), done = function () { cp.textContent = t("famCopied"); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(code).then(done, function () {});
      else { var ta = document.createElement("textarea"); ta.value = code; document.body.appendChild(ta); ta.select(); try { document.execCommand("copy"); done(); } catch (x) { /* ignore */ } ta.remove(); }
      return;
    }
    var fchip = e.target.closest("[data-fam]");
    if (fchip) {
      var fk = fchip.getAttribute("data-fam"), fv = fchip.getAttribute("data-v") || null;
      if (fk.indexOf("b:") === 0) {
        var bk = fk.slice(2);
        if (bk === "sure" || bk === "online") bState[bk] = !bState[bk]; else bState[bk] = bState[bk] === fv ? null : fv;
        renderBounty(); return;
      }
      if (fk === "free") famState.free = !famState.free; else famState[fk] = famState[fk] === fv ? null : fv;
      if (location.hash === "#/family/read") renderFamilyRead(); else renderFamilyEvents();
      return;
    }
    var fage = e.target.closest("[data-fam-age]");
    if (fage) { famState.age = fage.getAttribute("data-fam-age"); famState.topic = null; famState.region = null; famState.q = ""; }
    var dchip = e.target.closest("[data-dom]");
    if (dchip) { var dn = dchip.getAttribute("data-dom"); homeState.dom = homeState.dom === dn ? null : dn; renderHome(); }
  });
  // ---------- 贊助按鈕：網址放在 support.json，沒填就不顯示 ----------
  var SUPPORT = null;
  function renderSupport() {
    var a = document.getElementById("nav-support"), note = document.getElementById("support-note");
    if (!SUPPORT || !/^https:\/\//i.test(SUPPORT.url || "")) { a.hidden = true; note.hidden = true; return; }
    var en = prefs.lang === "en", label = en ? SUPPORT.label_en : SUPPORT.label_zh;
    a.href = SUPPORT.url; a.innerHTML = '☕ <span class="sup-label">' + esc(label || "") + "</span>"; a.title = label || ""; a.setAttribute("aria-label", label || "☕"); a.hidden = false;
    var n = en ? SUPPORT.note_en : SUPPORT.note_zh;
    note.innerHTML = n ? esc(n) + ' <a href="' + esc(SUPPORT.url) + '" target="_blank" rel="noopener noreferrer">☕ ' + esc(label || "") + "</a>" : "";
    note.hidden = !n;
  }
  getJSON("support.json").then(function (d) { SUPPORT = d; renderSupport(); }, function () { /* 沒有檔案就不顯示 */ });
  document.getElementById("lang-toggle").addEventListener("click", function () { prefs.lang = prefs.lang === "zh" ? "en" : "zh"; persist(); route(); });
  document.getElementById("help-btn").addEventListener("click", function () {
    var pop = document.getElementById("help-pop"), open = pop.hidden; pop.hidden = !open; this.setAttribute("aria-expanded", open);
  });
  document.getElementById("nav-toggle").addEventListener("click", function () {
    var nav = document.getElementById("site-nav"); nav.classList.toggle("open"); this.setAttribute("aria-expanded", nav.classList.contains("open"));
  });
  route();
})();
