/* 閱讀完成證明（規劃 8.4）。名字只在本頁產生，不送出、不記錄。 */
(function () {
  "use strict";
  var STATEMENT = "本證明表示持有人已讀完本書的學習筆記，並通過 15 題理解測驗。本證明不是學分、執照或專業認證。";

  function today() {
    var d = new Date();
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  }
  function code(name, slug, date) {
    return crypto.subtle.digest("SHA-256", new TextEncoder().encode(name + slug + date)).then(function (buf) {
      return Array.from(new Uint8Array(buf)).map(function (b) { return b.toString(16).padStart(2, "0"); }).join("").slice(0, 8).toUpperCase();
    });
  }
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function render(container, opts) {
    var D = opts.data, date = today();
    container.textContent = "";
    var sheet = el("div", "cert-sheet");
    sheet.id = "cert-print";
    sheet.appendChild(el("p", "cert-kicker", "臨床心語 ClinicMind｜深度閱讀心理學"));
    sheet.appendChild(el("h2", "cert-title", "閱讀完成證明"));
    sheet.appendChild(el("p", "cert-name", opts.name));
    sheet.appendChild(el("p", "cert-book", "《" + D.title + "》"));
    sheet.appendChild(el("p", "cert-en", D.en));
    sheet.appendChild(el("p", "cert-meta", "全書 " + D.chapters + " 章｜完成日期 " + date));
    sheet.appendChild(el("p", "cert-statement", STATEMENT));
    var foot = el("p", "cert-foot", "驗證碼 ");
    var codeEl = el("span", "cert-code", "……");
    foot.appendChild(codeEl);
    foot.appendChild(el("span", "", "｜ 驗證碼只用於核對證明上的資料，不能防偽。"));
    sheet.appendChild(foot);
    sheet.appendChild(el("p", "cert-url", "clinicmind.github.io/library/" + D.slug + "/"));
    container.appendChild(sheet);
    code(opts.name, D.slug, date).then(function (c) { codeEl.textContent = c; opts.code = c; });

    var bar = el("div", "cert-actions");
    var pr = el("button", "btn", "列印／存成 PDF（A4）");
    pr.type = "button";
    pr.addEventListener("click", function () { window.print(); });
    var dl = el("button", "btn btn-ghost", "下載分享圖（PNG）");
    dl.type = "button";
    dl.addEventListener("click", function () { drawPng(opts, date, dl); });
    bar.appendChild(pr);
    bar.appendChild(dl);
    container.appendChild(bar);
    container.appendChild(el("p", "cert-note", "名字只存在您目前的瀏覽器頁面中，不會傳到網站。離開或重新整理後需要重新輸入。"));
  }

  function drawPng(opts, date, btn) {
    var D = opts.data;
    var c = document.createElement("canvas");
    c.width = 1080; c.height = 1350;
    var g = c.getContext("2d");
    var font = "'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', system-ui, sans-serif";
    g.fillStyle = "#F7F5F0"; g.fillRect(0, 0, 1080, 1350);
    g.fillStyle = "#6B8E88"; g.fillRect(0, 0, 1080, 18);
    g.textAlign = "center"; g.fillStyle = "#2F3B3A";
    g.font = "500 36px " + font; g.fillText("臨床心語 ClinicMind｜深度閱讀心理學", 540, 150);
    g.font = "700 96px " + font; g.fillText("閱讀完成證明", 540, 330);
    g.font = "700 88px " + font; g.fillText(opts.name, 540, 540);
    g.font = "500 52px " + font; g.fillText("《" + D.title + "》", 540, 660);
    var enSize = 36;
    do { g.font = "400 " + enSize + "px " + font; enSize -= 2; } while (g.measureText(D.en).width > 960 && enSize > 18);
    g.fillStyle = "#5A6967"; g.fillText(D.en, 540, 720);
    g.fillText("全書 " + D.chapters + " 章｜完成日期 " + date, 540, 800);
    g.font = "400 36px " + font;
    var words = "本證明表示持有人已讀完本書的學習筆記，並通過 15 題理解測驗。本證明不是學分、執照或專業認證。";
    var line = "", y = 920;
    for (var i = 0; i < words.length; i++) {
      var t = line + words[i];
      if (g.measureText(t).width > 880) { g.fillText(line, 540, y); line = words[i]; y += 58; }
      else line = t;
    }
    g.fillText(line, 540, y);
    g.font = "500 40px " + font; g.fillStyle = "#2F3B3A";
    g.fillText("驗證碼 " + (opts.code || ""), 540, 1130);
    g.font = "400 34px " + font; g.fillStyle = "#5A6967";
    g.fillText("clinicmind.github.io/library/" + D.slug + "/", 540, 1220);
    c.toBlob(function (blob) {
      var a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "閱讀完成證明-" + D.slug + ".png";
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
    }, "image/png");
  }

  window.CERT = { render: render };
})();
