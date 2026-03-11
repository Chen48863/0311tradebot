# 20260311 — chat.py 說明文件

## 專案簡介

`chat.py` 是一個基於 **LangChain** 與 **Google Gemini API** 的多模態命令列對話程式，支援文字、圖片、PDF 及純文字檔案的輸入，並具備多輪對話歷史記憶與退出時自動儲存功能。

---

## 功能特色

| 功能 | 說明 |
|------|------|
| 💬 文字對話 | 支援多輪自然語言對話，保留完整歷史 |
| 🖼️ 圖片分析 | 支援 JPG / JPEG / PNG，以 Base64 編碼傳送 |
| 📄 PDF 解析 | 使用 `PyPDFLoader` 擷取 PDF 內文後送入模型 |
| 📝 TXT 解讀 | 讀取純文字檔並附加使用者問題一起分析 |
| 🧠 對話記憶 | 使用 `chat_history` 保存每輪對話脈絡 |
| 💾 自動儲存 | 退出時以 `chat_YYYYMMDD_HHMMSS.json` 格式儲存紀錄 |

---

## 環境需求

- Python 3.10 以上
- 套件清單：

```bash
pip install langchain langchain-google-genai langchain-community python-dotenv pypdf
```

---

## 環境變數設定

在專案根目錄建立 `.env` 檔案，填入您的 Google Gemini API 金鑰：

```env
GOOGLE_API_KEY=your_google_api_key_here
```

> ⚠️ 請勿將 `.env` 上傳至版本控制系統（已在 `.gitignore` 中排除）。

---

## 使用方式

```bash
python chat.py
```

啟動後，程式會顯示歡迎畫面，並進入互動模式：

- **文字輸入**：直接輸入問題並按 Enter
- **檔案輸入**：貼入完整檔案路徑（可附加問題），例如：
  ```
  C:\Users\willi\Desktop\report.pdf 請幫我總結這份報告
  ```
- **退出程式**：輸入 `quit`、`exit`、`bye`、`掰掰` 或 `再見`

---

## 支援的檔案格式

| 副檔名 | 類型 | 處理方式 |
|--------|------|----------|
| `.jpg` / `.jpeg` / `.png` | 圖片 | Base64 編碼，透過多模態接口傳送 |
| `.pdf` | PDF 文件 | PyPDFLoader 擷取文字 |
| `.txt` | 純文字 | 直接讀取並傳送 |

---

## 主要函式說明

| 函式名稱 | 功能說明 |
|----------|----------|
| `create_llm()` | 建立 Gemini LLM 實例（模型：`gemini-3-flash-preview`） |
| `detect_file(text)` | 判斷輸入是否包含合法檔案路徑並拆分路徑與問題 |
| `load_image_as_b64(path)` | 讀取圖片並轉換為 Base64 字串 |
| `load_pdf_text(path)` | 使用 PyPDFLoader 擷取 PDF 文字 |
| `load_txt_text(path)` | 讀取純文字檔內容 |
| `build_file_message(path, question)` | 根據檔案類型建立對應的 `HumanMessage` |
| `extract_text(raw)` | 解析 AI 回應（相容新舊版模型格式） |
| `save_conversation(records)` | 將對話紀錄以 JSON 格式儲存至本地 |
| `main()` | 主程式邏輯，負責互動迴圈與流程控制 |

---

## 對話紀錄格式

退出後會在程式所在目錄自動產生 JSON 紀錄檔，格式如下：

```json
[
  {
    "timestamp": "2026-03-11T10:00:00.000000",
    "role": "user",
    "content": "請分析這個檔案的內容。"
  },
  {
    "timestamp": "2026-03-11T10:00:02.000000",
    "role": "ai",
    "content": "這份檔案的主要內容為..."
  }
]
```

---

## 注意事項

- 使用圖片功能需確保 Gemini 模型版本支援多模態輸入。
- PDF 解析依賴 `pypdf`，若 PDF 為掃描版（圖片型），可能無法提取文字。
- 程式預設使用 `temperature=0.7`，可在 `create_llm()` 中調整。

---

## 授權

本程式僅供學習與教學用途使用。
