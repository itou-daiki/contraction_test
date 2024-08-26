import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import io

def log_transform(x):
    return np.log1p(x)

def z_score_standardize(x):
    return stats.zscore(x)

def main():
    st.title("5件法と時間データの縮約アプリ")

    # 1. Excelファイルのアップロード
    uploaded_file = st.file_uploader("Excelファイルをアップロードしてください", type=["xlsx"])

    if uploaded_file is not None:
        # 2. Excelファイルをデータフレームに変換
        df = pd.read_excel(uploaded_file)
        st.write("データプレビュー:")
        st.write(df.head())

        # 3. 5件法のカラムと時間（分）のカラムを選択
        all_columns = df.columns.tolist()
        likert_columns = st.multiselect("5件法のカラムを選択してください", all_columns)
        time_columns = st.multiselect("時間（分）のカラムを選択してください", all_columns)

        # 4. 縮約後のカラム名を入力
        reduced_column_name = st.text_input("縮約後のカラム名を入力してください", "reduced_score")

        if likert_columns or time_columns:
            # 5. 処理を実行
            standardized_data = pd.DataFrame()

            # 5件法の変数を処理
            for col in likert_columns:
                standardized_data[f"{col}_standardized"] = z_score_standardize(df[col])

            # 時間（分）の変数を処理
            for col in time_columns:
                log_transformed = log_transform(df[col])
                standardized_data[f"{col}_standardized"] = z_score_standardize(log_transformed)

            # 縮約（平均化）
            df[reduced_column_name] = standardized_data.mean(axis=1)

            st.write("処理後のデータプレビュー:")
            st.write(df.head())

            # 処理済みデータの統計情報
            st.write("縮約されたカラムの統計情報:")
            st.write(df[[reduced_column_name]].describe())

            # 相関行列の表示
            st.write("元のカラムと縮約されたカラムの相関行列:")
            correlation_matrix = df[likert_columns + time_columns + [reduced_column_name]].corr()
            st.write(correlation_matrix)

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