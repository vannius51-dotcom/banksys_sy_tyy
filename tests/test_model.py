"""Tests for model module."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.model import (    PREDICTION_CATEGORICAL_COLS,
    PREDICTION_NUMERIC_COLS,
    build_preprocessor,
    evaluate_on_test,
    load_model,
    save_model,
    train_and_evaluate,
)


@pytest.fixture
def small_train_df() -> pd.DataFrame:
    """A 100-row synthetic DataFrame mimicking the bank marketing schema."""
    np.random.seed(42)
    n = 100
    data: dict[str, list] = {
        "age": np.random.randint(18, 70, n).tolist(),
        "campaign": np.random.randint(1, 10, n).tolist(),
        "pdays": np.random.choice([999, 5, 10, 20, 0], n).tolist(),
        "previous": np.random.randint(0, 5, n).tolist(),
        "emp_var_rate": np.random.uniform(-3, 3, n).tolist(),
        "cons_price_index": np.random.uniform(92, 96, n).tolist(),
        "cons_conf_index": np.random.uniform(-50, -30, n).tolist(),
        "lending_rate3m": np.random.uniform(0.5, 5, n).tolist(),
        "nr_employed": np.random.uniform(4900, 5300, n).tolist(),
        "job": _choice(["admin.", "blue-collar", "technician", "services"], n),
        "marital": _choice(["married", "single", "divorced"], n),
        "education": _choice(["high.school", "university.degree", "basic.9y"], n),
        "default": _choice(["no", "yes", "unknown"], n),
        "housing": _choice(["yes", "no", "unknown"], n),
        "loan": _choice(["yes", "no", "unknown"], n),
        "contact": _choice(["cellular", "telephone"], n),
        "month": _choice(["may", "jun", "jul", "aug"], n),
        "day_of_week": _choice(["mon", "tue", "wed", "thu", "fri"], n),
        "poutcome": _choice(["nonexistent", "failure", "success"], n),
        "subscribe": _choice_p(["yes", "no"], n, [0.13, 0.87]),
    }
    return pd.DataFrame(data)


def _choice(options: list, n: int) -> list:
    """Shorthand: np.random.choice(...).tolist()."""
    return np.random.choice(options, n).tolist()  # type: ignore[no-any-return]


def _choice_p(options: list, n: int, p: list[float]) -> list:
    """Shorthand: np.random.choice(...p=...).tolist()."""
    return np.random.choice(options, n, p=p).tolist()  # type: ignore[no-any-return]


@pytest.fixture
def small_test_df() -> pd.DataFrame:
    """A 30-row synthetic test DataFrame."""
    np.random.seed(99)
    n = 30
    data: dict[str, list] = {
        "age": np.random.randint(18, 70, n).tolist(),
        "campaign": np.random.randint(1, 10, n).tolist(),
        "pdays": np.random.choice([999, 5, 10, 20, 0], n).tolist(),
        "previous": np.random.randint(0, 5, n).tolist(),
        "emp_var_rate": np.random.uniform(-3, 3, n).tolist(),
        "cons_price_index": np.random.uniform(92, 96, n).tolist(),
        "cons_conf_index": np.random.uniform(-50, -30, n).tolist(),
        "lending_rate3m": np.random.uniform(0.5, 5, n).tolist(),
        "nr_employed": np.random.uniform(4900, 5300, n).tolist(),
        "job": _choice(["admin.", "blue-collar", "technician", "services"], n),
        "marital": _choice(["married", "single", "divorced"], n),
        "education": _choice(["high.school", "university.degree", "basic.9y"], n),
        "default": _choice(["no", "yes", "unknown"], n),
        "housing": _choice(["yes", "no", "unknown"], n),
        "loan": _choice(["yes", "no", "unknown"], n),
        "contact": _choice(["cellular", "telephone"], n),
        "month": _choice(["may", "jun", "jul", "aug"], n),
        "day_of_week": _choice(["mon", "tue", "wed", "thu", "fri"], n),
        "poutcome": _choice(["nonexistent", "failure", "success"], n),
        "subscribe": _choice_p(["yes", "no"], n, [0.13, 0.87]),
    }
    return pd.DataFrame(data)


def test_build_preprocessor() -> None:
    """build_preprocessor returns a ColumnTransformer."""
    preprocessor = build_preprocessor()
    assert preprocessor is not None


def test_feature_lists_exclude_duration() -> None:
    """Prediction feature lists must not include 'duration'."""
    assert "duration" not in PREDICTION_NUMERIC_COLS
    assert "duration" not in PREDICTION_CATEGORICAL_COLS


def test_train_and_evaluate_returns_pipeline_and_metrics(
    small_train_df: pd.DataFrame,
) -> None:
    """train_and_evaluate returns a Pipeline and metrics dict."""
    model, cv_metrics = train_and_evaluate(small_train_df)
    assert isinstance(model, Pipeline)
    assert "auc" in cv_metrics
    assert "f1" in cv_metrics
    assert 0.0 <= cv_metrics["auc"] <= 1.0


def test_evaluate_on_test_returns_metrics(
    small_train_df: pd.DataFrame, small_test_df: pd.DataFrame
) -> None:
    """evaluate_on_test returns valid metric values."""
    model, _ = train_and_evaluate(small_train_df)
    metrics = evaluate_on_test(model, small_test_df)
    assert "auc" in metrics
    assert "f1" in metrics
    assert "recall" in metrics
    assert 0.0 <= metrics["auc"] <= 1.0


def test_save_and_load_model(small_train_df: pd.DataFrame, tmp_path: Path) -> None:
    """save_model then load_model round-trips correctly."""
    import app.model as mod

    model, _ = train_and_evaluate(small_train_df)

    # Override paths to use tmp_path
    original_dir = mod.MODEL_DIR
    original_model_path = mod.MODEL_PATH
    mod.MODEL_DIR = tmp_path
    mod.MODEL_PATH = tmp_path / "model.pkl"

    try:
        save_model(model)
        assert mod.MODEL_PATH.exists()

        loaded = load_model()
        assert isinstance(loaded, Pipeline)
    finally:
        mod.MODEL_DIR = original_dir
        mod.MODEL_PATH = original_model_path


def test_load_model_file_not_found() -> None:
    """load_model raises FileNotFoundError when model does not exist."""
    with pytest.raises(FileNotFoundError, match="模型文件不存在"):
        load_model()


def test_predict_proba_shape(
    small_train_df: pd.DataFrame,
) -> None:
    """Trained model predict_proba returns correct shape."""
    model, _ = train_and_evaluate(small_train_df)
    X = small_train_df[PREDICTION_NUMERIC_COLS + PREDICTION_CATEGORICAL_COLS]
    proba = model.predict_proba(X)
    assert proba.shape == (len(small_train_df), 2)
