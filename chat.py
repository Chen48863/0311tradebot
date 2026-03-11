"""
LangChain + Google Gemini API 多模態對話程式
支援：文字對話、圖片 (JPG/PNG)、PDF、TXT 檔案輸入
      多輪對話歷史記憶、退出時 JSON 持久化
"""

import os
import json
import base64
import mimetypes
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# 載入 .env 檔案中的環境變數
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("❌ 找不到 GOOGLE_API_KEY，請確認 .env 檔案是否正確設定。")

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".txt"}


# ── LLM 建立 ────────────────────────────────────────────

def create_llm() -> ChatGoogleGenerativeAI:
    """建立 Gemini LLM 實例（支援多模態）"""
    return ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.7,
    )


# ── 檔案處理 ────────────────────────────────────────────

def detect_file(text: str) -> tuple[Path | None, str]:
    """
    判斷輸入是否包含合法檔案路徑（支援帶引號的路徑）。
    回傳 (Path物件, 附帶的問題文字) 或 (None, 原始輸入)
    """
    text = text.strip()
    # 嘗試抓出第一段 token（可能含引號）
    if text.startswith(('"', "'")):
        quote = text[0]
        end = text.find(quote, 1)
        candidate = text[1:end] if end != -1 else text[1:]
        rest = text[end + 1:].strip() if end != -1 else ""
    else:
        parts = text.split(None, 1)
        candidate = parts[0]
        rest = parts[1] if len(parts) > 1 else ""

    p = Path(candidate)
    if p.exists() and p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS:
        return p, rest
    return None, text


def load_image_as_b64(path: Path) -> tuple[str, str]:
    """讀取圖片，回傳 (base64字串, MIME type)"""
    mime, _ = mimetypes.guess_type(str(path))
    mime = mime or "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return b64, mime


def load_pdf_text(path: Path) -> str:
    """用 PyPDFLoader 提取 PDF 文字"""
    from langchain_community.document_loaders import PyPDFLoader
    loader = PyPDFLoader(str(path))
    pages = loader.load()
    return "\n\n".join(p.page_content for p in pages)


def load_txt_text(path: Path) -> str:
    """讀取純文字檔"""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def build_file_message(path: Path, question: str) -> tuple[HumanMessage, str]:
    """
    根據檔案類型建立對應的 HumanMessage 與紀錄摘要。
    回傳 (HumanMessage, 紀錄用的摘要字串)
    """
    ext = path.suffix.lower()
    default_question = "請分析這個檔案的內容。"
    q = question.strip() or default_question

    if ext in (".jpg", ".jpeg", ".png"):
        b64, mime = load_image_as_b64(path)
        msg = HumanMessage(content=[
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}"},
            },
            {"type": "text", "text": q},
        ])
        summary = f"[圖片：{path.name}] {q}"

    elif ext == ".pdf":
        text = load_pdf_text(path)
        msg = HumanMessage(
            content=f"[PDF 檔案：{path.name}]\n\n{text}\n\n{q}"
        )
        summary = f"[PDF：{path.name}（{len(text)} 字元）] {q}"

    elif ext == ".txt":
        text = load_txt_text(path)
        msg = HumanMessage(
            content=f"[文字檔：{path.name}]\n\n{text}\n\n{q}"
        )
        summary = f"[TXT：{path.name}（{len(text)} 字元）] {q}"

    else:
        raise ValueError(f"不支援的檔案格式：{ext}")

    return msg, summary


# ── 回應解析 ────────────────────────────────────────────

def extract_text(raw) -> str:
    """解析 AI 回應（相容新舊版模型格式）"""
    if isinstance(raw, list):
        return " ".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in raw
        ).strip()
    return raw


# ── 持久化 ──────────────────────────────────────────────

def save_conversation(records: list[dict]) -> str:
    """將對話紀錄存為 JSON，檔名格式 chat_YYYYMMDD_HHMMSS.json"""
    if not records:
        return ""
    filename = datetime.now().strftime("chat_%Y%m%d_%H%M%S.json")
    filepath = Path(__file__).parent / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    return str(filepath)


# ── 畫面 ────────────────────────────────────────────────

def print_banner():
    print("=" * 58)
    print("  🤖  LangChain × Gemini  多模態對話助理  🤖")
    print("=" * 58)
    print("  模型：gemini-3-flash-preview")
    print("  支援：文字 | 圖片 (JPG/PNG) | PDF | TXT")
    print("  用法：直接輸入問題，或貼上檔案路徑後按 Enter")
    print("  輸入 'quit' 或 'exit' 結束並儲存對話")
    print("=" * 58)
    print()


def print_file_tip(path: Path):
    icons = {".jpg": "🖼️", ".jpeg": "🖼️", ".png": "🖼️",
             ".pdf": "📄", ".txt": "📝"}
    icon = icons.get(path.suffix.lower(), "📁")
    print(f"  {icon} 偵測到檔案：{path.name}")
    print(f"     格式：{path.suffix.upper()}  大小：{path.stat().st_size / 1024:.1f} KB")


# ── 主程式 ──────────────────────────────────────────────

def main():
    print_banner()

    llm = create_llm()
    chat_history = [
        SystemMessage(content=(
            "你是一個友善且專業的 AI 助理，"
            "能夠分析文字、圖片、PDF 及純文字檔案，"
            "請以繁體中文回答使用者的問題。"
        ))
    ]
    conversation_records: list[dict] = []
    turn = 1

    while True:
        try:
            user_input = input(f"\n[第 {turn} 輪] 您：").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            break

        if not user_input:
            print("⚠️  請輸入訊息或貼入檔案路徑。")
            continue

        if user_input.lower() in ("quit", "exit", "bye", "掰掰", "再見"):
            break

        # ── 判斷是否為檔案輸入 ──────────────────────────
        file_path, question = detect_file(user_input)

        if file_path:
            print_file_tip(file_path)
            if not question:
                try:
                    question = input("  ❓ 請輸入關於此檔案的問題（直接 Enter 使用預設）：").strip()
                except (KeyboardInterrupt, EOFError):
                    question = ""

            print("⏳ AI 分析中...", end="\r")
            try:
                human_msg, content_summary = build_file_message(file_path, question)
            except Exception as e:
                print(f"\n❌ 檔案載入失敗：{e}\n")
                continue

            record_content = content_summary

        else:
            # ── 一般文字輸入 ────────────────────────────
            human_msg = HumanMessage(content=user_input)
            record_content = user_input
            print("⏳ AI 思考中...", end="\r")

        # 記錄使用者訊息
        conversation_records.append({
            "timestamp": datetime.now().isoformat(),
            "role": "user",
            "content": record_content,
        })
        chat_history.append(human_msg)

        # ── 呼叫 LLM ────────────────────────────────────
        try:
            response = llm.invoke(chat_history)
            ai_text = extract_text(response.content)

            chat_history.append(AIMessage(content=ai_text))
            conversation_records.append({
                "timestamp": datetime.now().isoformat(),
                "role": "ai",
                "content": ai_text,
            })

            print(" " * 20, end="\r")
            print(f"AI助理：{ai_text}")

        except Exception as e:
            chat_history.pop()
            conversation_records.pop()
            print(f"\n❌ 發生錯誤：{e}\n")

        turn += 1

    # ── 結束：儲存對話紀錄 ──────────────────────────────
    print("\n👋 對話已結束，掰掰！")
    if conversation_records:
        filepath = save_conversation(conversation_records)
        print(f"💾 對話紀錄已儲存：{filepath}")
    else:
        print("（本次沒有任何對話紀錄，不儲存。）")


if __name__ == "__main__":
    main()
