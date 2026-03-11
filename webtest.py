import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_community.document_loaders import PyPDFLoader

# 1. 載入環境變數 (確保同目錄下有 .env)
load_dotenv()

def main():
    print("🤖 [對照組測試] 終端機多模態 AI 已啟動！")
    print("💡 可以直接打字對話，或貼上 .pdf 檔案的絕對路徑讓他讀取。")
    print("輸入 'exit' 或 'quit' 即可結束並自動存檔 (JSON)。\n" + "-"*50)

    # 2. 抓取金鑰並初始化 Gemini 模型
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 錯誤：找不到 GOOGLE_API_KEY，請檢查 .env 檔案！")
        return

    # 對應教授要求的 gemini-2.5-flash 模型
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)

    # 3. 初始化對話記憶
    chat_history = [
        SystemMessage(content="你是一位精通文件分析與工程學科的專業 AI 助理。")
    ]
    json_log = []

    while True:
        user_input = input("\n[您]: ").strip()
        
        if user_input.lower() in ['exit', 'quit']:
            break
        if not user_input:
            continue

        # 4. 多模態讀取邏輯 (判斷是否輸入了 PDF 路徑)
        message_content = user_input
        if user_input.lower().endswith('.pdf'):
            try:
                if os.path.exists(user_input):
                    print(f"📄 正在解析 PDF 檔案：{os.path.basename(user_input)}...")
                    loader = PyPDFLoader(user_input)
                    pages = loader.load()
                    pdf_text = "\n".join([page.page_content for page in pages])
                    message_content = f"請幫我分析以下 PDF 內容並總結重點：\n\n{pdf_text}"
                    print("✅ PDF 讀取成功！")
                else:
                    print("❌ 找不到該檔案，請確認路徑是否正確（不要有引號）。")
                    continue
            except Exception as e:
                print(f"❌ PDF 讀取失敗：{e}")
                continue

        # 紀錄使用者訊息
        chat_history.append(HumanMessage(content=message_content))
        json_log.append({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "role": "user", "content": user_input})

        # 5. 呼叫 Gemini 模型
        try:
            print("⏳ AI 思考中...")
            response = llm.invoke(chat_history)
            ai_reply = response.content
            
            print(f"\n[AI助理]:\n{ai_reply}")
            
            # 紀錄 AI 訊息
            chat_history.append(AIMessage(content=ai_reply))
            json_log.append({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "role": "ai", "content": ai_reply})
            
        except Exception as e:
            print(f"❌ 發生錯誤：{e}")

    # 6. 資料持久化 (存成 JSON)
    if json_log:
        # 抓取這個 webtest.py 所在的絕對資料夾路徑
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 把檔名跟資料夾路徑拼起來，強制存在這裡
        filename = os.path.join(current_dir, f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(json_log, f, ensure_ascii=False, indent=4)
            print(f"\n👋 對話已結束！\n💾 紀錄已成功儲存至：{filename}")
        except Exception as e:
            print(f"\n❌ 存檔失敗，可能是系統權限問題：{e}")

if __name__ == "__main__":
    main()