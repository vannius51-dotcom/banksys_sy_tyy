"""在线预测页面 — 点选式表单输入客户画像,实时预测认购意向."""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.predict import make_prediction, render_prediction_form  # noqa: E402

st.set_page_config(page_title="在线预测", page_icon="🔮", layout="wide")

st.title("🔮 定期存款认购预测")
st.markdown("请填写客户信息,系统将基于历史数据训练的模型预测该客户是否会认购定期存款。")

# ── Check model availability ─────────────────────────────
try:
    from app.model import MODEL_PATH  # noqa: E402
except ImportError:
    st.error("无法导入模型模块,请检查项目结构。")
    st.stop()

if not MODEL_PATH.exists():
    st.warning(
        "⚠️ **模型未就绪** — 请先在命令行运行以下命令训练模型:\n\n"
        "```bash\npython -m app.model --train\n```\n\n"
        f"训练完成后模型将保存到 `{MODEL_PATH}`。"
    )
    st.stop()

# ── Render form ──────────────────────────────────────────
values = render_prediction_form()

col_btn1, col_btn2, _ = st.columns([1, 1, 4])
predict_clicked = col_btn1.button("🔮 预测", type="primary", use_container_width=True)
reset_clicked = col_btn2.button("🔄 重置", use_container_width=True)

if reset_clicked:
    st.rerun()

# ── Prediction result ────────────────────────────────────
if predict_clicked:
    # Validate: check for missing fields (shouldn't happen with defaults, but guard)
    missing = [
        k
        for k, v in values.items()
        if v is None or (isinstance(v, str) and v.strip() == "")
    ]
    if missing:
        st.error(f"❌ 以下字段未填写: {', '.join(missing)}")
    else:
        try:
            with st.spinner("正在分析..."):
                label, confidence = make_prediction(values)

            st.divider()
            st.subheader("📊 预测结果")

            if "会认购" in label:
                st.success(f"### {label}")
                st.metric("认购概率", f"{confidence:.1%}")
                st.progress(
                    min(float(confidence), 1.0), text=f"置信度 {confidence:.1%}"
                )
            else:
                st.error(f"### {label}")
                st.metric("认购概率", f"{confidence:.1%}")
                st.progress(
                    min(float(confidence), 1.0), text=f"置信度 {confidence:.1%}"
                )

            # Show input summary
            with st.expander("📋 查看输入详情"):
                col_a, col_b = st.columns(2)
                numeric_keys = list(values.keys())[:9]
                cat_keys = list(values.keys())[9:]
                with col_a:
                    st.markdown("**数值特征**")
                    for k in numeric_keys:
                        st.text(f"{k}: {values[k]}")
                with col_b:
                    st.markdown("**类别特征**")
                    for k in cat_keys:
                        st.text(f"{k}: {values[k]}")

        except FileNotFoundError as e:
            st.error(f"❌ {e}")
        except Exception as e:
            st.error(f"❌ 预测失败: {e}")
