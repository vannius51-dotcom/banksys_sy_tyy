"""Tests for analysis module."""

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.analysis import (  # noqa: E402
    get_overview,
    plot_categorical_distribution,
    plot_correlation_heatmap,
    plot_numeric_distribution,
    plot_scatter,
    plot_time_trends,
)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Create a minimal sample DataFrame matching the bank marketing schema."""
    return pd.DataFrame(
        {
            "age": [30, 45, 52, 28, 39],
            "duration": [120, 300, 180, 90, 250],
            "campaign": [1, 3, 2, 1, 4],
            "pdays": [999, 5, 999, 10, 999],
            "previous": [0, 2, 0, 1, 0],
            "emp_var_rate": [-1.8, 1.4, -0.5, 2.0, -1.2],
            "cons_price_index": [93.2, 94.1, 92.8, 95.0, 93.5],
            "cons_conf_index": [-40.0, -35.5, -42.1, -30.2, -38.0],
            "lending_rate3m": [1.5, 2.0, 1.8, 2.5, 1.6],
            "nr_employed": [5000.0, 5100.0, 5050.0, 5200.0, 4990.0],
            "job": ["admin.", "services", "blue-collar", "entrepreneur", "admin."],
            "marital": ["married", "single", "divorced", "married", "single"],
            "education": [
                "high.school", "university.degree", "basic.9y",
                "high.school", "university.degree",
            ],
            "default": ["no", "unknown", "no", "yes", "no"],
            "housing": ["yes", "no", "yes", "yes", "no"],
            "loan": ["no", "yes", "no", "yes", "no"],
            "contact": ["cellular", "cellular", "telephone", "cellular", "cellular"],
            "month": ["may", "jun", "jul", "aug", "may"],
            "day_of_week": ["mon", "tue", "wed", "thu", "fri"],
            "poutcome": ["nonexistent", "failure", "nonexistent", "success", "nonexistent"],
            "subscribe": ["no", "yes", "no", "yes", "no"],
        }
    )


def test_get_overview(sample_df: pd.DataFrame) -> None:
    """get_overview returns correct summary statistics."""
    result = get_overview(sample_df)
    assert result["row_count"] == 5
    assert result["pos_count"] == 2
    assert result["neg_count"] == 3
    assert result["pos_rate"] == 40.0
    assert result["col_count"] == 20


def test_get_overview_missing(sample_df: pd.DataFrame) -> None:
    """get_overview handles missing values."""
    sample_df.loc[0, "age"] = None
    result = get_overview(sample_df)
    assert result["missing_total"] == 1


def test_plot_numeric_distribution_histogram(sample_df: pd.DataFrame) -> None:
    """plot_numeric_distribution returns a Figure for histogram."""
    fig = plot_numeric_distribution(sample_df, "age", chart_type="histogram")
    assert isinstance(fig, go.Figure)


def test_plot_numeric_distribution_box(sample_df: pd.DataFrame) -> None:
    """plot_numeric_distribution returns a Figure for box plot."""
    fig = plot_numeric_distribution(sample_df, "age", chart_type="box")
    assert isinstance(fig, go.Figure)


def test_plot_categorical_distribution(sample_df: pd.DataFrame) -> None:
    """plot_categorical_distribution returns a Figure."""
    fig = plot_categorical_distribution(sample_df, "job")
    assert isinstance(fig, go.Figure)


def test_plot_correlation_heatmap(sample_df: pd.DataFrame) -> None:
    """plot_correlation_heatmap returns a Figure."""
    fig = plot_correlation_heatmap(sample_df)
    assert isinstance(fig, go.Figure)


def test_plot_scatter(sample_df: pd.DataFrame) -> None:
    """plot_scatter returns a Figure."""
    fig = plot_scatter(sample_df, "age", "duration")
    assert isinstance(fig, go.Figure)


def test_plot_time_trends_month(sample_df: pd.DataFrame) -> None:
    """plot_time_trends returns a Figure for month dimension."""
    fig = plot_time_trends(sample_df, "month")
    assert isinstance(fig, go.Figure)


def test_plot_time_trends_day_of_week(sample_df: pd.DataFrame) -> None:
    """plot_time_trends returns a Figure for day_of_week dimension."""
    fig = plot_time_trends(sample_df, "day_of_week")
    assert isinstance(fig, go.Figure)


def test_plot_time_trends_invalid_dimension(sample_df: pd.DataFrame) -> None:
    """plot_time_trends raises ValueError for unsupported dimension."""
    with pytest.raises(ValueError, match="不支持的时间维度"):
        plot_time_trends(sample_df, "invalid")
