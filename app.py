"""
Streamlit GUI — LangChain × Gemini 多模態對話助理
功能：多輪對話 | 多模態檔案 | 自訂 AI 角色管理 | JSON 持久化
"""

import os
import json
import tempfile
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from chat import create_llm, extract_text, build_file_message, save_conversation

load_dotenv()

ROLES_FILE = Path(__file__).parent / "roles.json"

# ─────────────────────────────────────────────────────────
# 角色持久化
# ─────────────────────────────────────────────────────────
def load_roles() -> list[dict]:
    if ROLES_FILE.exists():
        with open(ROLES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_roles(roles: list[dict]):
    with open(ROLES_FILE, "w", encoding="utf-8") as f:
        json.dump(roles, f, ensure_ascii=False, indent=2)

# ─────────────────────────────────────────────────────────
# 頁面設定
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Gemini 多模態對話助理",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer { visibility: hidden; }

.main-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 1.4rem 2rem;
    border-radius: 16px;
    margin-bottom: 1.2rem;
    text-align: center;
}
.main-header h1 { color: #e0e0ff; font-size: 1.7rem; font-weight: 600; margin: 0; }
.main-header p  { color: #8888bb; margin: 0.3rem 0 0; font-size: 0.85rem; }

.role-card {
    background: #1e2a40;
    border-left: 3px solid #4a90d9;
    border-radius: 8px;
    padding: 0.6rem 0.9rem;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
    color: #aac4e8;
}
.role-card strong { color: #e0e0ff; display: block; margin-bottom: 2px; }
.active-role {
    border-left-color: #44d9a0 !important;
    background: #1a2e25 !important;
}

.status-badge {
    display: inline-block;
    background: #0f3460;
    color: #7eb8f7;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 500;
    margin-top: 0.3rem;
}
.file-preview {
    background: #1e2a40;
    border-left: 3px solid #4a90d9;
    padding: 0.6rem 1rem;
    border-radius: 8px;
    font-size: 0.85rem;
    color: #aac4e8;
    margin-bottom: 0.8rem;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
}
[data-testid="stSidebar"] * { color: #ccc !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #e0e0ff !important; }
.stButton > button {
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(74,144,217,0.3) !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# 頁面路由
# ─────────────────────────────────────────────────────────
PAGES = ["💬 對話", "🎭 角色管理"]

# ─────────────────────────────────────────────────────────
# Session State 初始化
# ─────────────────────────────────────────────────────────
def init_session():
    if "llm" not in st.session_state:
        st.session_state.llm = create_llm()
    if "roles" not in st.session_state:
        st.session_state.roles = load_roles()
    if "active_role_idx" not in st.session_state:
        st.session_state.active_role_idx = 0
    if "chat_history" not in st.session_state:
        _init_chat()
    if "conversation_records" not in st.session_state:
        st.session_state.conversation_records = []
    if "display_messages" not in st.session_state:
        st.session_state.display_messages = []
    if "pending_file" not in st.session_state:
        st.session_state.pending_file = None
    if "page" not in st.session_state:
        st.session_state.page = PAGES[0]

def _init_chat():
    roles = st.session_state.get("roles", load_roles())
    idx   = st.session_state.get("active_role_idx", 0)
    prompt = roles[idx]["prompt"] if roles else "你是一個友善的 AI 助理，請以繁體中文回答。"
    st.session_state.chat_history = [SystemMessage(content=prompt)]

def switch_role(idx: int):
    """切換角色並重置對話"""
    st.session_state.active_role_idx = idx
    st.session_state.chat_history = []
    st.session_state.display_messages = []
    st.session_state.conversation_records = []
    _init_chat()

init_session()

# ─────────────────────────────────────────────────────────
# 側邊欄（共用）
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 Gemini 助理")
    st.markdown('<span class="status-badge">⚡ gemini-3-flash-preview</span>',
                unsafe_allow_html=True)
    st.divider()

    # 頁面切換
    st.session_state.page = st.radio("📌 頁面", PAGES, label_visibility="collapsed")
    st.divider()

    # ── 角色快速切換 ─────────────────────────────────────
    st.markdown("### 🎭 目前角色")
    roles = st.session_state.roles
    if roles:
        role_names = [r["name"] for r in roles]
        selected = st.selectbox(
            "選擇角色",
            options=range(len(role_names)),
            format_func=lambda i: role_names[i],
            index=st.session_state.active_role_idx,
            label_visibility="collapsed",
        )
        if selected != st.session_state.active_role_idx:
            switch_role(selected)
            st.rerun()
        # 顯示目前角色的 prompt 摘要
        preview = roles[st.session_state.active_role_idx]["prompt"][:80] + "..."
        st.caption(f"📝 {preview}")
    else:
        st.info("尚未設定角色，請前往「角色管理」新增。")

    st.divider()

    # ── 檔案上傳 ─────────────────────────────────────────
    if st.session_state.page == PAGES[0]:
        st.markdown("### 📎 上傳檔案")
        uploaded_file = st.file_uploader(
            "JPG / PNG / PDF / TXT",
            type=["jpg", "jpeg", "png", "pdf", "txt"],
            label_visibility="collapsed",
        )
        if uploaded_file:
            ext = Path(uploaded_file.name).suffix.lower()
            icons = {".jpg":"🖼️",".jpeg":"🖼️",".png":"🖼️",".pdf":"📄",".txt":"📝"}
            st.markdown(
                f'<div class="file-preview">'
                f'{icons.get(ext,"📁")} <b>{uploaded_file.name}</b><br>'
                f'大小：{uploaded_file.size/1024:.1f} KB',
                unsafe_allow_html=True,
            )
            tmp = tempfile.NamedTemporaryFile(
                delete=False, suffix=Path(uploaded_file.name).suffix
            )
            tmp.write(uploaded_file.read())
            tmp.flush()
            st.session_state.pending_file = {
                "path": Path(tmp.name),
                "name": uploaded_file.name,
            }
            st.success("✅ 檔案就緒！")
        else:
            st.session_state.pending_file = None

        st.divider()

        # ── 對話統計與儲存 ───────────────────────────────
        n = len(st.session_state.conversation_records)
        col1, col2 = st.columns(2)
        col1.metric("訊息", n)
        col2.metric("輪數", n // 2)

        if st.button("� 儲存 JSON", use_container_width=True):
            if st.session_state.conversation_records:
                fp = save_conversation(st.session_state.conversation_records)
                st.success(f"已儲存：`{Path(fp).name}`")
            else:
                st.warning("尚無紀錄")

        if st.session_state.conversation_records:
            st.download_button(
                "⬇️ 下載 JSON",
                data=json.dumps(st.session_state.conversation_records,
                                ensure_ascii=False, indent=2).encode("utf-8"),
                file_name=datetime.now().strftime("chat_%Y%m%d_%H%M%S.json"),
                mime="application/json",
                use_container_width=True,
            )

        if st.button("🗑️ 清除對話", use_container_width=True):
            switch_role(st.session_state.active_role_idx)
            st.rerun()


# ═════════════════════════════════════════════════════════
# 頁面 1：對話
# ═════════════════════════════════════════════════════════
if st.session_state.page == PAGES[0]:

    # 標題顯示目前角色
    current_role_name = (
        roles[st.session_state.active_role_idx]["name"]
        if roles else "一般助理"
    )
    st.markdown(f"""
    <div class="main-header">
        <h1>🤖 LangChain × Gemini 多模態對話</h1>
        <p>目前角色：{current_role_name}　|　支援文字 · 圖片 · PDF · TXT　|　多輪記憶</p>
    </div>
    """, unsafe_allow_html=True)

    # 歷史訊息
    for msg in st.session_state.display_messages:
        with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])

    # 輸入框
    pending = st.session_state.pending_file
    placeholder = (
        f"💬 請輸入關於「{pending['name']}」的問題..."
        if pending else "💬 請輸入問題..."
    )

    if user_input := st.chat_input(placeholder):
        display_text = (
            f"📎 `{pending['name']}`\n\n{user_input}" if pending else user_input
        )
        st.session_state.display_messages.append(
            {"role": "user", "content": display_text}
        )
        with st.chat_message("user", avatar="🧑"):
            st.markdown(display_text)

        if pending:
            try:
                human_msg, summary = build_file_message(pending["path"], user_input)
                record_content = summary
            except Exception as e:
                st.error(f"❌ 檔案處理失敗：{e}")
                st.stop()
        else:
            human_msg = HumanMessage(content=user_input)
            record_content = user_input

        st.session_state.conversation_records.append({
            "timestamp": datetime.now().isoformat(),
            "role": "user",
            "content": record_content,
        })
        st.session_state.chat_history.append(human_msg)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("⏳ AI 思考中..."):
                try:
                    response = st.session_state.llm.invoke(
                        st.session_state.chat_history
                    )
                    ai_text = extract_text(response.content)
                    st.session_state.chat_history.append(AIMessage(content=ai_text))
                    st.session_state.conversation_records.append({
                        "timestamp": datetime.now().isoformat(),
                        "role": "ai",
                        "content": ai_text,
                    })
                    st.session_state.display_messages.append(
                        {"role": "assistant", "content": ai_text}
                    )
                    st.markdown(ai_text)
                except Exception as e:
                    st.session_state.chat_history.pop()
                    st.session_state.conversation_records.pop()
                    st.error(f"❌ 發生錯誤：{e}")
        st.rerun()


# ═════════════════════════════════════════════════════════
# 頁面 2：角色管理
# ═════════════════════════════════════════════════════════
elif st.session_state.page == PAGES[1]:

    st.markdown("""
    <div class="main-header">
        <h1>🎭 AI 角色管理</h1>
        <p>新增、編輯或刪除 AI 角色，切換角色後對話會重新開始</p>
    </div>
    """, unsafe_allow_html=True)

    # ── 新增角色 ─────────────────────────────────────────
    with st.expander("➕ 新增自訂角色", expanded=True):
        new_name   = st.text_input("角色名稱（含 emoji 更好看）",
                                   placeholder="例如：🧑‍⚕️ 醫療顧問")
        new_prompt = st.text_area(
            "角色 System Prompt",
            placeholder=(
                "例如：你是一位專業的醫療健康顧問，"
                "擅長用淺顯易懂的方式解釋醫學知識。"
                "請務必聲明你的建議僅供參考，需諮詢正規醫師。"
                "請以繁體中文回答。"
            ),
            height=140,
        )
        if st.button("✅ 新增角色", use_container_width=True):
            if not new_name.strip():
                st.error("請填寫角色名稱！")
            elif not new_prompt.strip():
                st.error("請填寫 System Prompt！")
            elif any(r["name"] == new_name.strip()
                     for r in st.session_state.roles):
                st.error("角色名稱已存在，請使用不同名稱！")
            else:
                st.session_state.roles.append(
                    {"name": new_name.strip(), "prompt": new_prompt.strip()}
                )
                save_roles(st.session_state.roles)
                st.success(f"✅ 角色「{new_name.strip()}」已新增！")
                st.rerun()

    st.divider()

    # ── 角色列表 ─────────────────────────────────────────
    st.markdown("### 📋 目前所有角色")
    roles = st.session_state.roles

    if not roles:
        st.info("尚未有任何角色。請使用上方表單新增。")
    else:
        for i, role in enumerate(roles):
            is_active = (i == st.session_state.active_role_idx)
            card_class = "role-card active-role" if is_active else "role-card"
            active_tag = " ✅ 使用中" if is_active else ""

            with st.container():
                col_info, col_use, col_del = st.columns([6, 1.5, 1.5])

                with col_info:
                    st.markdown(
                        f'<div class="{card_class}">'
                        f'<strong>{role["name"]}{active_tag}</strong>'
                        f'{role["prompt"][:120]}{"..." if len(role["prompt"]) > 120 else ""}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                with col_use:
                    if not is_active:
                        if st.button("切換", key=f"use_{i}", use_container_width=True):
                            switch_role(i)
                            st.session_state.page = PAGES[0]
                            st.rerun()
                    else:
                        st.markdown("　")

                with col_del:
                    if st.button("🗑️", key=f"del_{i}", use_container_width=True,
                                 help="刪除此角色"):
                        if len(roles) == 1:
                            st.error("至少保留一個角色！")
                        else:
                            st.session_state.roles.pop(i)
                            save_roles(st.session_state.roles)
                            if st.session_state.active_role_idx >= len(st.session_state.roles):
                                switch_role(0)
                            st.rerun()

    st.divider()
    st.caption("💡 角色資料儲存於 `roles.json`，重啟程式後仍會保留。")
