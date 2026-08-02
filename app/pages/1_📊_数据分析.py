"""数据分析页面 — 银行营销数据多维度可视化探索."""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Ensure the app package is importable when run as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.analysis import (
    get_overview,
    plot_categorical_distribution,
    plot_correlation_heatmap,
    plot_numeric_distribution,
    plot_scatter,
    plot_time_trends,
)
from app.data_loader import (
    CATEGORICAL_COLS,
    NUMERIC_COLS,
    get_missing_stats,
    load_train_data,
)

st.set_page_config(page_title="数据分析", page_icon="📊", layout="wide")

st.title("📊 银行营销数据分析")

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ 分析控制面板")

    analysis_mode = st.radio(
        "选择分析维度",
        [
            "📋 数据概览",
            "📈 数值特征分布",
            "📊 类别特征分析",
            "🔗 相关性分析",
            "📅 时间趋势",
        ],
    )

# ── Load data ────────────────────────────────────────────
try:
    df = load_train_data()
except FileNotFoundError as e:
    st.error(f"❌ 数据加载失败: {e}")
    st.info("请确认 `data/train.csv` 文件存在于项目根目录的 `data/` 文件夹下。")
    st.stop()

# ── 1. Data overview ─────────────────────────────────────
if analysis_mode == "📋 数据概览":
    st.header("📋 数据概览")

    overview = get_overview(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("总行数", f"{overview['row_count']:,}")
    col2.metric("特征数", overview["col_count"])
    col3.metric("认购率 (yes)", f"{overview['pos_rate']}%")
    col4.metric("缺失值总数", overview["missing_total"])

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("认购分布")
        subscribe_counts = df["subscribe"].value_counts()
        st.bar_chart(
            subscribe_counts,
            color=[
                "#2ca02c" if x == "yes" else "#d62728" for x in subscribe_counts.index
            ],
            horizontal=True,
        )
    with col_b:
        st.subheader("缺失值统计")
        missing = get_missing_stats(df)
        if missing.empty:
            st.success("✅ 数据集无缺失值")
        else:
            st.dataframe(missing, use_container_width=True)

    st.divider()
    st.subheader("数据预览 (前 100 行)")
    st.dataframe(df.head(100), use_container_width=True)

# ── 2. Numeric distribution ──────────────────────────────
elif analysis_mode == "📈 数值特征分布":
    st.header("📈 数值特征分布")

    col1, col2 = st.columns(2)
    with col1:
        selected_num = st.selectbox("选择数值特征", NUMERIC_COLS)
    with col2:
        chart_type = st.radio("图表类型", ["直方图", "箱线图"], horizontal=True)

    fig = plot_numeric_distribution(
        df, selected_num, chart_type="histogram" if chart_type == "直方图" else "box"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Basic stats
    st.subheader(f"📊 {selected_num} 统计摘要")
    stats = df[selected_num].describe()
    st.dataframe(stats, use_container_width=True)

# ── 3. Categorical analysis ──────────────────────────────
elif analysis_mode == "📊 类别特征分析":
    st.header("📊 类别特征分析")

    selected_cat = st.selectbox("选择类别特征", CATEGORICAL_COLS)

    fig = plot_categorical_distribution(df, selected_cat)
    st.plotly_chart(fig, use_container_width=True)

    # Cross-tab
    st.subheader("📋 交叉统计表")
    crosstab = pd.crosstab(df[selected_cat], df["subscribe"], normalize="index") * 100
    crosstab.columns = ["不认购(%)", "认购(%)"]
    st.dataframe(crosstab.style.format("{:.1f}%"), use_container_width=True)

# ── 4. Correlation analysis ──────────────────────────────
elif analysis_mode == "🔗 相关性分析":
    st.header("🔗 相关性分析")

    tab1, tab2 = st.tabs(["热力图", "散点图"])

    with tab1:
        fig = plot_correlation_heatmap(df)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            x_col = st.selectbox("X 轴", NUMERIC_COLS, key="scatter_x")
        with col2:
            y_col = st.selectbox(
                "Y 轴",
                NUMERIC_COLS,
                index=min(1, len(NUMERIC_COLS) - 1),
                key="scatter_y",
            )

        fig = plot_scatter(df, x_col, y_col)
        st.plotly_chart(fig, use_container_width=True)

# ── 5. Time trends ───────────────────────────────────────
elif analysis_mode == "📅 时间趋势":
    st.header("📅 时间趋势分析")

    time_dim = st.radio(
        "选择时间维度", ["month (月份)", "day_of_week (星期几)"], horizontal=True
    )

    dim = "month" if "month" in time_dim else "day_of_week"
    fig = plot_time_trends(df, dim)
    st.plotly_chart(fig, use_container_width=True)

    # Additional stats
    st.subheader("📋 详细数据")
    if dim == "month":
        month_order = [
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
        ]
    else:
        month_order = ["mon", "tue", "wed", "thu", "fri"]

    summary_rows = []
    for val in month_order:
        if val in df[dim].values:
            sub = df[df[dim] == val]
            summary_rows.append(
                {
                    dim: val,
                    "联系次数": len(sub),
                    "认购数": int((sub["subscribe"] == "yes").sum()),
                    "认购率(%)": round((sub["subscribe"] == "yes").mean() * 100, 2),
                }
            )
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)
