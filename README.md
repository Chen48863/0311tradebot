# AI Chatbot 專案名稱

## 小組：

### 組員：

* 組員1 陳柏宇
* 組員2

## 專案簡介

本專案是一個使用 **LangChain** 搭配 **Google Gemini API** 開發的多模態 AI 對話程式（`chat.py`），可在終端機中執行，支援文字、圖片（JPG/PNG）、PDF、TXT 等多種輸入格式，並具備多輪對話歷史記憶功能，退出時會自動將對話記錄儲存為 JSON 檔案。

## 目前功能

* 💬 多輪文字對話（保留完整歷史脈絡）
* 🖼️ 圖片分析（JPG / JPEG / PNG，以 Base64 傳送）
* 📄 PDF 文件解析（使用 PyPDFLoader）
* 📝 純文字檔讀取與分析（TXT）
* 💾 退出時自動儲存對話紀錄（JSON 格式）

---

## 執行方式

1. 下載專案

```bash
git clone 你的專案網址
cd 0304tradebot
```

2. 安裝相依套件

```bash
pip install langchain langchain-google-genai langchain-community python-dotenv pypdf
```

3. 建立 `.env` 檔案並填入 API Key（詳見下方說明）

4. 執行程式

```bash
python chat.py
```

---

範例指令：

```bash
git clone https://github.com/Chen48863/0311tradebot.git
```

---

## 環境變數說明

請自行建立 `.env` 檔案，並填入自己的 API key。

範例：

```env
GEMINI_API_KEY=your_api_key_here
```

> ⚠️ 請勿將 `.env` 上傳至 GitHub（已在 `.gitignore` 中排除）。

---

## 遇到的問題與解法

### 問題 1

問題：執行程式時出現 `ValueError: ❌ 找不到 GOOGLE_API_KEY`，無法啟動對話。

解法：發現忘記在專案根目錄建立 `.env` 檔案。於是在根目錄新增 `.env`，並填入 `GOOGLE_API_KEY=自己的金鑰` 後，問題解決。同時確認 `python-dotenv` 套件已安裝（`pip install python-dotenv`）。

### 問題 2

問題：
解法：

---

## 學習心得

> 請簡要寫出本次作業的學習心得。

---

## GitHub 專案連結

陳柏宇:https://github.com/Chen48863/0311tradebot.git
