# Research Repo Doctor - Codex for OSS Application Readiness

## 1. Repository URL

Public URL: https://github.com/Tom409114/research-repo-doctor

Status: public GitHub repository created under `Tom409114`.

## 2. Release URL

Release URL: https://github.com/Tom409114/research-repo-doctor/releases/tag/v0.1.0

Status: verify with `gh release view v0.1.0`.

## 3. Current version

`0.1.0`

Verified in:

- `pyproject.toml`
- `src/rrdoctor/__init__.py`
- `CITATION.cff`
- `CHANGELOG.md`

## 4. Maintainer role

Primary maintainer for release engineering, deterministic rule design, issue triage, PR review, release workflow hygiene, documentation quality, and responsible Codex/API-assisted maintenance workflows.

## 5. What has been published

Local release state is prepared:

- Python package and CLI.
- GitHub Action metadata.
- CI and release workflow definitions.
- Documentation, examples, fixtures, and reports.
- Issue templates and initial roadmap issue drafts.
- Local v0.1.0 package artifacts can be built from source.

GitHub repository publication is complete. CI and release status should be verified with GitHub CLI before submission.

## 6. What is intentionally not yet claimed

- No fabricated stars, forks, downloads, users, or adoption.
- No claim that PyPI is published unless it is actually published.
- No claim that CI is passing on GitHub until the public workflow run is visible.
- No claim that the GitHub Release exists until `v0.1.0` is created on GitHub.

## 7. Metrics to fill in the form

- Stars: fill after launch
- Forks: fill after launch
- Issues: at least 1 roadmap issue created; update after creating the remaining roadmap issues
- PRs: fill after real PR activity exists
- Downloads: fill after PyPI release, if any
- Release URL: fill after GitHub release creation

## 8. Copy-ready answer: why this repository qualifies

Research Repo Doctor 面向科研开源生态中的基础痛点：许多论文代码仓库难以复现、审查、引用和二次维护。项目提供确定性 CLI 与 GitHub Action，可在 PR 和发布前自动检查环境、数据、实验入口、Notebook、引用、许可、CI、安全与发布准备。它虽处早期，不声称已有采用量，但定位清晰、规则可测试、文档和维护流程完整，适合作为可长期维护的开源基础设施。

## 9. Copy-ready answer: how API credits will be used

API 额度只用于维护者工作流，不会让终端用户调用 API。计划用途包括：分析误报/漏报 issue，生成最小复现夹具；辅助审查规则 PR 的说明、测试覆盖、安全证据和潜在误报；汇总 issue 与合并记录，起草 release notes、迁移说明和文档更新。核心 CLI 始终本地优先、确定性运行，不依赖 OpenAI API 或网络服务。

## 10. Copy-ready answer: additional notes

项目将公开维护路线图、贡献指南、规则作者规范、issue 模板、PR 模板、CI、发布流程和安全政策。我会按误报、漏报、新规则、扫描案例和 bug 分类 triage，要求规则变更配套 fixture 与测试。申请前会补充真实指标占位、v0.1.0 发布、self-scan 报告、示例扫描和可复核的 GitHub Action 运行记录，不伪造 stars、下载量或用户采用。

## 11. Evidence checklist

- Public repo: ready
- CI passing: verify with `gh run list --limit 5`
- Release created: verify with `gh release view v0.1.0`
- GitHub Action metadata: ready in `action.yml`
- README: ready
- Docs: ready
- Roadmap issues: 1 created; drafts for the remaining issues are ready in `docs/initial-issues.md`
- Contribution guide: ready
- Security policy: ready
- Changelog: ready
- Citation file: ready

## 12. Remaining optional improvements

- PyPI publish after Trusted Publishing is configured.
- Docs website deployment.
- More example scans from public or sanitized research repositories.
- Early feedback from researchers and lab maintainers.
