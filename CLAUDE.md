# ClinicMind 網站維護手冊

本檔是 `clinicmind/clinicmind.github.io` 的唯一維護規則來源。Claude 與 Muse 工作前都先讀本檔。專案指示只需寫一句：「先讀 repo 根目錄的 `CLAUDE.md`」。

- 網站：https://clinicmind.github.io/ ；知心選 PsyPick 在 `/psypick/`。
- PsyPick 的唯一資料源是本 repo 的 `psypick/data/`。舊 repo `clinicmind/psypick` 只作轉址與 `muse-inbox` 存檔，不要再寫入它的 `site/data/`。
- 筆記 repo `clinicmind/clinicmind` 是書房（library）的資料來源，不受 PsyPick 流程影響。

## 1. 六條鐵則

1. 例行工作只寫 `psypick/data/` 與 `psypick/posters/`。
2. 寫入前讀最新檔。不可以用舊副本。
3. 一則一檔。不手改由腳本產生的檔（`index.json`、`family.json`、`version.json`）。
4. 推送後看兩樣：Actions 是綠色；真網站 `version.json` 的提交編號等於剛才的提交。
5. 還原時，取壞提交的上一個提交的內容。在提交訊息寫明來源 SHA。
6. 不代 Gu 登入、不代 Gu 提交表格、不引入收費服務。

## 2. 資料放哪裡

| 內容 | 位置 | 備註 |
|---|---|---|
| 專業條目（研究、培訓等） | `psypick/data/cases/<slug>.json` | 一則一檔；只可由 `tools/psypick/inbox_to_cases.py` 寫入（第 3 節） |
| 索引（自動產生） | `psypick/data/index.json`、`index-lite.json`、`family-lite.json`、`version.json` | 由 `tools/psypick/build.py` 產生，**不要手改** |
| 親子內容 | `psypick/data/family.json` | 整檔維護：改前必讀最新版全檔，只改目標條目 |
| 人物動態 | `psypick/data/figures.json` | 整檔維護，同上 |
| 會議 | `psypick/data/conferences.json` | 整檔維護，同上 |
| 海報圖 | `psypick/posters/<slug>.svg` | case 檔的 `poster` 欄位指向這裡 |
| 巡查紀錄 | 舊 repo `clinicmind/psypick` 的 `muse-inbox` 分支 `inbox/*.json` | 只作存檔 |
| 主站臨床頁 | repo 根目錄 `*.html`、`assets/` | 例行 PsyPick 工作不要碰 |

## 3. 日常上架流程

1. **讀最新版**：先開真站 `psypick/data/version.json`，記下提交 SHA 與六個數字（`index` 專業條目、`family` 親子、`deal` 優惠、`figures_people` 人物、`figures_updates` 動態、`conferences` 會議）。要改的檔逐個讀最新版，不用手邊的舊副本（鐵則 2）。
2. **寫 inbox v2**：專業條目（case）一律先寫成 inbox v2 JSON（格式見下面），不要直接寫 case 檔。
3. **跑轉換器（唯一上架方法）**：`python3 tools/psypick/inbox_to_cases.py <inbox.json>`。
   - 轉換器會自動：檢查必填欄位、對照舊分類名、把 `evidence_hint` 換成數字、去重（slug 或來源網址已存在就略過，**不會覆蓋**舊檔）、寫入 `psypick/data/cases/<slug>.json`、跑 `build.py` 與 `validate.py`。
   - 任何一則有錯 → 整批不寫；`validate.py` 不過 → 自動刪走新檔並還原索引，結束碼 1。可先加 `--dry-run` 只做檢查。
   - **最後一行未見 `VALIDATION PASSED` 不准推送。**
   - **禁止**另寫臨時轉換腳本、禁止人手寫或改 case 檔。要改舊條目內容（例如下架 `include: false`）屬例外，改完一樣要跑 `build.py` 與 `validate.py` 全過。
   - 親子、人物、會議是整檔維護（不經轉換器）：以最新版全檔為底，只加或改目標條目，不要用舊版整檔覆蓋；改完跑 `python3 tools/psypick/build.py --data-dir psypick/data` 及 `python3 tools/validate.py --data-dir psypick/data`，全過才推送。
4. **去重以外的重複**：轉換器只認 slug 與來源網址。同主辦＋同活動日期＋同主題但網址不同的，寫 inbox 前自己用腳本在 `index.json` 搜一次（不要把整個 JSON 讀入對話）。

### inbox v2 格式

```json
{
  "version": 2,
  "run_at": "2026-11-25T01:00:00+00:00",
  "items": [
    {
      "type": "case",
      "slug": "（可省略；省略就由 title_en 自動產生，最長 60 字元）",
      "title_zh": "…", "title_en": "…",
      "summary_zh": "…", "summary_en": "…",
      "category": "研究與證據｜臨床實務｜AI 與倫理｜進修培訓",
      "kind": "research｜practice｜product｜incident｜training",
      "evidence_hint": "個人經驗或評論｜產品宣稱｜前導或質性研究｜對照試驗｜系統性回顧或統合分析",
      "evidence_note": "一句說明",
      "evidence_quote": "原文逐字摘句，不多於 40 字",
      "page_date": "YYYY-MM-DD（原文頁面日期；找不到留空，並要 verify_needed=true）",
      "brief_zh": ["重點 1", "重點 2"],
      "caution": "注意事項",
      "supervision_questions": ["督導問題"],
      "tags": ["…"], "population": ["…"],
      "verify_needed": false, "verify_reason": "",
      "ethics_flags": [], "model_names": [],
      "source": {"url": "官方頁面", "title": "原文標題", "author_name": "機構／期刊", "content": "一句專業註解（可省略）"},
      "training": {"provider": "…", "format": "線上直播", "price": "…", "price_tier": "免費",
                   "ce_credits": "…", "language": "英文", "event_date": "YYYY-MM-DD 或 隨選",
                   "deadline": "", "audience_level": "…", "topic": "…", "signup_url": "報名頁"}
    }
  ]
}
```

- **必填**：`title_zh`、`title_en`、`summary_zh`、`summary_en`、`category`、`kind`、`evidence_hint`（或 0–4 的 `evidence_level`）、`evidence_note`、`evidence_quote`（≤40 字）、`brief_zh`、`caution`、`supervision_questions`、`tags`、`population`、`verify_needed`、`source.url`／`source.title`／`source.author_name`。
- **培訓**（`kind=training` 或分類「進修培訓」）另要 `training.provider`、`format`、`event_date`（ISO 或「隨選」）、`signup_url`。
- 冇 `page_date` 就必須 `verify_needed: true` 並寫 `verify_reason`。`page_date` 會寫入 `posts[0].posted_at`。
- 舊分類名自動對照：臨床與治療應用、評估與篩檢 → 臨床實務；進修與培訓 → 進修培訓；倫理與風險、人機互動心理 → AI 與倫理。其他未知分類報錯。
- `type` 不是 `case` 的項目（親子、人物等）轉換器會列出並略過。
- 同一份 inbox 同時是巡查存檔（推去舊 repo `muse-inbox` 分支），可另加 `key_points_zh` 等存檔欄位，轉換器不讀。

5. **一項一提交**：提交訊息寫明任務或來源（例：「巡查上架 2026-11-21 週五組」）。任一集合一次減少超過 5 項，提交訊息要加 `[remove]`，並先通知 Gu。
6. **推送後核實**：推送到 `main` 後等部署完成（通常 1–3 分鐘），讀真站 `version.json`：SHA 等於剛才的提交、六個數字正確；再開新條目頁面抽查一次（網址格式：`https://clinicmind.github.io/psypick/#/case/<slug>`）。兩樣都對才算完成（鐵則 4）。
7. **留紀錄與匯報**：巡查紀錄 inbox JSON 推去舊 repo 的 `muse-inbox` 分支；照第 7 節格式向 Gu 匯報。

## 4. 條目欄位（case 檔）

| 欄位 | 說明 |
|---|---|
| `slug` | 與檔名一致。由轉換器產生：inbox 有寫 `slug` 就用，冇就由 `title_en` 轉小寫連字號、刪標點，最長 60 字元（與現有條目一致，保留 `for`、`and` 等字）。可在 inbox 自訂主辦方前綴（例：`pesi-`）。已存在的 slug 轉換器會略過，不會覆蓋 |
| `title_zh` / `title_en`、`summary_zh` / `summary_en` | 標題與摘要，中英各一 |
| `category` | 站內既有分類名稱（研究與證據／臨床實務／AI 與倫理／進修培訓） |
| `kind` | `research`、`training` 等既有值 |
| `date` | 條目日期（ISO）；培訓日期放 `training.event_date` |
| `first_seen_at` | 首次上架時間（ISO） |
| `posts[]` | 來源：`platform`、`url`、`author_name`、`title`、`content`（專業註解）、`posted_at`。至少一條要有 `url`（檢查閘 (e)） |
| `evidence_quote` | 原文摘句，不多於 40 字，逐字照錄。**`first_seen_at` 在 2026-11-20 之後的新條目必填**（檢查閘 (h)） |
| `evidence_level` / `evidence_note` | 證據強度 0–4（0 個人經驗或評論、1 產品宣稱、2 前導或質性研究、3 對照試驗、4 系統性回顧或統合分析；以 `index.json` 的 `config.evidence_levels` 為準）與一句說明 |
| `ethics_flags[]`、`caution`、`supervision_questions[]` | 倫理旗標、注意事項、督導思考問題 |
| `tags[]`、`population[]` | 標籤與對象 |
| `verify_needed` / `verify_reason` | 未核實要標 `true` 並寫原因，不要扮已核實 |
| `training{}` | 培訓才有：`provider`、`format`、`price`、`price_tier`、`ce_credits`、`language`、`event_date`（`YYYY-MM-DD`、空白或「隨選」）、`deadline`、`audience_level`、`topic`、`signup_url`（註：`build.py` 只把其中 8 個子欄位帶入索引——`provider`、`format`、`price`、`price_tier`、`ce_credits`、`language`、`event_date`、`deadline`；其餘只留在 case 檔） |
| `poster` | 海報入庫後才填，格式是物件：`{"src": "posters/<slug>.svg", "alt": "海報文字說明", "style": "…", "made": "YYYY-MM-DD"}`（`src` 相對於 `psypick/`，圖檔實體放 `psypick/posters/`）。迷幻藥／氯胺酮題材不可有此欄（檢查閘 (j)） |
| `include` | `false` = 下架但保留檔案；不填或 `true` = 在架 |

inbox 紀錄（巡查存檔）另有 `evidence_quote`、`page_date`、`source`、`key_points_zh` 等欄位，是核實證據的存放處。`page_date`（原文頁面上的日期）記入 inbox 紀錄；case 檔則以 `posts[].posted_at` 記來源發佈日期。兩者找不到都留空並標待查證，不可以用上架時間代替。

## 5. 每則條目的品質清單

| 欄位 | 要求 |
|---|---|
| 來源網址 | 官方頁面優先。第三方報道要標明 |
| `page_date` | 原文頁面上的日期。找不到就留空並標待查證。不可以用上架時間代替 |
| `evidence_quote` | 原文摘句，不多於 40 字，逐字照錄 |
| 數字、日期、價格 | 逐字照原文 |
| 培訓 | 對象是專業人員；可全程線上；`event_date` 用 ISO 格式 |
| 禁收 | 可識別個案資料、兒童姓名或相片、私人論壇求助帖、速成證書、嬰兒配方奶或食品推廣、任何購物優惠 |
| 海報 | 迷幻藥、氯胺酮、esketamine 題材不做海報 |

## 6. 檢查閘

- 部署流程 `.github/workflows/pages.yml`：推送到 `main` 後先跑 `build.py` 產生索引，再跑 `validate.py`，全過才部署。檢查失敗就不部署，真網站不變。
- `validate.py` 規則：(a) 所有 JSON 可解析；(b) index 的 slug 與 case 檔一一對應；(c) 沒有 `kind=deal`、沒有 `deal_platforms`、family 主題沒有「優惠」；(d) 在架培訓形式不含「實體／現場／面授」，除非同時含「線上」；(e) 每則有來源網址；(f) `generated_at` 不早於上一個提交；(g) 任一集合數量比上一個提交減少超過 5 項而提交訊息沒有 `[remove]` 就失敗；(h) 2026-11-20 之後的新條目必須有 `evidence_quote` 且不多於 40 字；(i) 培訓 `event_date` 必須是 ISO 日期、空白或「隨選」（警告）；(j) 迷幻藥／氯胺酮相關條目不可以有 `poster` 欄位；(k) `first_seen_at` 在 2026-11-24 之後的新條目，`category` 必須是「研究與證據／臨床實務／AI 與倫理／進修培訓」之一（舊條目只警告）。
- 注意：(f)、(g) 需要 `--prev-dir` 與 `--message` 參數，CI 現時未有帶，所以 (g) 在 CI 未啟用。防整檔覆蓋靠鐵則 2 與第 3 節流程自律；大量刪除仍要照 `[remove]` 標記，先通知 Gu。
- `tools/linkcheck.py` 每週自動跑一次：失效連結只報告，不自動下架。
- 把檢查交給腳本做，不要把幾百 KB 的 JSON 讀入對話。這是最大的 token 節省。

## 7. 節奏與排程對應

| 頻率 | 工作 | 由誰 |
|---|---|---|
| 每日 21:21 | Feed 篩選（上限 5 則） | Muse（cron `feed-to-psypick-daily`） |
| 週二、五 09:00 | PsyPick 巡查 | Muse（cron `psypick-daily-patrol`） |
| 週二、五 10:21 | IG 海報＋存圖＋寫 `poster` 欄位 | Muse（cron `psypick-free-training-ig-poster`） |
| 週二、五 15:00 | 人物巡查 | Muse（cron `psypick-figure-patrol`） |
| 每日（自動） | `build.py` 按日期自動歸檔過期條目 | Actions |
| 每週一（自動） | 連結檢查 | Actions |
| 每週五 | 週報：新增數、下架數、待查證數、證據摘句覆蓋率、失效連結數 | Muse |
| 每月 1 日 | 月度檢查：隨選培訓重新核實、賞金獵人重新核實、會議 `last_checked` 更新、分類與標籤是否仍然合用；連同月度報告交 Gu | Muse |
| 每季 | 檢視：來源清單增刪、人物名單、過期規則是否要調整 | Gu 與 Muse |

## 8. 匯報格式（每次上架後）

```
【PsyPick 上架 2026-11-17 週二組】
提交：abc1234　Actions：通過　version.json：已核對
新增：研究 4、培訓 3、親子 2
下架／歸檔：培訓 2（已過期）
現有總數：專業 268｜親子 183（deal 0）｜人物 40／動態 100｜會議 34
待查證：專業 12｜親子 9
需要 Gu 留意：無
```

## 9. 出事時的處理

| 情況 | 處理 |
|---|---|
| Actions 紅色 | 真網站沒有變。讀錯誤訊息。修正後再推送。不要繞過檢查 |
| 推送成功但網站沒更新 | 等 5 分鐘。再看 Actions 的部署步驟。仍然失敗就報告 Gu，附上執行連結 |
| 發現錯誤內容已上線 | 即時下架該則（改 `include: false`）。然後查證。24 小時內向 Gu 匯報 |
| 數量無故減少 | 停止所有推送。比對最近三個提交。用鐵則 5 還原 |
| 有人投訴內容（當事人、機構） | 即時下架。交 Gu 決定。不自行回覆 |

回滾做法（鐵則 5 的具體步驟）：找出壞提交的上一個提交，取它版本的受影響檔案內容，逐檔重新寫入，提交訊息寫明「還原自 <來源 SHA>」，推送後照第 3 節第 6 步核實 `version.json`。不要 force push，不要繞過檢查閘。

## 10. 什麼時候找 Claude

Muse 做日常維護。以下情況建議交 Claude 做，或請 Claude 覆核：

1. 修改 `validate.py`、`build.py` 的邏輯。
2. 修改 `app.js` 的路由或資料結構。
3. 同一類錯誤出現第二次。
4. 新增一個資料類別或新頁面。
5. 任何涉及私隱、法律或 Gu 專業守則的內容判斷。

## 11. 紅線

- 不碰 `.github/workflows/`：自動化連接器沒有這個權限；要改就把完整檔案內容交 Gu，由 Gu 在 GitHub 網頁版貼上。
- 例行工作不改主站臨床頁、`assets/` 與 PsyPick 程式（`psypick/app.js`、`style.css`、`index.html`）；任務指明並經 Gu 同意才改。
- 不上架購物優惠：`deal` 類別已經廢除，檢查閘 (c) 會擋。
- 不代 Gu 登入、不代 Gu 提交表格、不引入收費服務（鐵則 6）。
