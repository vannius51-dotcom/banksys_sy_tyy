"""Tests for data_loader module."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.data_loader import (
    CATEGORICAL_COLS,
    NUMERIC_COLS,
    TARGET_COL,
    get_data_dir,
    get_missing_stats,
    load_test_data,
    load_train_data,
)


def test_get_data_dir_returns_path() -> None:
    """get_data_dir should return a Path object."""
    result = get_data_dir()
    assert isinstance(result, Path)


def test_load_train_data_file_not_found() -> None:
    """load_train_data raises FileNotFoundError for non-existent file."""
    with pytest.raises(FileNotFoundError, match="训练数据文件不存在"):
        load_train_data(path="/nonexistent/train.csv")


def test_load_test_data_file_not_found() -> None:
    """load_test_data raises FileNotFoundError for non-existent file."""
    with pytest.raises(FileNotFoundError, match="测试数据文件不存在"):
        load_test_data(path="/nonexistent/test.csv")


def test_numeric_cols_defined() -> None:
    """NUMERIC_COLS should be a non-empty list."""
    assert len(NUMERIC_COLS) > 0
    assert "age" in NUMERIC_COLS


def test_categorical_cols_defined() -> None:
    """CATEGORICAL_COLS should be a non-empty list."""
    assert len(CATEGORICAL_COLS) > 0
    assert "job" in CATEGORICAL_COLS


def test_target_col_is_subscribe() -> None:
    """TARGET_COL should be 'subscribe'."""
    assert TARGET_COL == "subscribe"


def test_get_missing_stats_empty() -> None:
    """get_missing_stats returns empty DataFrame when there are no missing values."""
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    result = get_missing_stats(df)
    assert len(result) == 0


def test_get_missing_stats_with_missing() -> None:
    """get_missing_stats returns correct stats for missing values."""
    df = pd.DataFrame({"a": [1, None, 3], "b": ["x", "y", None]})
    result = get_missing_stats(df)
    assert len(result) == 2
    assert result.loc[0, "缺失率(%)"] == pytest.approx(33.33, abs=0.1)
