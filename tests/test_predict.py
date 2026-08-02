"""Tests for predict module."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.predict import (  # noqa: E402
    CATEGORICAL_OPTIONS,
    NUMERIC_RANGES,
    PREDICTION_CATEGORICAL_COLS,
    PREDICTION_NUMERIC_COLS,
    make_prediction,
)


def test_categorical_options_covers_prediction_cols() -> None:
    """CATEGORICAL_OPTIONS must cover all PREDICTION_CATEGORICAL_COLS."""
    for col in PREDICTION_CATEGORICAL_COLS:
        assert col in CATEGORICAL_OPTIONS, f"Missing options for {col}"
        assert len(CATEGORICAL_OPTIONS[col]) > 1, f"Options for {col} too few"


def test_numeric_ranges_covers_prediction_cols() -> None:
    """NUMERIC_RANGES must cover all PREDICTION_NUMERIC_COLS."""
    for col in PREDICTION_NUMERIC_COLS:
        assert col in NUMERIC_RANGES, f"Missing range for {col}"
        min_v, max_v, default_v, step_v = NUMERIC_RANGES[col]
        assert min_v < max_v
        assert min_v <= default_v <= max_v


def test_make_prediction_returns_label_and_prob() -> None:
    """make_prediction returns correct types."""
    # Build mock model
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = np.array([[0.25, 0.75]])
    mock_model.predict.return_value = np.array([1])

    with patch("app.predict._get_model", return_value=mock_model):
        form_values: dict = {}
        for col in PREDICTION_NUMERIC_COLS:
            _, _, default_v, _ = NUMERIC_RANGES[col]
            form_values[col] = default_v
        for col in PREDICTION_CATEGORICAL_COLS:
            form_values[col] = CATEGORICAL_OPTIONS[col][0]

        label, prob = make_prediction(form_values)
        assert isinstance(label, str)
        assert isinstance(prob, float)
        assert 0.0 <= prob <= 1.0


def test_make_prediction_negative_result() -> None:
    """make_prediction returns '不会认购' when probability is low."""
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = np.array([[0.92, 0.08]])
    mock_model.predict.return_value = np.array([0])

    with patch("app.predict._get_model", return_value=mock_model):
        form_values: dict = {}
        for col in PREDICTION_NUMERIC_COLS:
            _, _, default_v, _ = NUMERIC_RANGES[col]
            form_values[col] = default_v
        for col in PREDICTION_CATEGORICAL_COLS:
            form_values[col] = CATEGORICAL_OPTIONS[col][0]

        label, prob = make_prediction(form_values)
        assert "不会认购" in label
        assert prob == pytest.approx(0.08)
