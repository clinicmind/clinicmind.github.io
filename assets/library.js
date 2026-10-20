// 深度閱讀心理學首頁：搜尋時展開章節清單，清空搜尋時收合。只在瀏覽器執行，不送出資料。
(function () {
    var q = document.getElementById("lib-q");
    if (!q) return;
    var lists = document.querySelectorAll(".lib-ch-wrap");
    try {
        q.addEventListener("input", function () {
            var open = q.value.trim().length > 0;
            Array.prototype.forEach.call(lists, function (d) { d.open = open; });
        });
    } catch (e) { /* 舊瀏覽器：保持預設收合 */ }
})();
