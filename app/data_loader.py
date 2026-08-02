"""数据加载模块 — 从 data/ 目录加载银行营销 CSV 数据."""

import os
from pathlib import Path

import pandas as pd
import streamlit as st

# Column definitions based on the bank marketing dataset
NUMERIC_COLS = [
    "age",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr_employed",
]

CATEGORICAL_COLS = [
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "poutcome",
]

TARGET_COL = "subscribe"
ID_COL = "id"


def get_data_dir() -> Path:
    """Return the configured data directory path."""
    return Path(os.environ.get("DATA_DIR", "./data"))


def get_train_path() -> Path:
    """Return path to train.csv."""
    return get_data_dir() / "train.csv"


def get_test_path() -> Path:
    """Return path to test.csv."""
    return get_data_dir() / "test.csv"


@st.cache_data(show_spinner="正在加载数据...")
def load_train_data(path: str | None = None) -> pd.DataFrame:
    """Load the training dataset from CSV.

    Args:
        path: Optional override path to train.csv.

    Returns:
        DataFrame with the training data.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
    """
    filepath = Path(path) if path else get_train_path()
    if not filepath.exists():
        raise FileNotFoundError(f"训练数据文件不存在: {filepath}")
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip()
    return df


@st.cache_data(show_spinner="正在加载数据...")
def load_test_data(path: str | None = None) -> pd.DataFrame:
    """Load the test dataset from CSV.

    Args:
        path: Optional override path to test.csv.

    Returns:
        DataFrame with the test data.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
    """
    filepath = Path(path) if path else get_test_path()
    if not filepath.exists():
        raise FileNotFoundError(f"测试数据文件不存在: {filepath}")
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip()
    return df


def get_missing_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Compute missing-value statistics for a DataFrame.

    Args:
        df: Input DataFrame.

    Returns:
        DataFrame with columns: 特征, 缺失数, 缺失率(%).
    """
    missing = pd.DataFrame(
        {
            "特征": df.columns,
            "缺失数": df.isnull().sum().values,
            "缺失率(%)": (df.isnull().sum() / len(df) * 100).round(2).values,
        }
    )
    missing = missing[missing["缺失数"] > 0].reset_index(drop=True)
    return missing
