# 臨床心語 ClinicMind 網站

<https://clinicmind.github.io/> 的原始碼。純靜態 HTML，由 GitHub Pages 直接發布 `main` 分支，沒有建置步驟：合併到 `main` 就會上線。

## 目錄結構

```
.
├── index.html            首頁（樣式寫在頁內 <style>）
├── about.html            關於與資格
├── faq.html              常見問題（含 FAQ 結構化資料，改問答時要同步 JSON-LD）
├── articles.html         文章列表；也是書房頁首、頁尾的來源（見下方）
├── anfang*.html          「安放」系列文章（三篇各自獨立）
├── *.html                其他文章與主題頁（trauma、eft、ipt、family、addiction…）
├── resources.html        自助資源與即時求助專線
├── 404.html              找不到頁面
├── assets/
│   ├── site.css          全站共用樣式與品牌色票、字體（檔尾 brand 區塊）
│   ├── pages.css         內頁樣式
│   ├── library.css       深度閱讀心理學（書房）樣式
│   ├── site.js           手機版選單
│   ├── finder.js         頁內搜尋與篩選
│   ├── library.js / progress.js / quiz.js / certificate.js   書房功能，全部在瀏覽器執行
│   ├── favicon.svg, og-image.png
│   └── brand/            logo、favicon、apple-touch-icon
├── library/              深度閱讀心理學：由 tools/library/build.py 產生，不要手改
├── tools/library/        書房產生器
│   ├── build.py          主程式
│   ├── quiz.py           全書 15 題測驗的解析與出題規則
│   ├── config.json       書目分類與排序
│   └── vendor/           複製自 clinicmind/clinicmind pipeline/，不要在這裡修改
├── sitemap.xml           網站地圖
├── llms.txt              給 AI 搜尋引擎的網站摘要
└── robots.txt
```

## 本地預覽

頁面用的是以 `/` 開頭的絕對路徑，請從 repo 根目錄啟動伺服器，不要直接雙擊開檔：

```bash
python3 -m http.server 8000
# 瀏覽 http://localhost:8000/
```

## 產生書房（深度閱讀心理學）

`library/` 的內容來自筆記 repo `clinicmind/clinicmind`。需要 Python 3（只用標準函式庫）和 git。

```bash
# 1. 取得筆記 repo（需要所有分支，build.py 會為每本書挑最新的分支）
git clone https://github.com/clinicmind/clinicmind /path/to/clinicmind

# 2. 在本 repo 根目錄執行
python3 tools/library/build.py --notes /path/to/clinicmind

# 只重建一本書
python3 tools/library/build.py --notes /path/to/clinicmind --only psychopathology-maddux

# 指定檢查報告位置（預設 /tmp/library-report.txt）
python3 tools/library/build.py --notes /path/to/clinicmind --report report.txt
```

- 只會寫入 `library/`、`sitemap.xml`、`llms.txt`。
- 書必須列在 `tools/library/config.json`，而且在筆記 repo 中已完成（有學術版 PDF，或 `book.json` 的 `complete` 為 true）才會產生。
- 頁首與頁尾取自 `articles.html`，改了主選單或頁尾後要重跑一次。
- 任何自動檢查失敗時結束碼為 1，詳情看報告。

### 全書測驗

測驗不需要另外下指令：書的資料夾裡有 `quiz.md`，`build.py` 就會用 `quiz.py` 檢查出題規則，通過才產生 `library/<書>/quiz.html`；沒通過時書照常上線，原因寫在報告裡。答案只以雜湊值存在頁面中，靜態網站無法真正隱藏答案。

## 改動時要注意

- 新增或刪除頁面時，同步更新 `sitemap.xml` 與 `llms.txt`。
- 每頁都要有 `<title>`、`meta description`、canonical 與 OpenGraph 標籤。
- 網站用語為台港繁體中文，稱呼讀者用「您」。
- 品牌色票與字體集中在 `assets/site.css` 檔尾，不要在各頁另外覆寫。
