# Codex for Open Source Application Draft

## Project summary

中文：Research Repo Doctor 是面向科研代码仓库的开源 CLI 与 GitHub Action，帮助研究者和实验室团队在发布前检查可复现性、数据说明、环境依赖、实验入口、Notebook 卫生、引用信息、许可、CI、测试和发布准备。核心扫描器确定性、本地优先，不需要 OpenAI API key。

English: Research Repo Doctor is an open-source CLI and GitHub Action for auditing research repositories before public release. It checks reproducibility, data documentation, environments, experiment entrypoints, notebooks, citation metadata, licensing, CI, tests, and release readiness. The core scanner is deterministic and local-first.

Planned repository URL: https://github.com/Tom409114/research-repo-doctor

## Why this repository qualifies?

Research Repo Doctor 面向科研开源生态中的基础痛点：许多论文代码仓库难以复现、审查、引用和二次维护。项目提供确定性 CLI 与 GitHub Action，可在 PR 和发布前自动检查环境、数据、实验入口、Notebook、引用、许可、CI、安全与发布准备。它虽处早期，不声称已有采用量，但定位清晰、规则可测试、文档和维护流程完整，适合作为可长期维护的开源基础设施。

## How will API credits be used for this project?

API 额度只用于维护者工作流，不会让终端用户调用 API。计划用途包括：分析误报/漏报 issue，生成最小复现夹具；辅助审查规则 PR 的说明、测试覆盖、安全证据和潜在误报；汇总 issue 与合并记录，起草 release notes、迁移说明和文档更新。核心 CLI 始终本地优先、确定性运行，不依赖 OpenAI API 或网络服务。

## Additional notes

项目将公开维护路线图、贡献指南、规则作者规范、issue 模板、PR 模板、CI、发布流程和安全政策。我会按误报、漏报、新规则、扫描案例和 bug 分类 triage，要求规则变更配套 fixture 与测试。申请前会补充真实指标占位、v0.1.0 发布、self-scan 报告、示例扫描和可复核的 GitHub Action 运行记录，不伪造 stars、下载量或用户采用。

## Metrics checklist

- GitHub stars: fill after launch
- forks: fill after launch
- monthly downloads: fill after PyPI release
- issues/PRs: 12 maintainer roadmap issues created; PRs 0 until community or maintainer PR activity begins
- early user feedback links: fill after outreach
- CI status link: https://github.com/Tom409114/research-repo-doctor/actions
- v0.1.0 release link: https://github.com/Tom409114/research-repo-doctor/releases/tag/v0.1.0

## Honest early-stage wording

This is an early-stage OSS project prepared for public launch. It does not yet claim adoption, stars, downloads, or production users. Its ecosystem value comes from addressing a common, recurring maintenance problem in research software with a reusable local CLI and GitHub Action.

## Suggested launch checklist before application

- Public GitHub repo
- README complete
- v0.1.0 release
- At least 5 issues created from real test repos
- At least 3 example scans
- Self-scan report committed under `examples/reports/`
- GitHub Action working
- CI green
- One changelog entry
- Project board or milestone
- Pinned issue for rule requests
- Discussion/feedback channel if enabled
