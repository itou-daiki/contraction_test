import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import io

def log_transform(x, n):
    return np.log1p(x) / np.log1p(n)

def z_score_standardize(df, columns):
    scaler = StandardScaler()
    df[columns] = scaler.fit_transform(df[columns])
    return df

def main():
    st.title("時間データとリッカート尺度データの縮約アプリ")

    # 1. Excelファイルのアップロード
    uploaded_file = st.file_uploader("Excelファイルをアップロードしてください", type=["xlsx"])

    if uploaded_file is not None:
        # 2. Excelファイルをデータフレームに変換
        df = pd.read_excel(uploaded_file)
        st.write("データプレビュー:")
        st.write(df.head())

        # 3. 時間（分）のカラムとリッカート尺度のカラムを選択
        all_columns = df.columns.tolist()
        time_columns = st.multiselect("時間（分）のカラムを選択してください", all_columns)
        likert_columns = st.multiselect("リッカート尺度のカラムを選択してください", all_columns)

        # 4. log変換の最大値nを指定
        n = st.number_input("log変換の最大値nを指定してください（1以上の値）", min_value=1, value=5)

        if time_columns or likert_columns:
            # 5. 時間データにlog(x + 1)変換を適用（1～nの範囲）
            for col in time_columns:
                new_col_name = f"{col}_log"
                # データを1～nの範囲に正規化してからlog変換
                df[new_col_name] = df[col].clip(lower=1, upper=n)  # 1未満の値を1に、n超の値をnにクリップ
                df[new_col_name] = log_transform(df[new_col_name], n)

            # 6. Z-score標準化
            columns_to_standardize = [f"{col}_log" for col in time_columns] + likert_columns
            df = z_score_standardize(df, columns_to_standardize)

            # 7. 元のカラムを削除し、標準化されたデータを新規カラムとして挿入
            for col in time_columns:
                df = df.drop(columns=[col])
                df = df.rename(columns={f"{col}_log": f"{col}_standardized"})

            for col in likert_columns:
                df = df.rename(columns={col: f"{col}_standardized"})

            st.write("処理後のデータプレビュー:")
            st.write(df.head())

            # 処理済みデータの統計情報
            st.write("処理済みデータの統計情報:")
            st.write(df[[col for col in df.columns if col.endswith('_standardized')]].describe())

            # 処理済みデータのダウンロード
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
            output.seek(0)
            st.download_button(
                label="処理済みデータをダウンロード",
                data=output,
                file_name="processed_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()