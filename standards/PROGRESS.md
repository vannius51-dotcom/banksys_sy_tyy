# PROGRESS · banksys_sy_tyy 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-08-02 · by Claude)

- **阶段**:`六步流程第 ⑥ 步 — PR 已合并,CD SSH 认证待修复`
- **上一步完成**:`PR #1 合并 main,CI 全绿(format+lint+test 88%+docker),CD 因 SSH 密钥不匹配失败`
- **下一步 (TODO 第一条)**:`修复 SSH_PRIVATE_KEY → 服务器 authorized_keys 配对;然后 rerun CD 或空提交触发重新部署`
- **阻塞项**:`SSH 公钥未安装到服务器 ~/.ssh/authorized_keys;私钥需从本地 cat ~/.ssh/id_ed25519 更新到 GitHub Secrets`

---

## 待办清单 (TODO,按优先级)

- [x] **人工确认**:阅读并确认 `standards/00-project-context.md` 与 `standards/01-requirements.md`
- [x] **① 建仓 + 配 Secrets**:用 `gh` 创建 GitHub 仓库 `banksys_sy_tyy`(开源);提示人类配置 `SSH_PRIVATE_KEY` / `SSH_HOST` / `SSH_USER` 三个 Secrets
- [x] **② 开 feature 分支**:从 `main` 切 `feature/1-project-init`,完成工程化骨架
- [x] **③ 模块 1 — 项目骨架**:目录结构、requirements.txt、Dockerfile、CI/CD workflow、app/main.py 入口
- [x] **③ 模块 2 — US-2 数据分析页**:data_loader.py + analysis.py + Streamlit 页面 + 测试
- [x] **③ 模块 3 — US-3 模型训练**:model.py + 训练/评估逻辑 + 测试
- [x] **③ 模块 4 — US-4 在线预测**:predict.py + 表单页面 + 测试
- [x] **④ CI 自检**:ruff format ✅ + ruff lint ✅ + pytest 31 passed 88.21% ✅ + docker build ✅(GitHub Actions 执行)
- [x] **⑤ 触发 PR**:PR #1 已创建并 CI 全绿
- [x] **⑥ 人工审核 → 合并**:人工已 Merge PR #1
- [ ] **⑥ CD 自动部署**:SSH 认证失败 — **待用户修复密钥配对后 rerun CD workflow**
- [x] 会话结束前更新本文件

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

- **本地无 Python 3.11 环境**:Git Bash / PowerShell 均找不到 Python/conda/uv;解决:需手动安装 Python 3.11 或 conda 并创建虚拟环境;验证:安装后运行 `python --version` 确认版本为 3.11。
- **CD SSH 认证失败 `handshake failed`**:GitHub Actions runner 通过 `SSH_PRIVATE_KEY` 连接服务器(117.72.172.21)被拒,根因是 `~/.ssh/authorized_keys` 中缺少对应公钥;解决:将本地 `~/.ssh/id_ed25519.pub` 内容追加到服务器 `~/.ssh/authorized_keys`,再用 `cat ~/.ssh/id_ed25519` 内容更新 GitHub Secret `SSH_PRIVATE_KEY`,然后 rerun CD workflow;验证:`ssh root@117.72.172.21 "echo OK"` 返回 OK 即免密成功。

---

## 里程碑 (DONE)

- [ ] _暂无_
