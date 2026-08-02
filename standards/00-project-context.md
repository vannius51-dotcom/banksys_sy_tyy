# 00 · 项目上下文 〔本项目活记忆 · AI 维护〕

> **作用**:这是项目的"身份档案"。AI 接管项目时先读这里,了解项目目标、技术栈、目录、部署取值。
> **更新时机**:架构、技术栈、目录结构、端口、部署目录、重要约束变化时更新。

---

## 1. 项目是什么

- **项目名称**:`banksys_sy_tyy`
- **一句话目标**:基于银行电话营销数据,构建数据分析看板 + 定期认购预测在线服务。
- **使用者/受益者**:银行业务分析师、营销人员 — 通过数据洞察辅助营销决策,通过模型预测锁定高意向客户。
- **核心功能**:
  - **数据分析交互页面**:加载银行营销数据,提供多维度可视化探索(分布、相关性、时间趋势等),帮助业务人员快速理解数据特征。
  - **在线预测系统**:基于历史数据离线训练分类模型,构建 Web 表单(点选式输入),用户填写客户画像后实时返回"是否会认购定期存款"的预测结果。
- **输入/数据**(如有):
  - 来源:`data/` 目录,来自银行电话营销活动记录。
  - 文件:`train.csv`(22,500 行 × 22 列)、`test.csv`(7,500 行 × 22 列)、`bank_marketing_report.xlsx`(分析报告)。
  - 目标列:`subscribe`(yes/no),正类占比约 13.1%,属于不平衡二分类问题。
  - 特征:年龄、职业、婚姻状况、教育水平、信用违约、房贷、个人贷款、联系方式、联系月份、星期几、通话时长、营销活动联系次数、上次联系距今、之前联系次数、之前营销结果、就业变化率、消费价格指数、消费者信心指数、3 个月贷款利率、雇员人数。
  - 是否进 Git:不进 Git(已加入 `.gitignore`),本地使用。

## 2. 技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| 语言/运行时 | Python 3.11 | 课程指定;数据科学生态成熟 |
| Web/应用框架 | Streamlit | 课程指定;适合快速构建数据看板与交互式 ML 应用,纯 Python 无需前端 |
| 数据处理 | pandas、numpy | 表格数据 EDA 与特征工程标配 |
| 可视化 | plotly / matplotlib / seaborn | 配合 Streamlit 做交互式图表 |
| 机器学习 | scikit-learn | 经典二分类建模(逻辑回归/随机森林/XGBoost 备选) |
| 测试 | pytest | 课程指定;Python 生态主流测试框架 |
| 格式/静态检查 | ruff | 课程指定;Rust 实现,快且覆盖 format + lint |
| 打包/运行 | Docker | 课程指定;保证本地与服务器运行环境一致 |
| CI/CD | GitHub Actions | 通用、可视化、适合教学与团队协作 |

## 3. 目录地图

```text
banksys_sy_tyy/
├── standards/                  # AI 项目记忆与通用规范
├── data/                       # 银行营销数据(不进 Git)
│   ├── train.csv
│   ├── test.csv
│   └── bank_marketing_report.xlsx
├── app/                        # Streamlit 应用源码
│   ├── __init__.py
│   ├── main.py                 # 应用入口
│   ├── pages/                  # 多页面
│   │   ├── __init__.py
│   │   ├── 1_📊_数据分析.py     # 第 1 页:数据分析
│   │   └── 2_🔮_在线预测.py     # 第 2 页:在线预测
│   ├── data_loader.py          # 数据加载模块
│   ├── analysis.py             # 数据分析逻辑
│   ├── model.py                # 模型训练与加载模块
│   └── predict.py              # 预测逻辑
├── tests/                      # 测试目录
│   ├── __init__.py
│   ├── test_data_loader.py
│   ├── test_analysis.py
│   ├── test_model.py
│   └── test_predict.py
├── models/                     # 训练产物(不进 Git)
│   └── model.pkl
├── requirements.txt            # 生产运行依赖
├── requirements-dev.txt        # 本地/CI 检查依赖
├── Dockerfile                  # Docker 镜像构建
├── .dockerignore
├── .gitignore
├── .github/workflows/
│   ├── ci.yml
│   └── cd.yml
└── README.md
```

> 新增目录前先更新本节,避免项目越做越散。

## 4. 质量门槛

| 类型 | 本项目标准 |
|---|---|
| 格式检查 | `ruff format --check .` |
| 静态检查 | `ruff check .` |
| 单元测试 | `pytest` |
| 覆盖率 | `pytest --cov --cov-fail-under=80` |
| 构建 | `docker build` 成功(仅 CI;本地不强制) |
| 业务/模型指标 | AUC ≥ 0.70,F1 ≥ 0.50(不平衡数据,侧重召回与 AUC) |

## 5. 不变约束

- 密钥、密码、私钥、Token **绝不写进代码或文档**,只进 GitHub Secrets / 环境变量。
- 大文件(csv/xlsx)、模型产物(`models/*.pkl`)不进 Git,由 `.gitignore` 排除。
- `main` 分支受保护,日常开发必须走 feature 分支 + PR。
- CI 红灯不合并。
- Streamlit 应用端口:容器内 `8501`,主机映射 `8899`(预留 `8899-8910`)。
- 数据文件放在 `data/` 目录本地使用,不在 CI runner 上跑全量训练(CI 用 mock/小样本验证管道)。

## 6. 部署/CI 占位符取值

> `guides/` 和 workflow 里的通用占位符,在本项目里的真实值只写这里。

| 占位符 | 本项目取值 | 说明 |
|---|---|---|
| `<APP>` | `banksys_sy_tyy` | 应用名/镜像名/容器名 |
| `<DEPLOY_DIR>` | `/opt/banksys_sy_tyy` | 服务器部署目录 |
| `<PORT>` | `8899` | 主机服务端口 |
| `<PORT_MAX>` | `8910` | 主机端口回退上限 |
| `<CONTAINER_PORT>` | `8501` | 容器内 Streamlit 默认端口 |
| `<PYVER>` | `3.11` | Python 版本 |
| `<HEALTHCHECK>` | `/_stcore/health` | Streamlit 内置健康检查端点 |
| `<SSH_USER>` | `root` | 部署用户(按实际服务器调整) |
| `<SSH_HOST>` | 待填写 | 服务器公网 IP 或域名 |
