import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    st.title("施工前・施工後の比較ツール")

    # サイドバーに入力セクションを配置
    with st.sidebar:
        st.header("入力セクション")

        # 施工前のCSVファイルのアップロード
        st.subheader("施工前のファイルをアップロード")
        pre_file = st.file_uploader("施工前のCSVファイルをアップロード", type=["csv"], key="pre_file")

        # 施工後のCSVファイルのアップロード
        st.subheader("施工後のファイルをアップロード")
        post_file = st.file_uploader("施工後のCSVファイルをアップロード", type=["csv"], key="post_file")

        # キロ程の範囲を手入力で指定
        start_kilo = st.number_input("キロ程の開始値を入力してください", value=0.0)
        end_kilo = st.number_input("キロ程の終了値を入力してください", value=100.0)

        # 計算する統計量を選択
        stat_options = ["平均", "中央値", "最大値", "最小値", "標準偏差", "分散", "四分位数（Q1）", "四分位数（Q3）"]
        selected_stat = st.selectbox("計算する統計量を選択してください", stat_options)

        # 図の種類を選択
        plot_type = st.selectbox("表示する図の種類を選択してください", ["折れ線グラフ", "棒グラフ", "散布図"])

        # 相関分析を表示するか
        show_correlation = st.checkbox("相関分析を表示する")

        # データフィルタリングの設定
        filter_enabled = st.checkbox("特定の条件でデータをフィルタリングする")
        if filter_enabled:
            filter_column = st.selectbox("フィルタリングする列を選択してください", [])
            filter_value = st.number_input("フィルタリングする値を入力してください", value=0.0)

    # メインエリアにデータの表示とチャートを配置
    if pre_file and post_file:
        try:
            # ファイルを読み込む
            df_pre = pd.read_csv(pre_file, encoding='shift_jis', on_bad_lines='skip')
            df_post = pd.read_csv(post_file, encoding='shift_jis', on_bad_lines='skip')

            st.write("施工前のデータプレビュー:")
            st.write(df_pre.head())
            st.write("施工後のデータプレビュー:")
            st.write(df_post.head())

            # 比較する列を選択
            common_columns = list(set(df_pre.columns).intersection(set(df_post.columns)))
            selected_column = st.selectbox("比較する列を選択してください", common_columns)

            if start_kilo <= end_kilo:
                st.write(f"キロ程範囲: {start_kilo} から {end_kilo}")
                
                # 施工前と施工後のデータをフィルタリング
                filtered_pre = df_pre[(df_pre['キロ程'] >= start_kilo) & (df_pre['キロ程'] <= end_kilo)]
                filtered_post = df_post[(df_post['キロ程'] >= start_kilo) & (df_post['キロ程'] <= end_kilo)]

                if filter_enabled and filter_column:
                    filtered_pre = filtered_pre[filtered_pre[filter_column] >= filter_value]
                    filtered_post = filtered_post[filtered_post[filter_column] >= filter_value]

                # 統計量の計算
                def calculate_stat(df, column, stat):
                    if stat == "平均":
                        return df[column].mean()
                    elif stat == "中央値":
                        return df[column].median()
                    elif stat == "最大値":
                        return df[column].max()
                    elif stat == "最小値":
                        return df[column].min()
                    elif stat == "標準偏差":
                        return df[column].std()
                    elif stat == "分散":
                        return df[column].var()
                    elif stat == "四分位数（Q1）":
                        return df[column].quantile(0.25)
                    elif stat == "四分位数（Q3）":
                        return df[column].quantile(0.75)

                stat_pre = calculate_stat(filtered_pre, selected_column, selected_stat)
                stat_post = calculate_stat(filtered_post, selected_column, selected_stat)
                st.write(f"施工前の {selected_column} の{selected_stat}は {stat_pre:.4f} です")
                st.write(f"施工後の {selected_column} の{selected_stat}は {stat_post:.4f} です")

                # 図のプロット
                fig, ax = plt.subplots()
                if plot_type == "折れ線グラフ":
                    ax.plot(filtered_pre['キロ程'], filtered_pre[selected_column], label='施工前', color='blue')
                    ax.plot(filtered_post['キロ程'], filtered_post[selected_column], label='施工後', color='red')
                elif plot_type == "棒グラフ":
                    ax.bar(filtered_pre['キロ程'], filtered_pre[selected_column], label='施工前', color='blue', alpha=0.6)
                    ax.bar(filtered_post['キロ程'], filtered_post[selected_column], label='施工後', color='red', alpha=0.6)
                elif plot_type == "散布図":
                    sns.scatterplot(x=filtered_pre['キロ程'], y=filtered_pre[selected_column], label='施工前', color='blue', ax=ax)
                    sns.scatterplot(x=filtered_post['キロ程'], y=filtered_post[selected_column], label='施工後', color='red', ax=ax)

                ax.set_xlabel('キロ程')
                ax.set_ylabel(selected_column)
                ax.set_title(f'{selected_column} の比較')
                ax.legend()

                st.pyplot(fig)

                # 相関分析の表示
                if show_correlation:
                    st.header("相関分析")
                    correlation_pre = filtered_pre[selected_column].corr(filtered_post[selected_column])
                    st.write(f"施工前と施工後の相関係数: {correlation_pre:.4f}")

            else:
                st.error("開始値は終了値以下である必要があります。")
        except Exception as e:
            st.error(f"ファイルの読み込み中にエラーが発生しました: {e}")
    else:
        st.info("施工前および施工後のCSVファイルをアップロードしてください。")

if __name__ == "__main__":
    main()
