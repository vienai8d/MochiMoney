import streamlit as st
import json
from pathlib import Path
from datetime import datetime


# 保存先ディレクトリ
DATA_DIR = Path("./app/data/")
DATA_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="月次予算の登録",
    page_icon="./assets/icon/mochi_icon_512.png",
    layout="centered",
)

st.title("📋 毎月の支出リストをつくろう！")
st.caption("毎月記録したい項目と、それぞれの予算を設定してね。")

# ファイル一覧取得
def list_budget_files():
    return sorted(DATA_DIR.glob("monthly_budget_*.json"), reverse=True)

# ──────────────── 初期化 ────────────────
if "items" not in st.session_state:
    st.session_state["items"] = []

if "edit_mode" not in st.session_state:
    st.session_state["edit_mode"] = False

# ──────────────── サイドバー ────────────────
with st.sidebar:
    st.header("📚 過去の予算を見る・編集する")
    files = list_budget_files()

    selected_file = st.selectbox(
        "ファイルを選ぶ",
        options=["（表示しない）"] + [f.name for f in files],
        key="view_select"
    )

    if selected_file != "（表示しない）":
        with open(DATA_DIR / selected_file, "r", encoding="utf-8") as f:
            past_data = json.load(f)

        st.write("**内容：**")
        for item in past_data:
            st.write(f"・{item['name']}: ¥{item['budget']:,}")

        if st.button("✏ 編集モードで開く"):
            st.session_state["items"] = past_data
            st.session_state["edit_mode"] = True
            st.success("編集モードでフォームに読み込みました。")

    st.divider()

    st.subheader("🗑 ファイル削除")
    file_to_delete = st.selectbox(
        "削除したいファイル",
        options=["（選択しない）"] + [f.name for f in files],
        key="delete_select"
    )

    if file_to_delete != "（選択しない）":
        if st.button("⚠ このファイルを削除する", type="primary"):
            try:
                (DATA_DIR / file_to_delete).unlink()
                st.success(f"{file_to_delete} を削除しました。")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"削除に失敗しました: {e}")

# ──────────────── 入力フォーム ────────────────

if not st.session_state["items"]:
    st.session_state["items"] = [{"name": "", "budget": 0}]

def add_item():
    st.session_state["items"].append({"name": "", "budget": 0})

# 入力欄の表示
for idx, item in enumerate(st.session_state["items"]):
    cols = st.columns([2, 1, 0.2])
    item["name"] = cols[0].text_input(f"項目名 {idx+1}", value=item.get("name", ""), key=f"name_{idx}")
    item["budget"] = cols[1].number_input(f"予算（円）", value=item.get("budget", 0), step=1000, key=f"budget_{idx}")
    if cols[2].button("🗑", key=f"delete_{idx}"):
        st.session_state["items"].pop(idx)
        st.experimental_rerun()

st.button("＋ 項目を追加する", on_click=add_item)

# 保存処理（編集モードと通常モードで分岐）
if st.session_state["edit_mode"]:
    if st.button("💾 編集内容を別名で保存"):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        save_path = DATA_DIR / f"monthly_budget_{timestamp}_edited.json"
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(st.session_state["items"], f, ensure_ascii=False, indent=2)
        st.success(f"編集内容を保存しました！（{save_path.name}）")
        st.session_state["edit_mode"] = False
else:
    if st.button("💾 この内容で保存"):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        save_path = DATA_DIR / f"monthly_budget_{timestamp}.json"
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(st.session_state["items"], f, ensure_ascii=False, indent=2)
        st.success(f"保存しました！（{save_path.name}）")