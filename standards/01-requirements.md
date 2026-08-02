# 01 · 需求 / 活 PRD 〔本项目活记忆 · AI 维护〕

> **作用**:这是本项目唯一的需求文档。所有新功能、缺陷、技术债都追加到这里,不要另起多个 PRD 文件。
> **更新时机**:每次有新需求、需求变更、验收标准变化时更新。

---

## 1. 需求来源

| 类型 | 来源 | 进入方式 |
|---|---|---|
| 功能需求 Feature | 用户 / 课程要求 | 写成用户故事 |
| 缺陷 Bug | 测试 / 线上日志 / 用户反馈 | 写复现步骤和期望结果 |
| 技术债 Tech Debt | 开发 / Review / CI/CD 故障 | 写影响和修复目标 |

---

## 2. Issue 生命周期

| 阶段 | 状态 | 动作 |
|---|---|---|
| 提出 | Open | 写清场景、目标、验收标准 |
| 排期 | Backlog / Todo | 决定优先级和负责人 |
| 开发 | In Progress | 从 main 开 feature 分支 |
| 评审 | In Review | 提 PR,等待 CI 和 Review |
| 合并 | Done | PR 合并 main,自动关闭 Issue |
| 验收 | Verified | 按验收标准确认 |

**追踪规则**:分支名带 Issue 号,PR 描述写 `closes #<编号>`。

---

## 3. 需求清单

### US-1 初始化项目工程化与 CI/CD · 状态: Backlog

作为 **项目开发者**,
我想要 项目具备基础工程结构、测试、CI 与 CD,
以便 后续每次开发都能自动检查并自动部署。

验收标准:
- AC1: Given 空仓库,When 从 `main` 开 feature 分支完成初始化,Then 项目拥有完整目录结构(见 `00` 目录地图)、依赖声明(`requirements.txt` + `requirements-dev.txt`)、Dockerfile、`.gitignore`、CI/CD workflow。
- AC2: Given 提交 PR,When CI 被触发,Then 至少执行 `ruff format --check .`、`ruff check .`、`pytest --cov --cov-fail-under=80`、`docker build` 并全部通过。
- AC3: Given CI 全绿,When 人工 Review 通过并合并 main,Then CD 自动触发,SSH 到服务器构建镜像并启动容器。
- AC4: Given 容器已启动,When CD 执行健康检查,Then `curl http://localhost:8899/_stcore/health` 返回 200。
- AC5: Given 项目初始化完成,When 会话结束,Then `standards/PROGRESS.md` 已更新最新状态与 TODO。

---

### US-2 数据分析交互页面 · 状态: Backlog

作为 **银行业务分析师**,
我想要 在 Web 页面中交互式地探索银行营销数据,
以便 快速理解客户特征分布、识别影响认购的关键因素,为营销决策提供数据支撑。

验收标准:
- AC1: Given 应用已启动,When 访问首页(数据分析页),Then 页面显示数据概览:总行数、特征数、认购率(yes/no 占比)、缺失值统计。
- AC2: Given 数据分析页,When 用户选择一个数值特征,Then 页面展示该特征的直方图/箱线图,并按 `subscribe` 分组着色以便对比。
- AC3: Given 数据分析页,When 用户选择一个类别特征,Then 页面展示该特征的柱状图/饼图,显示各类别认购率。
- AC4: Given 数据分析页,When 用户选择两个数值特征,Then 页面展示散点图/相关性热力图。
- AC5: Given 数据分析页,When 用户切换时间维度(month/day_of_week),Then 页面展示按月份的认购趋势、按星期几的联系效果对比。
- AC6: Given 数据分析页,When 数据文件存在且格式正确,Then 页面成功加载;When 数据缺失,Then 页面给出明确错误提示,不白屏。

技术备注:
- 使用 Streamlit + plotly 实现,图表须可交互(缩放、悬停提示)。
- 页面需有合理的加载状态(spinner),数据量大时分批渲染。
- 数据文件路径通过环境变量 `DATA_DIR` 配置,默认 `./data`。

---

### US-3 离线模型训练模块 · 状态: Backlog

作为 **数据科学家**,
我想要 基于历史营销数据训练一个二分类模型来预测客户是否会认购定期存款,
以便 后续将模型导出供在线预测系统使用。

验收标准:
- AC1: Given `data/train.csv` 存在,When 运行训练脚本,Then 完成数据预处理(缺失值填充、类别编码、标准化)并输出处理后的特征矩阵与标签。
- AC2: Given 预处理后的数据,When 训练模型,Then 至少尝试 2 种算法(如逻辑回归 + 随机森林),使用交叉验证评估,输出并对比 AUC、F1、召回率。
- AC3: Given 训练完成,When 保存模型,Then 模型序列化为 `models/model.pkl`,同时保存特征名称列表与预处理管道(如 `models/preprocessor.pkl`)以保证预测时特征一致。
- AC4: Given 模型已保存,When 对 `data/test.csv` 做评估,Then 输出测试集上的 AUC ≥ 0.70 且 F1 ≥ 0.50,结果记录到终端日志。
- AC5: Given 训练模块,When `pytest` 运行,Then 模型训练和评估的核心函数有单元测试覆盖(使用 mock 小数据集或采样数据)。

技术备注:
- 数据不平衡(yes ≈ 13%),训练时需使用 class_weight 或 SMOTE 等策略。
- 特征 `duration`(通话时长)在真实预测场景中不可知(电话打完才知道),在线预测时不使用该特征;训练时保留用于分析但预测管道需排除。
- 训练脚本独立于 Streamlit,可命令行运行:`python -m app.model --train`。

---

### US-4 在线预测系统 · 状态: Backlog

作为 **银行营销人员**,
我想要 在 Web 页面中通过点选方式输入客户信息,
以便 系统即时返回该客户是否会认购定期存款的预测结果,辅助我在实际营销中优先联系高意向客户。

验收标准:
- AC1: Given 应用已启动,When 用户导航到预测页面,Then 页面展示一个表单,包含所有预测所需特征(不含 `duration`、`subscribe`、`id`),每个特征以适合其类型的控件展示:
  - 数值特征(age, campaign, pdays, previous, emp_var_rate, cons_price_index, cons_conf_index, lending_rate3m, nr_employed):数字输入框或滑块,带合理范围限制。
  - 类别特征(job, marital, education, default, housing, loan, contact, month, day_of_week, poutcome):下拉选择框,选项来源于训练数据中的实际取值。
- AC2: Given 用户已填写所有字段,When 点击"预测"按钮,Then 系统调用已训练的模型,返回预测结果(认购/不认购)及置信度概率,并以醒目的视觉样式展示(如绿色=会认购、红色=不会认购)。
- AC3: Given 用户未填写必填字段,When 点击"预测",Then 系统给出校验提示,指明缺失字段,不发起预测。
- AC4: Given 用户输入超出合理范围的值,When 点击"预测",Then 系统给出警告但仍允许预测(或拒绝并提示修正 — 按特征类型决定)。
- AC5: Given 模型文件(`models/model.pkl`)缺失或加载失败,When 进入预测页面,Then 页面给出明确提示"模型未就绪,请先运行训练",而非崩溃或白屏。
- AC6: Given 预测页面,When 用户点击"重置"按钮,Then 所有表单字段恢复默认值。

技术备注:
- 模型在应用启动时加载一次,放入 `st.cache_resource` 避免每次请求重新加载。
- 预测时不使用 `duration` 特征(该特征在实际拨打电话前不可知),训练管道与预测管道需分别处理。
- 类别特征的选项列表从训练数据中动态提取并硬编码为常量,避免在线加载原始数据。

---

## 4. 非功能需求

- **安全**:密钥只进 Secrets,不进 Git;模型文件与数据文件不进 Git。
- **可维护**:一需求一小 PR,每个 PR 不超过约 400 行;分支命名 `feature/<issue>-<desc>`。
- **可测试**:核心逻辑(数据加载、特征工程、模型训练、预测)必须有单元测试,覆盖率 ≥ 80%。
- **可部署**:Docker 容器化部署,端口 8899(主机) → 8501(容器);CD 部署后必须有健康检查。
- **性能**:Streamlit 页面首次加载 ≤ 5 秒;单次预测响应 ≤ 2 秒。
- **兼容性**:应用在 Python 3.11、主流浏览器(Chrome/Firefox/Edge 最新版)上正常运行。
