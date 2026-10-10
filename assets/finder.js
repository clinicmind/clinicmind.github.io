// 本頁搜尋與篩選：只在瀏覽器裡比對文字，不寫入網址、不送出、不記錄
(function () {
    document.querySelectorAll("[data-finder]").forEach(function (box) {
        var items = Array.prototype.slice.call(document.querySelectorAll(box.dataset.items));
        var groups = Array.prototype.slice.call(document.querySelectorAll(box.dataset.groups));
        var q = box.querySelector("input[type=search]");
        var topic = box.querySelector("select[data-topic]");
        var audBtns = box.querySelectorAll("button[data-aud]");
        var count = box.querySelector("[data-count]");
        var empty = box.querySelector("[data-empty]");
        var aud = "all", timer = null;
        if (!items.length || !q) return;
        box.hidden = false;
        var norm = function (t) { return (t || "").toLowerCase().replace(/\s+/g, ""); };
        items.forEach(function (it) { it._text = norm(it.textContent + " " + (it.dataset.alias || "")); });
        if (topic) groups.forEach(function (g) {
            var h = g.querySelector("h2");
            if (!h || !g.querySelector(box.dataset.items.split(" ").pop())) return;
            var o = document.createElement("option"); o.value = g.id; o.textContent = h.textContent; topic.appendChild(o);
        });
        function apply(announce) {
            var words = norm(q.value) ? q.value.toLowerCase().split(/\s+/).filter(Boolean) : [];
            var t = topic ? topic.value : "";
            var shown = 0;
            items.forEach(function (it) {
                var g = it.closest(box.dataset.groups);
                var ok = words.every(function (w) { return it._text.indexOf(w) !== -1; })
                    && (!t || (g && g.id === t))
                    && (aud === "all" || (it.dataset.audience || "public") === aud);
                it.hidden = !ok;
                if (ok) shown++;
            });
            groups.forEach(function (g) {
                var inside = g.querySelectorAll(box.dataset.items.split(" ").pop());
                if (!inside.length) return;
                var any = Array.prototype.some.call(inside, function (i) { return !i.hidden; });
                g.hidden = !any;
            });
            var filtering = words.length || t || aud !== "all";
            empty.hidden = !(filtering && shown === 0);
            if (announce) count.textContent = filtering ? "找到 " + shown + " 項" : "";
        }
        q.addEventListener("input", function () { apply(false); clearTimeout(timer); timer = setTimeout(function () { apply(true); }, 600); });
        if (topic) topic.addEventListener("change", function () { apply(true); });
        Array.prototype.forEach.call(audBtns, function (b) {
            b.addEventListener("click", function () {
                aud = b.dataset.aud;
                Array.prototype.forEach.call(audBtns, function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
                apply(true);
            });
        });
        box.querySelector("[data-clear]").addEventListener("click", function () {
            q.value = ""; if (topic) topic.value = ""; aud = "all";
            Array.prototype.forEach.call(audBtns, function (x) { x.setAttribute("aria-pressed", x.dataset.aud === "all" ? "true" : "false"); });
            apply(true); q.focus();
        });
    });
})();
