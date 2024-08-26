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

        # 3. すべてのカラムを表示
        all_columns = df.columns.tolist()
        st.write("利用可能なカラム:", all_columns)

        # 4. 縮約に使用するカラムを選択
        columns_to_reduce = st.multiselect("縮約に使用するカラムを選択してください", all_columns)

        # 5. 縮約後のカラム名を入力
        reduced_column_name = st.text_input("縮約後のカラム名を入力してください", "reduced_score")

        if columns_to_reduce:
            # 6. 処理を実行
            standardized_data = pd.DataFrame()

            for col in columns_to_reduce:
                if df[col].dtype in ['int64', 'float64']:
                    if df[col].min() >= 0 and df[col].max() <= 5:  # 5件法の判定
                        standardized_data[f"{col}_standardized"] = z_score_standardize(df[col])
                    else:  # 時間データの判定
                        log_transformed = log_transform(df[col])
                        standardized_data[f"{col}_standardized"] = z_score_standardize(log_transformed)
                else:
                    st.warning(f"{col} は数値データではないため、処理から除外されました。")

            # 縮約（平均化）
            df[reduced_column_name] = standardized_data.mean(axis=1)

            st.write("処理後のデータプレビュー:")
            st.write(df.head())

            # 処理済みデータの統計情報
            st.write("縮約されたカラムの統計情報:")
            st.write(df[[reduced_column_name]].describe())

            # 相関行列の表示
            st.write("元のカラムと縮約されたカラムの相関行列:")
            correlation_matrix = df[columns_to_reduce + [reduced_column_name]].corr()
            st.write(correlation_matrix)

            # ダウンロード用のデータフレームを作成
            columns_to_keep = [col for col in all_columns if col not in columns_to_reduce] + [reduced_column_name]
            df_download = df[columns_to_keep]

            # 処理済みデータのダウンロード
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_download.to_excel(writer, index=False, sheet_name='Sheet1')
            output.seek(0)
            st.download_button(
                label="処理済みデータをダウンロード（縮約に使用したカラムは削除済み）",
                data=output,
                file_name="processed_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()