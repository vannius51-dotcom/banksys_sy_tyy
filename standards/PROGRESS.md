# PROGRESS · banksys_sy_tyy 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-08-02 · by Claude)

- **阶段**:`初始化 — 六步流程第 ① 步前(需求确认中)`
- **上一步完成**:`standards/00-project-context.md 与 01-requirements.md 已填写初稿`
- **下一步 (TODO 第一条)**:`人工确认需求文档与项目上下文,确认后进入第 ① 步(建仓 + 配 Secrets)`
- **阻塞项**:`等待人工 Review 并确认 standards/00 与 01 内容无误`

---

## 待办清单 (TODO,按优先级)

- [ ] **人工确认**:阅读并确认 `standards/00-project-context.md` 与 `standards/01-requirements.md`
- [ ] **① 建仓 + 配 Secrets**:用 `gh` 创建 GitHub 仓库 `banksys_sy_tyy`(开源);提示人类配置 `SSH_PRIVATE_KEY` / `SSH_HOST` / `SSH_USER` 三个 Secrets
- [ ] **② 开 feature 分支**:从 `main` 切 `feature/1-project-init`,完成工程化骨架
- [ ] **③ 模块 1 — 项目骨架**:目录结构、`requirements.txt`、`requirements-dev.txt`、`Dockerfile`、`.gitignore`、`.dockerignore`、CI/CD workflow(ci.yml + cd.yml)
- [ ] **③ 模块 2 — US-2 数据分析页**:`data_loader.py` + `analysis.py` + `pages/1_📊_数据分析.py` + 测试
- [ ] **③ 模块 3 — US-3 模型训练**:`model.py` + 训练脚本 + 评估逻辑 + 测试
- [ ] **③ 模块 4 — US-4 在线预测**:`predict.py` + `pages/2_🔮_在线预测.py` + 测试
- [ ] **④ 本地 CI 自检**:`ruff format --check .` + `ruff check .` + `pytest --cov --cov-fail-under=80`
- [ ] **⑤ 触发 PR**:push + `gh pr create`;CI 在 PR 上复检(含 `docker build`)
- [ ] **⑥ 人工审核 → 合并 → CD**:人工 Review + Merge → CD 自动部署 → 健康检查 `http://<HOST>:8899/_stcore/health`
- [ ] 会话结束前更新本文件

---

## 关键决策记录 (ADR)

| 日期 | 决策 | 理由 |
|---|---|---|
| 2026-08-02 | 技术栈:Python 3.11 + Streamlit + scikit-learn + Docker | 课程指定;Streamlit 适合数据应用快速构建 |
| 2026-08-02 | 端口:主机 8899 → 容器 8501,预留 8899-8910 | 课程指定 8899;回退区间避免端口冲突 |
| 2026-08-02 | 模型训练排除 `duration` 特征用于在线预测 | `duration` 在电话完成后才知道,真实预测场景不可用 |
| 2026-08-02 | 模型指标底线:AUC ≥ 0.70,F1 ≥ 0.50 | 数据不平衡(yes ≈ 13%),侧重召回与排序能力 |
| 2026-08-02 | 数据与模型不进 Git | 大文件/二进制产物不适合版本控制;`.gitignore` 排除 |
| 2026-08-02 | CI 不跑全量训练,用 mock 小数据验证管道 | CI runner 资源有限,全量数据训练在本地/服务器执行 |

---

## 已知坑 (GOTCHAS)

- _暂无(项目刚初始化,尚未开始编码)_

---

## 里程碑 (DONE)

- [ ] _暂无_
