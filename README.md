# banksys_sy_tyy

银行营销数据分析与定期认购预测系统。

## 功能

- 📊 **数据分析看板** — 交互式探索银行电话营销数据，多维度可视化
- 🔮 **在线预测系统** — 基于机器学习模型，点选输入客户画像，实时预测认购意向

## 技术栈

Python 3.11 · Streamlit · scikit-learn · pytest · ruff · Docker

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt -r requirements-dev.txt

# 训练模型
python -m app.model --train

# 启动应用
streamlit run app/main.py

# 运行测试
pytest --cov --cov-fail-under=80
```

## 访问

http://localhost:8899

## 项目结构

详见 `standards/00-project-context.md`
