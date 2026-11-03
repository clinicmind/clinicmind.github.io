# EF 教學工作室 — Hill · Skill · Will

以 Lynn Meltzer（編，2018）《Executive Function in Education: From Theory to Practice》（第二版）作理論基礎，為澳門及繁體中文學校教師設計的免費、靜態網站。

## 啟動

直接開啟 `index.html`，或使用任何靜態 HTTP 伺服器（例如：`python -m http.server 8000` 後進入 `http://localhost:8000/`）。無需登入、資料庫或付費 API。

## 教師流程

1. 複製課文，或上載 TXT、MD、HTML、DOCX、有文字層的 PDF。
2. 設定學科／學段、學習目標及關鍵概念，選擇鷹架程度。
3. 產生可直接編輯的半完成筆記、Hill–Skill–Will 工作紙及教師答案。
4. 核對填空詞、題目、原文依據及課程目標；按需要調整。
5. 透過列印按鈕儲存 PDF，或匯出 Word 相容 `.doc`／獨立 HTML。

## 工作原理及限制

- **不使用大型語言模型。** 程式在瀏覽器內按規則擷取課文句子與候選關鍵詞，生成填空及原文依據；絕不宣稱完成自然語言語意理解、真偽判斷或客製化診斷。
- **不傳送課文到伺服器。** 原始文字只在本機記憶體處理，不寫入本機儲存空間或網站後端。DOCX 解析使用隨站提供的 JSZip；PDF 解析於需要時從 Cloudflare CDN 載入 pdf.js 程式碼（PDF 本身仍在瀏覽器本機解析）。如 CDN 連線失敗可改用複製貼上或 TXT/DOCX。
- 不支援 OCR、上鎖文件、影像掃描 PDF。無法處理複雜數學排版或表格原有位置；內容需人工審閱。
- 學生身分資料不應出現在上載的課文內；不要把個案資料或敏感健康資訊用作教材。
- 工作紙屬原創教育輔助工具，**不是 Meltzer 原書工作紙或標準化執行功能評估**；不能用來診斷 ADHD、學習障礙或其他臨床問題。

## 理論與教材對應

| 源頭 | 轉化為網站設計 |
| --- | --- |
| Moran & Gardner (2018), Ch. 2 | Hill = 任務目的及成功準則；Skill = 可操作的學習技能；Will = 參與意願、努力與目標投入。網站以原創問句及任務安排操作化，不直接複製原書表格。 |
| Meltzer (2018), Ch. 11 | 目標設定、認知彈性、組織與優次、工作記憶、自我監控；透過原文提取、筆記鷹架、循序提示與自查練習融入實際學科。 |
| Chs. 8–10, 12–13 | 閱讀理解、數學解題、寫作自我調節相關的學科提示。 |
| Ch. 14 | 支援多種合理學習路徑和表達方式；不應以單一工作紙替代個別化教學。 |

參考：https://www.guilford.com/books/Executive-Function-in-Education/Lynn-Meltzer/9781462534531/contents

## 發布

這個資料夾可以整體上載至 GitHub Pages、Cloudflare Pages、Netlify 或任何靜態網站伺服器。必須保留 `index.html`、`styles.css`、`engine.js`、`app.js` 和 `assets/jszip.min.js` 的相對路徑。

## 版本

v1.0 · 2026-11-04 · 繁體中文 / 港澳教師應用；核心程式沒有服務端、收費服務或使用追蹤。
