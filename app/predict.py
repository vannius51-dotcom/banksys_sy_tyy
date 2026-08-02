"""在线预测模块 — 表单字段定义、输入解析、模型推理."""

import logging
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

from app.model import PREDICTION_CATEGORICAL_COLS, PREDICTION_NUMERIC_COLS, load_model

logger = logging.getLogger(__name__)

# ── Form field definitions ──────────────────────────────
# Categorical options derived from the bank marketing dataset.
CATEGORICAL_OPTIONS: dict[str, list[str]] = {
    "job": [
        "admin.", "blue-collar", "entrepreneur", "housemaid",
        "management", "retired", "self-employed", "services",
        "student", "technician", "unemployed", "unknown",
    ],
    "marital": ["divorced", "married", "single", "unknown"],
    "education": [
        "basic.4y", "basic.6y", "basic.9y", "high.school",
        "illiterate", "professional.course", "university.degree", "unknown",
    ],
    "default": ["no", "yes", "unknown"],
    "housing": ["no", "yes", "unknown"],
    "loan": ["no", "yes", "unknown"],
    "contact": ["cellular", "telephone"],
    "month": [
        "jan", "feb", "mar", "apr", "may", "jun",
        "jul", "aug", "sep", "oct", "nov", "dec",
    ],
    "day_of_week": ["mon", "tue", "wed", "thu", "fri"],
    "poutcome": ["failure", "nonexistent", "success"],
}

# Numeric ranges: (min, max, default, step)
NUMERIC_RANGES: dict[str, tuple[float, float, float, float]] = {
    "age": (17, 98, 40, 1),
    "campaign": (1, 50, 1, 1),
    "pdays": (0, 999, 999, 1),
    "previous": (0, 10, 0, 1),
    "emp_var_rate": (-3.5, 3.5, 0.0, 0.1),
    "cons_price_index": (92.0, 96.0, 93.5, 0.01),
    "cons_conf_index": (-51.0, -26.0, -40.0, 0.1),
    "lending_rate3m": (0.5, 6.0, 2.0, 0.01),
    "nr_employed": (4900.0, 5300.0, 5100.0, 0.1),
}


# ── Form builder ─────────────────────────────────────────
def render_prediction_form() -> dict[str, Any]:
    """Render the prediction input form and return user-submitted values.

    Returns:
        Dict mapping feature name → value, or empty dict if form not yet submitted.
    """
    values: dict[str, Any] = {}

    st.subheader("👤 客户画像")
    col_a, col_b, col_c = st.columns(3)

    numeric_fields = list(NUMERIC_RANGES.keys())
    for i, col_name in enumerate(numeric_fields):
        min_v, max_v, default_v, step_v = NUMERIC_RANGES[col_name]
        # Distribute across 3 columns
        with [col_a, col_b, col_c][i % 3]:
            values[col_name] = st.number_input(
                label=f"{col_name}",
                min_value=float(min_v),
                max_value=float(max_v),
                value=float(default_v),
                step=float(step_v),
                key=f"pred_{col_name}",
            )

    st.divider()
    st.subheader("📋 客户背景")

    cat_fields = list(CATEGORICAL_OPTIONS.keys())
    col_d, col_e, col_f = st.columns(3)
    for i, col_name in enumerate(cat_fields):
        options = CATEGORICAL_OPTIONS[col_name]
        with [col_d, col_e, col_f][i % 3]:
            values[col_name] = st.selectbox(
                label=f"{col_name}",
                options=options,
                key=f"pred_{col_name}",
            )

    return values


# ── Prediction logic ─────────────────────────────────────
def make_prediction(form_values: dict[str, Any]) -> tuple[str, float]:
    """Run model inference on form inputs.

    Args:
        form_values: Dict of feature → value from the prediction form.

    Returns:
        Tuple of (prediction_label: "会认购" or "不会认购", confidence_probability: float).

    Raises:
        FileNotFoundError: If the model file is missing.
        Exception: If prediction fails for any reason.
    """
    # Load model (cached by Streamlit at page level)
    model = _get_model()

    # Build a single-row DataFrame in the expected column order
    feature_order = PREDICTION_NUMERIC_COLS + PREDICTION_CATEGORICAL_COLS
    input_data = {col: [form_values[col]] for col in feature_order}
    df = pd.DataFrame(input_data)

    # Predict
    proba: np.ndarray = model.predict_proba(df)
    yes_prob = float(proba[0, 1])
    predicted_class = int(model.predict(df)[0])

    label = "会认购 ✅" if predicted_class == 1 else "不会认购 ❌"
    return label, yes_prob


@st.cache_resource(show_spinner="正在加载预测模型...")
def _get_model():
    """Cached model loader — loads once per app session."""
    return load_model()
