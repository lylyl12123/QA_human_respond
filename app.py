import streamlit as st
import json
import os

# ===== 文件路径 =====
DATA_FILE = "data_human_respond_shuffled.json"     # 原始 200 条样本


@st.cache_data
def load_data():
    """加载样本数据（例如 200 条）"""
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = [data]
    return data


def main():
    # ===== 页面设置（尽量最先调用） =====
    st.set_page_config(page_title="教师答疑数据采集标注", layout="wide")

    st.title("📚 教师答疑数据采集界面")
    st.write("在该界面中，需要您作为一位擅长苏格拉底式答疑的老师。阅读下面的对话历史，对学生进行引导式解答：")
    st.write("  - 不要直接给出答案或完整解题步骤，而是通过提问引导学生进一步思考。")
    st.write("  - 每次只提出一个引导性问题，根据学生理解情况逐步推进。")
    st.write("  - 如果学生表现出不理解，请调整讲解方式，进一步拆解问题。")

    # ===== 加载数据 =====
    data = load_data()
    num_samples = len(data)

    # ===== 样本编号管理 =====
    if "current_idx" not in st.session_state:
        st.session_state["current_idx"] = 1

    st.sidebar.header("样本选择")

    col_prev, col_next = st.sidebar.columns(2)
    with col_prev:
        if st.button("⬅ 上一个"):
            if st.session_state["current_idx"] > 1:
                st.session_state["current_idx"] -= 1
    with col_next:
        if st.button("下一个 ➡"):
            if st.session_state["current_idx"] < num_samples:
                st.session_state["current_idx"] += 1

    idx = st.sidebar.number_input(
        "选择样本编号（从 1 开始）",
        min_value=1,
        max_value=num_samples,
        value=st.session_state["current_idx"],
        step=1,
    )
    st.session_state["current_idx"] = int(idx)
    idx = st.session_state["current_idx"]

    # ===== 当前样本 =====
    current = data[idx - 1]
    dialog_id = current.get("dialog_id", f"sample_{idx}")

    st.sidebar.markdown("---")
    st.sidebar.write(f"当前样本 ID：`{dialog_id}`")

    # ===== 主区域展示 =====
    st.subheader(f"样本 {idx} / {num_samples}")
    st.write(f"**dialog_id**: `{dialog_id}`")

    st.markdown("### 对话历史")
    for m in current.get("messages", []):
        role = m.get("role", "user")
        content = m.get("content", "")
        # 保证 role 合法：Streamlit chat_message 只官方支持 "user"/"assistant"/"system"
        if role not in ["user", "assistant", "system"]:
            role = "user"
        with st.chat_message(role):
            st.markdown(content)

    # ===== 教师填写回复 =====
    st.markdown("### ✍️ 请老师给出下一轮用于引导学生的对话")

    teacher_key = f"text_{dialog_id}"

    teacher_response = st.text_area(
        "教师回复内容：",
        value=st.session_state.get(teacher_key, ""),   # 用 session_state 保持输入
        height=200,
        key=teacher_key,
    )

    # 同步最新文本到 session_state（显式一点）
    st.session_state[teacher_key] = teacher_response

    # ===== 构建导出内容，并放到 session_state 里 =====
    record = dict(current)
    record["teacher_response"] = (teacher_response or "").strip()
    jsonl_str = json.dumps(record, ensure_ascii=False) + "\n"
    jsonl_bytes = jsonl_str.encode("utf-8")

    st.session_state["export_bytes"] = jsonl_bytes
    st.session_state["export_filename"] = f"{dialog_id}.jsonl"

    st.sidebar.markdown("### 💾 导出当前样本")

    # 增加一个小提示，方便你确认当前内容有没有生成
    with st.sidebar.expander("调试信息（可随时关掉）"):
        st.write("当前回复长度：", len(teacher_response or ""))
        #st.write("导出字节大小：", len(jsonl_bytes))

    st.sidebar.download_button(
        label="⬇ 下载当前样本 JSONL（含回复）",
        data=st.session_state["export_bytes"],
        file_name=st.session_state["export_filename"],
        mime="application/json",
        key=f"download_{dialog_id}",   # 给定稳定 key，避免重跑时混乱
    )


if __name__ == "__main__":
    main()
