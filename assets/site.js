// 手機版選單開合
(function () {
    var btn = document.querySelector(".nav-toggle");
    var nav = document.getElementById("site-nav");
    if (!btn || !nav) return;
    btn.addEventListener("click", function () {
        var open = nav.classList.toggle("open");
        btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.addEventListener("click", function (ev) {
        if (ev.target.tagName === "A") { nav.classList.remove("open"); btn.setAttribute("aria-expanded", "false"); }
    });
})();

// 連結指向收合的區塊（例如自我評量）時，自動展開
(function () {
    function openTarget() {
        var id = decodeURIComponent(location.hash.slice(1));
        var el = id && document.getElementById(id);
        if (el && el.tagName === "DETAILS") el.open = true;
    }
    openTarget();
    window.addEventListener("hashchange", openTarget);
})();
