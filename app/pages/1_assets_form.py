import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

st.title("📘 資産の月次入力")

# 保存先ディレクトリ
DATA_DIR = Path("./app/data/assets")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 年月選択（ドロップダウン形式）
this_year = datetime.today().year
this_month = datetime.today().month

year = st.selectbox("年", list(range(2020, 2031)), index=this_year - 2020)
month = st.selectbox("月", list(range(1, 13)), index=this_month - 1)

month_str = f"{year}-{month:02d}"
file_path = DATA_DIR / f"{month_str}.csv"

st.markdown(f"### 対象月：**{month_str}**")

# 📋 前月コピー機能
def get_prev_month(year, month):
    if month == 1:
        return (year - 1, 12)
    else:
        return (year, month - 1)

prev_year, prev_month = get_prev_month(year, month)
prev_month_str = f"{prev_year}-{prev_month:02d}"
prev_file_path = DATA_DIR / f"{prev_month_str}.csv"

if prev_file_path.exists():
    if not file_path.exists():
        if st.button(f"📋 前月（{prev_month_str}）からコピー"):
            prev_data = pd.read_csv(prev_file_path)
            prev_data.to_csv(file_path, index=False)
            st.success(f"{prev_month_str} のデータを {month_str} にコピーしました！")
    else:
        st.info(f"{month_str} はすでにデータがあります（コピーは上書きしません）")

# 資産入力フォーム
st.markdown("### 資産を入力してください")

account_name = st.text_input("アカウント名")
account_type = st.selectbox("アカウント種別", ["銀行口座", "証券口座", "その他"])
balance = st.number_input("残高（円）", min_value=0, step=1000)
note = st.text_input("備考（任意）")

if st.button("保存"):
    new_data = pd.DataFrame([{
        "account_name": account_name,
        "account_type": account_type,
        "balance": balance,
        "note": note
    }])

    if file_path.exists():
        existing = pd.read_csv(file_path)
        updated = pd.concat([existing, new_data], ignore_index=True)
    else:
        updated = new_data

    updated.to_csv(file_path, index=False)
    st.success(f"{month_str} の資産データを保存しました！")

# 編集可能な入力内容表示
if file_path.exists():
    st.markdown("### 現在の入力内容（編集可）")

    df = pd.read_csv(file_path)

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        key="editor"
    )

    if st.button("変更を保存"):
        edited_df.to_csv(file_path, index=False)
        st.success(f"{month_str} の内容を更新しました！")

    st.markdown("---")
    with st.expander("🗑️ この月のデータを削除する"):
        st.warning("この操作は取り消せません。本当に削除してもよいですか？")

        if st.button("⚠️ この月のデータを削除"):
            file_path.unlink()  # ファイル削除
            st.success(f"{month_str} のデータを削除しました。ページを再読み込みしてください。")