import streamlit as st
import json
import os

DATA_FILE = "data_human_respond_shuffled.json"
OUTPUT_FILE = "data_human_respond_with_teacher.json"


@st.cache_data
def load_data():
    """加载 200 条样本"""
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = [data]
    return data


def load_teacher_responses():
    """
    加载已有的教师回复，返回 dict: dialog_id -> teacher_response(str)
    对于 None 或其他非字符串，统一转为 ""
    """
    if not os.path.exists(OUTPUT_FILE):
        return {}
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        saved = json.load(f)

    mapping = {}
    for item in saved:
        did = item.get("dialog_id")
        tr = item.get("teacher_response")
        if did:
            mapping[did] = tr if isinstance(tr, str) else ""
    return mapping


def save_teacher_responses(data, teacher_map):
    merged = []
    for item in data:
        did = item.get("dialog_id")
        new_item = dict(item)
        if did in teacher_map:
            new_item["teacher_response"] = teacher_map[did]
        merged.append(new_item)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)


def main():
    st.set_page_config(page_title="教师答疑数据采集标注", layout="wide")
    st.title("📚 教师答疑数据采集界面")
    st.write("在该界面中，需要您作为一位擅长苏格拉底式答疑的老师。阅读下面的对话历史，对学生进行引导式解答：")
    st.write("  - 不要直接给出答案或完整解题步骤，而是通过提问引导学生进一步思考。")
    st.write("  - 每次只提出一个引导性问题，根据学生理解情况逐步推进。")
    st.write("  - 如果学生表现出不理解，请调整讲解方式，进一步拆解问题。")

    data = load_data()
    teacher_map = load_teacher_responses()
    num_samples = len(data)

    # ===== 用 session_state 管理当前样本编号 =====
    if "current_idx" not in st.session_state:
        st.session_state["current_idx"] = 1

    # ===== 左侧栏 =====
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

    current = data[idx - 1]
    dialog_id = current.get("dialog_id", f"sample_{idx}")

    st.sidebar.markdown("---")
    st.sidebar.write(f"当前样本 ID：`{dialog_id}`")

    # ===== 保存按钮移到左侧 =====

    # 构造 JSONL 记录
    temp_teacher_resp = teacher_map.get(dialog_id, "")
    record = dict(current)
    record["teacher_response"] = temp_teacher_resp.strip()
    jsonl_str = json.dumps(record, ensure_ascii=False) + "\n"

    st.sidebar.markdown("### 💾 下载当前样本")
    st.sidebar.download_button(
        label="保存并下载 JSONL",
        data=jsonl_str.encode("utf-8"),
        file_name=f"{dialog_id}.jsonl",
        mime="application/json",
    )

    # ===== 主区域展示 =====
    st.subheader(f"样本 {idx} / {num_samples}")
    st.write(f"**dialog_id**: `{dialog_id}`")

    st.markdown("### 对话历史")
    for m in current.get("messages", []):
        role = m.get("role", "user")
        content = m.get("content", "")
        with st.chat_message(role):
            st.markdown(content)

    st.markdown("### ✍️ 请老师给出下一轮用于引导学生的对话")

    default_text = teacher_map.get(dialog_id, "")
    if not isinstance(default_text, str):
        default_text = ""

    teacher_response = st.text_area(
        "教师回复内容：",
        value=default_text,
        height=200,
        key=f"text_{dialog_id}",
    )


if __name__ == "__main__":
    main()
