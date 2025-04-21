import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import calendar
from dateutil.relativedelta import relativedelta

# 定期性に基づいて対象月に金額を適用すべきか判定する関数
def should_include_this_month(frequency, start_month, end_month, target_month):
    def parse_ym(val):
        try:
            if isinstance(val, str) and val:
                return datetime.strptime(val, "%Y-%m")
            return None
        except:
            return None

    try:
        s = parse_ym(start_month)
        e = parse_ym(end_month)
        c = datetime.strptime(target_month, "%Y-%m")
        if s and c < s:
            return False
        if e and c > e:
            return False
        diff = (c.year - s.year) * 12 + (c.month - s.month) if s else 0
        if frequency == "once":
            return s and c.year == s.year and c.month == s.month
        if frequency == "monthly":
            return True
        elif frequency == "bimonthly":
            return diff % 2 == 0
        elif frequency == "quarterly":
            return diff % 3 == 0
        elif frequency == "semiannual":
            return diff % 6 == 0
        elif frequency == "annual":
            return diff % 12 == 0
        return False
    except:
        return False

# 保存先
DATA_DIR = Path("./app/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

st.title("📋 月次家計入力フォーム")

this_year = datetime.today().year
this_month = datetime.today().month

# 当月とデータファイルから年月を収集
existing_months = {
    f.stem for f in DATA_DIR.glob("*.csv")
    if f.stem.count("-") == 1 and f.stem.replace("-", "").isdigit()
}
# 当月も含める
current_month_str = f"{this_year}-{this_month:02d}"
existing_months.add(current_month_str)

# YYYY/MM 表記に変換して表示用リストを作成
year_month_options = sorted({m.replace("-", "/") for m in existing_months})
default_option = current_month_str.replace("-", "/")

st.markdown("#### 対象年月の選択")
manual_ym = st.text_input("手動入力（例：2024/07）", value="")
selected_ym_from_list = st.selectbox("リストから選択", year_month_options, index=year_month_options.index(default_option), disabled=manual_ym != "")

# バリデーション簡易化：手動入力が有効ならば形式をチェックして採用
import re

valid_manual_ym = re.fullmatch(r"\d{4}/(0[1-9]|1[0-2])", manual_ym)
if valid_manual_ym:
    selected_ym = manual_ym
else:
    if manual_ym:
        st.error("年月の形式が正しくありません。例：2024/07")
    selected_ym = selected_ym_from_list

# ファイル名形式に変換
month_str = selected_ym.replace("/", "-")
file_path = DATA_DIR / f"{month_str}.csv"

# ファイルが存在しない場合、コピー案内とボタン表示
# 前月の予測データを条件に応じてコピーし、新規ファイルを作成する処理
if not file_path.exists():
    st.warning("この月のデータはまだありません。必要であれば前月の予測データをコピーしてください。")
    if st.button("前月から予測データをコピーする"):
        prev_year = int(month_str[:4])
        prev_month = int(month_str[5:])
        if prev_month == 1:
            prev_year -= 1
            prev_month = 12
        else:
            prev_month -= 1
        prev_month_str = f"{prev_year}-{prev_month:02d}"
        prev_file_path = DATA_DIR / f"{prev_month_str}.csv"

        if prev_file_path.exists():
            prev_df = pd.read_csv(prev_file_path)
            
            excluded_rows = []
            filtered_rows = []
            for _, row in prev_df.iterrows():
                freq = row.get("frequency")
                sm = row.get("start_month")
                if freq == "once" and sm:
                    try:
                        start = datetime.strptime(sm, "%Y-%m")
                        current = datetime.strptime(month_str, "%Y-%m")
                        if start < current:
                            excluded_rows.append(row)
                            continue  # 過去のonceはコピー対象外
                    except:
                        pass  # 無効な日付は無視して続行
                filtered_rows.append(row)
            
            predicted_rows = pd.DataFrame(filtered_rows)

            if not predicted_rows.empty:
                pd.DataFrame(predicted_rows).to_csv(file_path, index=False)
                st.success("前月の予測データをコピーしました ✅")
                if excluded_rows:
                    st.markdown("#### 除外されたデータ（過去の`once`）")
                    st.dataframe(pd.DataFrame(excluded_rows))
            else:
                st.info("前月にコピー可能な予測データが見つかりませんでした。")
        else:
            st.info("前月のデータファイルが存在しません。")

st.markdown(f"### 対象月：**{month_str}**")

# データ削除ボタン
if file_path.exists():
    if st.button("🗑️ この月のデータを削除"):
        file_path.unlink()
        st.success("この月のデータを削除しました ✅")
        st.stop()

# 入力フォーム
with st.form("entry_form"):
    st.subheader("新規項目の追加")

    # 種別の選択（収入、支出、預金、貯蓄、投資、年金）
    type_ = st.selectbox("種別", ["income", "outgo", "outgo_saving", "deposit", "saving", "invest", "pension"])
    # 名前の入力（例：P_楽天カード、M_給与など）
    name = st.text_input("名前（例：P_楽天カード、M_給与など）")
    # 実績金額（actual_amount）の入力（万円単位）
    actual_amount = st.number_input("実績金額（万円）", min_value=0.0, step=0.0001, format="%.4f")
    # 予測金額（expected_amount）の入力（万円単位）
    expected_amount = st.number_input("予測金額（万円）", min_value=0.0, step=0.0001, format="%.4f")
    # 定期性の指定（毎月、隔月、1回など）
    frequency = st.selectbox("定期性", ["once", "monthly", "bimonthly", "quarterly", "semiannual", "annual"])
    start_month = st.text_input("開始月（例：2024-04）", value="")
    end_month = st.text_input("終了月（例：2025-12）", value="")

    submitted = st.form_submit_button("追加")

    if submitted:
        new_data = {
            "type": type_,
            "name": name,
            "actual_amount": actual_amount if actual_amount > 0 else "",
            "expected_amount": expected_amount if expected_amount > 0 else "",
            "frequency": frequency if frequency else "",
            "start_month": start_month,
            "end_month": end_month
        }

        if file_path.exists():
            df = pd.read_csv(file_path)
        else:
            df = pd.DataFrame(columns=new_data.keys())

        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df = df.sort_values(by=["type", "name"])  # 追加
        df.to_csv(file_path, index=False)
        st.success("データを保存しました ✅")

# 既存データの表示・編集
if file_path.exists():
    st.markdown("### 登録済みデータの編集")
    df = pd.read_csv(file_path)
    # 表示月の収支と資産総和を表示
    try:
        total_income = df.loc[df["type"] == "income", "actual_amount"].astype(float).sum()
        total_outgo = df.loc[df["type"] == "outgo", "actual_amount"].astype(float).sum()
        total_deposit = df.loc[df["type"] == "deposit", "actual_amount"].astype(float).sum()
        total_invest = df.loc[df["type"] == "investment", "actual_amount"].astype(float).sum()
        total_pension = df.loc[df["type"] == "pension", "actual_amount"].astype(float).sum()
        balance = total_income - total_outgo
        total_assets = total_deposit + total_invest + total_pension
        st.markdown(f"#### 💰 今月の収支：**{balance:.2f} 万円**")
        st.markdown(f"#### 📦 今月の資産合計：**{total_assets:.2f} 万円**")
    except:
        st.warning("収支・資産集計中にエラーが発生しました。")
    edited_df = st.data_editor(df, num_rows="dynamic")
    if st.button("変更を保存"):
        edited_df = edited_df.sort_values(by=["type", "name"])  # 追加
        edited_df.to_csv(file_path, index=False)
        st.success("変更を保存しました ✅")

# 翌月から3年後までのシミュレーション（予測値ベース）

# 表示月のデータを起点に、翌月から3年分の予測データを作成・プロットする
if "df" in locals() and not df.empty:
    # シミュレーション年数をフォームで指定（1～10年）
    sim_years = st.slider("シミュレーション年数", min_value=1, max_value=10, value=3, step=1)
    st.markdown(f"### 🔮 翌月から{sim_years}年後までのシミュレーション")
    start_dt = datetime.strptime(month_str, "%Y-%m") + relativedelta(months=1)
    future_months = [(start_dt + relativedelta(months=i)).strftime("%Y-%m") for i in range(sim_years * 12)]
    sim_data = pd.DataFrame(index=future_months, columns=["income", "outgo", "outgo_saving", "deposit", "saving", "investment", "pension"]).fillna(0.0)

    for _, row in df.iterrows():
        # 各type（income, outgo, deposit, saving, investment, pension）に対する処理
        if row["type"] not in sim_data.columns:
            continue
        if row["expected_amount"] == "":
            continue
        try:
            est_val = float(row["expected_amount"])
        except:
            continue
        for ym in future_months:
            # 各月に予測金額を加算（typeに応じて定期性チェック）
            if should_include_this_month(row.get("frequency", ""), row.get("start_month", ""), row.get("end_month", ""), ym):
                sim_data.loc[ym, row["type"]] += est_val

    # deposit, investment, pension の初期残高を設定
    cumulative_deposit = df.loc[df["type"] == "deposit", "actual_amount"].astype(float).sum()

    cumulative_investment = df.loc[df["type"] == "investment", "actual_amount"].astype(float).sum()
    cumulative_pension = df.loc[df["type"] == "pension", "actual_amount"].astype(float).sum()
    cumulative_saving = df.loc[df["type"] == "saving", "actual_amount"].astype(float).sum()

    for ym in future_months:
        net = sim_data.loc[ym, "income"] - sim_data.loc[ym, "outgo"]
        cumulative_deposit += net
        sim_data.loc[ym, "deposit"] += cumulative_deposit

        if "investment" in sim_data.columns:
            cumulative_investment += sim_data.loc[ym, "investment"]
            sim_data.loc[ym, "investment"] = cumulative_investment
        if "pension" in sim_data.columns:
            cumulative_pension += sim_data.loc[ym, "pension"]
            sim_data.loc[ym, "pension"] = cumulative_pension
        if "saving" in sim_data.columns:
            cumulative_saving += sim_data.loc[ym, "saving"]
            cumulative_saving -= sim_data.loc[ym, "outgo_saving"]
            sim_data.loc[ym, "saving"] = cumulative_saving

    st.line_chart(sim_data)
    # 総資産 = deposit + saving + investment + pension
    asset_total = sim_data[["deposit", "saving", "investment", "pension"]].sum(axis=1)
    st.markdown("### 🧮 総資産の推移（予測）")
    st.line_chart(asset_total)
