/* 閱讀進度（規劃 8.5 第 2 項）。只存在讀者瀏覽器，key：cm-read-<slug>。 */
(function () {
  "use strict";
  function read(slug) {
    try { return JSON.parse(localStorage.getItem("cm-read-" + slug)) || []; }
    catch (e) { return []; }
  }
  function write(slug, list) {
    try { localStorage.setItem("cm-read-" + slug, JSON.stringify(list)); } catch (e) { /* 無法保存時只在本頁有效 */ }
  }

  // 章節頁：「我讀完了」按鈕
  document.querySelectorAll("[data-read-btn]").forEach(function (btn) {
    var slug = btn.getAttribute("data-book"), unit = btn.getAttribute("data-unit");
    var list = read(slug);
    function paint() {
      var done = read(slug).indexOf(unit) !== -1;
      btn.setAttribute("aria-pressed", done ? "true" : "false");
      btn.textContent = done ? "✓ 已標記讀完（再按可取消）" : "我讀完了";
    }
    btn.addEventListener("click", function () {
      var cur = read(slug), i = cur.indexOf(unit);
      if (i === -1) cur.push(unit); else cur.splice(i, 1);
      write(slug, cur);
      paint();
    });
    paint();
  });

  // 書頁：章節 ✓、進度條、全部讀完時提示測驗
  var map = document.querySelector("[data-book-map]");
  if (map) {
    var slug = map.getAttribute("data-book-map");
    var total = map.querySelectorAll("li[data-unit]").length;
    var done = read(slug);
    map.querySelectorAll("li[data-unit]").forEach(function (li) {
      if (done.indexOf(li.getAttribute("data-unit")) !== -1) li.classList.add("is-read");
    });
    var count = map.querySelectorAll("li.is-read").length;
    var bar = document.getElementById("book-progress");
    if (bar) {
      bar.max = total; bar.value = count;
      var label = document.getElementById("book-progress-text");
      if (label) label.textContent = "已標記讀完 " + count + " ／ " + total + " 章";
    }
    var tip = document.getElementById("book-quiz-tip");
    if (tip && count === total && total > 0) tip.hidden = false;
  }
})();
