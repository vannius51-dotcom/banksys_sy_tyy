"""模型训练与加载模块 — 二分类模型(认购/不认购)的训练、评估、序列化."""

import argparse
import logging
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ── Feature definitions ──────────────────────────────────
# Prediction features exclude "duration" — it is only known after the phone call.
PREDICTION_NUMERIC_COLS = [
    "age",
    "campaign",
    "pdays",
    "previous",
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr_employed",
]

PREDICTION_CATEGORICAL_COLS = [
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
MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_PATH = MODEL_DIR / "model.pkl"
PREPROCESSOR_PATH = MODEL_DIR / "preprocessor.pkl"


# ── Pipeline builder ─────────────────────────────────────
def build_preprocessor() -> ColumnTransformer:
    """Build a ColumnTransformer that scales numerics and one-hot encodes categoricals.

    Returns:
        Fitted-independent ColumnTransformer ready to be placed in a Pipeline.
    """
    numeric_transformer = Pipeline([("scaler", StandardScaler())])
    categorical_transformer = Pipeline(
        [
            (
                "onehot",
                OneHotEncoder(
                    drop="first", handle_unknown="ignore", sparse_output=False
                ),
            )
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, PREDICTION_NUMERIC_COLS),
            ("cat", categorical_transformer, PREDICTION_CATEGORICAL_COLS),
        ],
        remainder="drop",
    )
    return preprocessor


# ── Training ─────────────────────────────────────────────
def train_and_evaluate(
    df: pd.DataFrame,
) -> tuple[Pipeline, dict[str, float]]:
    """Train models and return the best-performing pipeline with its CV metrics.

    Uses StratifiedKFold (5-fold) to compare LogisticRegression vs RandomForest.
    The model with the higher mean ROC-AUC is chosen.

    Args:
        df: Training DataFrame containing features and target.

    Returns:
        Tuple of (best Pipeline, dict of test-set metrics).
    """
    X = df[PREDICTION_NUMERIC_COLS + PREDICTION_CATEGORICAL_COLS]
    y = df[TARGET_COL].map({"yes": 1, "no": 0})

    preprocessor = build_preprocessor()

    candidates: dict[str, Pipeline] = {
        "LogisticRegression": Pipeline(
            [
                ("preprocessor", preprocessor),
                (
                    "classifier",
                    LogisticRegression(
                        class_weight="balanced",
                        max_iter=2000,
                        random_state=42,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
        "RandomForest": Pipeline(
            [
                ("preprocessor", preprocessor),
                (
                    "classifier",
                    RandomForestClassifier(
                        class_weight="balanced",
                        random_state=42,
                        n_jobs=-1,
                        n_estimators=200,
                    ),
                ),
            ]
        ),
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    best_name = ""
    best_auc = -1.0
    best_model: Pipeline | None = None
    cv_results: dict[str, dict[str, float]] = {}

    for name, pipe in candidates.items():
        logger.info(f"Training {name} with 5-fold CV...")
        scores = cross_validate(
            pipe,
            X,
            y,
            cv=cv,
            scoring=["roc_auc", "f1", "recall"],
            n_jobs=-1,
            return_train_score=False,
        )
        mean_auc = float(np.mean(scores["test_roc_auc"]))
        mean_f1 = float(np.mean(scores["test_f1"]))
        mean_recall = float(np.mean(scores["test_recall"]))
        cv_results[name] = {"auc": mean_auc, "f1": mean_f1, "recall": mean_recall}
        logger.info(
            f"  {name}: AUC={mean_auc:.4f}, F1={mean_f1:.4f}, Recall={mean_recall:.4f}"
        )
        if mean_auc > best_auc:
            best_auc = mean_auc
            best_name = name
            best_model = pipe

    # Refit the best model on full training data
    logger.info(f"Refitting best model ({best_name}) on full training set...")
    best_model.fit(X, y)
    logger.info("Training complete.")

    return best_model, cv_results[best_name]


def evaluate_on_test(model: Pipeline, df_test: pd.DataFrame) -> dict[str, float]:
    """Evaluate a trained pipeline on the test set.

    Args:
        model: Trained scikit-learn Pipeline.
        df_test: Test DataFrame with features and target.

    Returns:
        Dict with keys: auc, f1, recall, accuracy.
    """
    X_test = df_test[PREDICTION_NUMERIC_COLS + PREDICTION_CATEGORICAL_COLS]
    y_test = df_test[TARGET_COL].map({"yes": 1, "no": 0})

    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)

    metrics = {
        "auc": float(roc_auc_score(y_test, y_prob)),
        "f1": float(f1_score(y_test, y_pred)),
        "recall": float(recall_score(y_test, y_pred)),
        "accuracy": float(accuracy_score(y_test, y_pred)),
    }

    logger.info("Test Set Evaluation:")
    logger.info(f"  AUC:      {metrics['auc']:.4f}")
    logger.info(f"  F1:       {metrics['f1']:.4f}")
    logger.info(f"  Recall:   {metrics['recall']:.4f}")
    logger.info(f"  Accuracy: {metrics['accuracy']:.4f}")
    logger.info(
        "\n" + classification_report(y_test, y_pred, target_names=["no", "yes"])
    )

    return metrics


# ── Serialization ────────────────────────────────────────
def save_model(model: Pipeline) -> None:
    """Save the trained pipeline to disk.

    Args:
        model: Trained Pipeline to persist.
    """
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    logger.info(f"Model saved to {MODEL_PATH}")


def load_model() -> Pipeline:
    """Load a trained pipeline from disk.

    Returns:
        Trained scikit-learn Pipeline.

    Raises:
        FileNotFoundError: If the model file does not exist.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"模型文件不存在: {MODEL_PATH}\n请先运行训练: python -m app.model --train"
        )
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    logger.info(f"Model loaded from {MODEL_PATH}")
    return model


# ── CLI entry point ──────────────────────────────────────
def main() -> None:
    """CLI entry point for model training and evaluation."""
    parser = argparse.ArgumentParser(description="银行营销认购预测模型训练")
    parser.add_argument(
        "--train",
        action="store_true",
        help="运行模型训练并在测试集上评估",
    )
    parser.add_argument(
        "--train-path",
        default=None,
        help="训练数据 CSV 路径 (默认: ./data/train.csv)",
    )
    parser.add_argument(
        "--test-path",
        default=None,
        help="测试数据 CSV 路径 (默认: ./data/test.csv)",
    )
    args = parser.parse_args()

    if not args.train:
        parser.print_help()
        return

    from app.data_loader import load_test_data, load_train_data

    logger.info("=" * 60)
    logger.info("开始模型训练流程")
    logger.info("=" * 60)

    # Load data
    df_train = load_train_data(path=args.train_path)
    df_test = load_test_data(path=args.test_path)
    logger.info(f"训练集: {len(df_train)} 行, 测试集: {len(df_test)} 行")

    # Train
    model, cv_metrics = train_and_evaluate(df_train)
    logger.info(f"CV Metrics: AUC={cv_metrics['auc']:.4f}, F1={cv_metrics['f1']:.4f}")

    # Evaluate on test
    test_metrics = evaluate_on_test(model, df_test)

    # Quality gate
    passed = test_metrics["auc"] >= 0.70 and test_metrics["f1"] >= 0.50
    status = "✅ PASS" if passed else "❌ FAIL"
    logger.info(f"质量门禁: {status} (AUC≥0.70, F1≥0.50)")

    if passed:
        save_model(model)
    else:
        logger.error("质量门禁未通过,模型未保存。请调整特征工程或算法参数。")
        sys.exit(1)


if __name__ == "__main__":
    main()
