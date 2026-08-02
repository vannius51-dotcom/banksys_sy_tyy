"""数据分析逻辑模块 — 提供统计概览、分布图、相关性、时间趋势等分析函数."""

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app.data_loader import CATEGORICAL_COLS, NUMERIC_COLS, TARGET_COL


def get_overview(df: pd.DataFrame) -> dict[str, Any]:
    """Compute data overview statistics.

    Args:
        df: Input DataFrame with bank marketing data.

    Returns:
        Dict with keys: row_count, col_count, pos_rate, pos_count, neg_count,
        numeric_count, categorical_count, missing_total.
    """
    total = len(df)
    pos_count = int((df[TARGET_COL] == "yes").sum())
    neg_count = total - pos_count
    pos_rate = pos_count / total * 100 if total > 0 else 0.0
    missing_total = int(df.isnull().sum().sum())

    return {
        "row_count": total,
        "col_count": df.shape[1],
        "pos_count": pos_count,
        "neg_count": neg_count,
        "pos_rate": round(pos_rate, 2),
        "numeric_count": len(NUMERIC_COLS),
        "categorical_count": len(CATEGORICAL_COLS),
        "missing_total": missing_total,
    }


def plot_numeric_distribution(
    df: pd.DataFrame, col: str, chart_type: str = "histogram"
) -> go.Figure:
    """Plot distribution of a numeric column, grouped by subscription status.

    Args:
        df: DataFrame containing the data.
        col: Name of the numeric column to plot.
        chart_type: "histogram" or "box".

    Returns:
        A plotly Figure object.
    """
    if chart_type == "histogram":
        fig = px.histogram(
            df,
            x=col,
            color=TARGET_COL,
            barmode="overlay",
            histnorm="percent",
            opacity=0.7,
            color_discrete_map={"yes": "#2ca02c", "no": "#d62728"},
            title=f"{col} 分布 (按认购状态分组)",
        )
    else:
        fig = px.box(
            df,
            x=TARGET_COL,
            y=col,
            color=TARGET_COL,
            color_discrete_map={"yes": "#2ca02c", "no": "#d62728"},
            title=f"{col} 箱线图 (按认购状态分组)",
        )
    fig.update_layout(template="plotly_white")
    return fig


def plot_categorical_distribution(df: pd.DataFrame, col: str) -> go.Figure:
    """Plot bar chart of a categorical column with subscription rates.

    Args:
        df: DataFrame containing the data.
        col: Name of the categorical column.

    Returns:
        A plotly Figure containing two subplots: count distribution and subscription rate.
    """
    # Count distribution
    count_df = df.groupby([col, TARGET_COL]).size().reset_index(name="count")

    # Subscription rate per category
    rate_df = (
        df.groupby(col)[TARGET_COL]
        .apply(lambda x: (x == "yes").mean() * 100)
        .reset_index(name="认购率(%)")
        .sort_values("认购率(%)", ascending=False)
    )

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(f"{col} 各类别数量分布", f"{col} 各类别认购率(%)"),
        specs=[[{"type": "bar"}, {"type": "bar"}]],
    )

    # Counts per category
    for status, color in [("yes", "#2ca02c"), ("no", "#d62728")]:
        sub = count_df[count_df[TARGET_COL] == status]
        fig.add_trace(
            go.Bar(
                name=status,
                x=sub[col],
                y=sub["count"],
                marker_color=color,
                showlegend=True,
            ),
            row=1,
            col=1,
        )

    # Subscription rate
    colors_rate = [
        "#2ca02c" if v > rate_df["认购率(%)"].mean() else "#d62728" for v in rate_df["认购率(%)"]
    ]
    fig.add_trace(
        go.Bar(
            x=rate_df[col],
            y=rate_df["认购率(%)"],
            marker_color=colors_rate,
            showlegend=False,
        ),
        row=1,
        col=2,
    )

    fig.update_layout(template="plotly_white", barmode="stack")
    return fig


def plot_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    """Plot correlation heatmap for numeric columns.

    Args:
        df: DataFrame containing the data.

    Returns:
        A plotly Figure with the correlation heatmap.
    """
    corr = df[NUMERIC_COLS].corr()
    fig = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="数值特征相关性热力图",
    )
    fig.update_layout(template="plotly_white")
    return fig


def plot_scatter(
    df: pd.DataFrame, x_col: str, y_col: str, color_by: str | None = None
) -> go.Figure:
    """Plot scatter plot of two numeric columns.

    Args:
        df: DataFrame containing the data.
        x_col: Column name for x-axis.
        y_col: Column name for y-axis.
        color_by: Optional column to color by (default: subscribe).

    Returns:
        A plotly Figure.
    """
    color = color_by or TARGET_COL
    fig = px.scatter(
        df.sample(min(2000, len(df)), random_state=42),
        x=x_col,
        y=y_col,
        color=color,
        opacity=0.6,
        color_discrete_map={"yes": "#2ca02c", "no": "#d62728"},
        title=f"{x_col} vs {y_col}",
    )
    fig.update_layout(template="plotly_white")
    return fig


def plot_time_trends(df: pd.DataFrame, dimension: str) -> go.Figure:
    """Plot subscription trends by month or day_of_week.

    Args:
        df: DataFrame containing the data.
        dimension: "month" or "day_of_week".

    Returns:
        A plotly Figure with the trend chart.
    """
    if dimension == "month":
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
        rate_df = (
            df.groupby("month")[TARGET_COL]
            .apply(lambda x: (x == "yes").mean() * 100)
            .reset_index(name="认购率(%)")
        )
        # Sort by calendar month
        rate_df["_order"] = rate_df["month"].apply(
            lambda m: month_order.index(m) if m in month_order else 99
        )
        rate_df = rate_df.sort_values("_order")
        title = "各月份认购率趋势"
    elif dimension == "day_of_week":
        day_order = ["mon", "tue", "wed", "thu", "fri"]
        rate_df = (
            df.groupby("day_of_week")[TARGET_COL]
            .apply(lambda x: (x == "yes").mean() * 100)
            .reset_index(name="认购率(%)")
        )
        rate_df["_order"] = rate_df["day_of_week"].apply(
            lambda d: day_order.index(d) if d in day_order else 99
        )
        rate_df = rate_df.sort_values("_order")
        title = "各星期几联系效果对比"
    else:
        raise ValueError(f"不支持的时间维度: {dimension}")

    # Also add contact count
    count_df = df.groupby(dimension).size().reset_index(name="联系次数")
    count_df = count_df.set_index(dimension).loc[rate_df[dimension].tolist()].reset_index()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            name="联系次数",
            x=rate_df[dimension],
            y=count_df["联系次数"],
            marker_color="#1f77b4",
            opacity=0.5,
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            name="认购率(%)",
            x=rate_df[dimension],
            y=rate_df["认购率(%)"],
            mode="lines+markers",
            marker_color="#2ca02c",
            line={"width": 3},
        ),
        secondary_y=True,
    )
    fig.update_layout(template="plotly_white", title=title)
    fig.update_yaxes(title_text="联系次数", secondary_y=False)
    fig.update_yaxes(title_text="认购率(%)", secondary_y=True)
    return fig
