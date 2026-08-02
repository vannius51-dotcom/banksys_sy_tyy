"""Smoke tests for the Streamlit app entry point."""

import sys
from pathlib import Path

# Ensure app is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_app_imports() -> None:
    """Verify core app modules are importable."""
    import app  # noqa: F401


def test_main_has_title() -> None:
    """Verify main.py contains the expected page config."""
    root = Path(__file__).resolve().parent.parent
    content = root.joinpath("app", "main.py").read_text(encoding="utf-8")
    assert "st.set_page_config" in content
    assert "银行营销" in content
