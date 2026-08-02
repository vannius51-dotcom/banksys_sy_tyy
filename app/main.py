"""banksys_sy_tyy — 银行营销数据分析与定期认购预测系统."""

import streamlit as st

st.set_page_config(
    page_title="银行营销分析系统",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏦 银行营销数据分析与认购预测系统")
st.markdown("""
欢迎使用银行营销分析系统。请通过侧边栏导航到各功能页面：

- 📊 **数据分析** — 交互式探索银行电话营销数据
- 🔮 **在线预测** — 基于机器学习模型，预测客户认购意向
""")
