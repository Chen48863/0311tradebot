# AI Chatbot 專案名稱

## 小組：五分之四之五之四

### 組員：

* 組員 1 :陳柏宇
* 組員 2 :陳婉榕
* 組員 3 :洪紹禎
* 組員 4 :林永富
* 組員 5 :楊程軒
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

> 陳柏宇:透過這次實作，學會了如何使用 LangChain 串接 Google Gemini API，並實現多模態輸入（文字、圖片、PDF）的對話功能。過程中也更了解如何透過 `.env` 管理 API 金鑰，以及如何用 JSON 格式保存對話記錄。整體而言，對於 AI Agent 的基本架構有了更清楚的認識。

> 林永富：這週的 AI Agent 課程讓我學到如何利用 GitHub 進行版本控制，也更了解專案開發中管理程式碼的重要性。透過實際操作，我認識了像是提交、同步與版本紀錄等基本功能，知道 GitHub 不只是存放程式碼的平台，也能幫助團隊協作與追蹤修改內容。這次課程讓我對版本控制有更清楚的概念，也覺得這是未來開發 AI 專案時很實用的基礎能力。

> 陳婉榕：本次課程主要介紹 AI 專案開發過程中「版本控制與團隊協作」的重要性，並實際操作 Git 與 GitHub 來管理專案。透過重建一個最小可運作的 chatbot 專案，我理解到在 AI 開發中，程式會頻繁修改，如果沒有良好的版本管理機制，很容易在修改錯誤時無法回復，或在多人協作時造成程式碼互相覆蓋的問題。課程也讓我學習到 Git 的基本操作，例如使用 commit 記錄版本、push 將本地端程式同步到 GitHub，以及透過 branch 進行分工開發。此外，我也了解到 API key 等敏感資訊應透過 .env 檔案管理並加入 .gitignore，避免上傳到 GitHub 造成安全風險。透過這次實作，我不僅學會了基本的專案版控流程，也更理解團隊協作在 AI 專案開發中的重要性，對未來進行多人合作開發專案具有很大的幫助。 
---

## GitHub 專案連結

陳柏宇:https://github.com/Chen48863/0311tradebot.git

林永富：https://github.com/Frankfurt-shrimp/Chatbot.git

陳婉榕：https://github.com/chenwanrong0819/gemini-agent-hw.git
