import streamlit as st
import json
from pathlib import Path
from datetime import datetime

# 保存先
DATA_DIR = Path("./app/data/")
DATA_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="収支記録", layout="centered")
st.title("📆 収支を記録しよう")

# 入力フォーム
today = datetime.today().date()
col1, col2 = st.columns(2)
date = col1.date_input("日付", value=today)
kind = col2.radio("区分", ["支出", "収入"], horizontal=True)

amount = st.number_input("金額", min_value=0, step=100, format="%d")
note = st.text_input("メモ（自由入力）")

# 保存処理
if st.button("💾 記録する"):
    record = {
        "date": date.isoformat(),
        "kind": kind,
        "amount": amount,
        "note": note
    }
    month_key = date.strftime("%Y-%m")
    record_file = DATA_DIR / f"records_{month_key}.json"

    if record_file.exists():
        with open(record_file, "r", encoding="utf-8") as f:
            records = json.load(f)
    else:
        records = []

    records.append(record)
    with open(record_file, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    st.success("記録しました！")

# 記録表示
if st.checkbox("📋 今月の記録を見る"):
    month_key = date.strftime("%Y-%m")
    record_file = DATA_DIR / f"records_{month_key}.json"

    if record_file.exists():
        with open(record_file, "r", encoding="utf-8") as f:
            records = json.load(f)

        st.subheader(f"{month_key} の記録一覧")
        total_income = sum(r["amount"] for r in records if r["kind"] == "収入")
        total_expense = sum(r["amount"] for r in records if r["kind"] == "支出")
        st.write(f"💰 合計収入: ¥{total_income:,}")
        st.write(f"💸 合計支出: ¥{total_expense:,}")
        st.write(f"📊 差額: ¥{total_income - total_expense:,}")

        for r in records:
            st.markdown(f"- {r['date']}｜{r['kind']}：¥{r['amount']:,}（{r['note']}）")
    else:
        st.info("まだ記録がありません。")