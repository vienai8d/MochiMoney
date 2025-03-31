import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from difflib import ndiff

# 保存先
DATA_DIR = Path("./app/data/")
DATA_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="月次予算の登録", layout="centered")

st.title("📋 毎月の支出リストをつくろう！")
st.caption("毎月記録したい項目と、それぞれの予算を設定してね。")

# ヘルパー関数
def list_budget_files():
    return sorted(DATA_DIR.glob("monthly_budget_*.json"), reverse=True)

def show_diff(original, updated):
    diffs = []
    for i, (o, u) in enumerate(zip(original, updated)):
        changes = []
        if o["name"] != u["name"]:
            changes.append(f"項目名: '{o['name']}' → '{u['name']}'")
        if o["budget"] != u["budget"]:
            changes.append(f"予算: ¥{o['budget']:,} → ¥{u['budget']:,}")
        if changes:
            diffs.append(f"#{i+1} " + " ／ ".join(changes))
    return diffs

# セッション状態
if "items" not in st.session_state:
    st.session_state["items"] = []
if "edit_mode" not in st.session_state:
    st.session_state["edit_mode"] = False
if "edit_filename" not in st.session_state:
    st.session_state["edit_filename"] = ""
if "edit_original" not in st.session_state:
    st.session_state["edit_original"] = []

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
            st.session_state["items"] = past_data.copy()
            st.session_state["edit_original"] = past_data.copy()
            st.session_state["edit_mode"] = True
            st.session_state["edit_filename"] = selected_file.replace(".json", "")
            st.success("編集モードで読み込みました。")

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
                st.rerun()
            except Exception as e:
                st.error(f"削除に失敗しました: {e}")

# ──────────────── 編集モード表示 ────────────────
if st.session_state["edit_mode"]:
    st.markdown(
        f"""<div style="background-color:#FF11CD;padding:10px;border-radius:10px;margin-bottom:20px;">
        ✏ <strong>編集モード</strong>：<code>{st.session_state["edit_filename"]}</code> を編集中です。
        </div>""",
        unsafe_allow_html=True
    )

# ──────────────── 入力フォーム ────────────────
if not st.session_state["items"]:
    st.session_state["items"] = [{"name": "", "budget": 0}]

def add_item():
    st.session_state["items"].append({"name": "", "budget": 0})

for idx, item in enumerate(st.session_state["items"]):
    cols = st.columns([2, 1, 0.2])
    item["name"] = cols[0].text_input(f"項目名 {idx+1}", value=item.get("name", ""), key=f"name_{idx}")
    item["budget"] = cols[1].number_input(f"予算（円）", value=item.get("budget", 0), step=1000, key=f"budget_{idx}")
    if cols[2].button("🗑", key=f"delete_{idx}"):
        st.session_state["items"].pop(idx)
        st.rerun()

st.button("＋ 項目を追加する", on_click=add_item)

# ──────────────── 保存処理 ────────────────
if st.session_state["edit_mode"]:
    # 差分表示
    diff = show_diff(st.session_state["edit_original"], st.session_state["items"])
    if diff:
        st.subheader("✏ 変更された内容")
        for line in diff:
            st.markdown(f"- {line}")
    else:
        st.info("変更はありません。")

    if st.button("💾 編集内容を別名で保存"):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        base = st.session_state["edit_filename"]
        save_path = DATA_DIR / f"{base}_{timestamp}_edited.json"
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(st.session_state["items"], f, ensure_ascii=False, indent=2)
        st.success(f"編集内容を保存しました！（{save_path.name}）")
        st.session_state["edit_mode"] = False
        st.session_state["edit_filename"] = ""
        st.session_state["edit_original"] = []
else:
    if st.button("💾 この内容で保存"):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        save_path = DATA_DIR / f"monthly_budget_{timestamp}.json"
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(st.session_state["items"], f, ensure_ascii=False, indent=2)
        st.success(f"保存しました！（{save_path.name}）")