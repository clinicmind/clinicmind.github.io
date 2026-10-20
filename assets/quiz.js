/* 全書 15 題測驗（規劃 8.3）。全部在瀏覽器執行，不送出任何資料。 */
(function () {
  "use strict";
  var root = document.getElementById("quiz");
  var dataEl = document.getElementById("quiz-data");
  if (!root || !dataEl) return;
  var D = JSON.parse(dataEl.textContent);
  var KEY = "cm-quiz-" + D.slug;
  var live = document.getElementById("quiz-live");
  var form = document.getElementById("quiz-form");
  var resultBox = document.getElementById("quiz-result");
  var list = document.getElementById("quiz-list");

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || { passed: [] }; }
    catch (e) { return { passed: [] }; }
  }
  function save(s) { try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (e) { /* 無法保存時照常作答 */ } }
  function shuffle(a) {
    for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; }
    return a;
  }
  function sha(text) {
    return crypto.subtle.digest("SHA-256", new TextEncoder().encode(text)).then(function (buf) {
      return Array.from(new Uint8Array(buf)).map(function (b) { return b.toString(16).padStart(2, "0"); }).join("");
    });
  }
  function el(tag, attrs, text) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (text != null) n.textContent = text;
    return n;
  }

  var state = load();
  var wrong = {};
  var order = shuffle(D.questions.slice());
  var passed = {};
  state.passed.forEach(function (id) { passed[id] = true; });

  function render() {
    list.textContent = "";
    order.forEach(function (q, idx) {
      var fs = el("fieldset", { "class": "quiz-q", "data-qid": q.id });
      var lg = el("legend", {}, "第 " + (idx + 1) + " 題：" + q.stem);
      fs.appendChild(lg);
      if (passed[q.id]) {
        fs.classList.add("is-passed");
        fs.appendChild(el("p", { "class": "quiz-ok" }, "✓ 已答對"));
      } else {
        shuffle(q.options.slice()).forEach(function (opt, oi) {
          var id = "q-" + q.id + "-" + oi;
          var wrap = el("div", { "class": "quiz-opt" });
          wrap.appendChild(el("input", { type: "radio", name: "q-" + q.id, id: id, value: opt }));
          wrap.appendChild(el("label", { "for": id }, opt));
          fs.appendChild(wrap);
        });
        var hint = el("div", { "class": "quiz-hint", hidden: "" });
        if (wrong[q.id]) hint.hidden = false;
        hint.id = "hint-" + q.id;
        var link = el("a", { href: "/library/" + D.slug + "/" + q.unit + ".html#" + q.section }, "回到相關段落");
        hint.appendChild(el("p", {}, "提醒：" + q.hint));
        hint.appendChild(el("p", {}, "")).appendChild(link);
        fs.appendChild(hint);
      }
      list.appendChild(fs);
    });
  }

  function say(msg) { if (live) live.textContent = msg; }

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var jobs = [];
    order.forEach(function (q) {
      if (passed[q.id]) return;
      var sel = form.querySelector('input[name="q-' + q.id + '"]:checked');
      if (!sel) return;
      jobs.push(sha(D.slug + "|" + q.id + "|" + sel.value).then(function (h) {
        return { q: q, ok: h.slice(0, 12) === q.key };
      }));
    });
    if (!jobs.length) { say("請先為未答的題目選一個選項。"); return; }
    Promise.all(jobs).then(function (res) {
      res.forEach(function (r) {
        if (r.ok) {
          passed[r.q.id] = true;
          state.passed.push(r.q.id);
        } else {
          wrong[r.q.id] = true;
        }
      });
      save(state);
      order.forEach(function (q) { if (passed[q.id]) delete wrong[q.id]; });
      var count = Object.keys(passed).length;
      say("這次交卷：答對 " + res.filter(function (r) { return r.ok; }).length + " 題。目前共答對 " + count + " 題，全部 " + D.questions.length + " 題。");
      render();
      finish(count);
    });
  });

  function finish(count) {
    if (count < D.questions.length) return;
    resultBox.hidden = false;
    resultBox.textContent = "";
    resultBox.appendChild(el("h2", {}, "15 題全部答對"));
    resultBox.appendChild(el("p", {}, "以下是每題的解說（附原書頁碼）。"));
    var ol = el("ol", {});
    D.questions.forEach(function (q) { ol.appendChild(el("li", {}, q.explain)); });
    resultBox.appendChild(ol);
    document.getElementById("cert-start").hidden = false;
  }

  document.getElementById("cert-start").addEventListener("click", function () {
    document.getElementById("cert-form").hidden = false;
    document.getElementById("cert-name").focus();
  });
  document.getElementById("cert-form").addEventListener("submit", function (ev) {
    ev.preventDefault();
    var name = document.getElementById("cert-name").value.trim();
    if (!name) { say("請輸入名字。"); return; }
    window.CERT.render(document.getElementById("cert-out"), { name: name.slice(0, 40), data: D });
    document.getElementById("cert-out").hidden = false;
    document.getElementById("cert-out").scrollIntoView({ behavior: "smooth", block: "start" });
  });

  render();
  finish(Object.keys(passed).length);
  if (Object.keys(passed).length) say("您已答對 " + Object.keys(passed).length + " 題（已保存在此瀏覽器）。");
})();
