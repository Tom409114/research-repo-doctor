# Research Repo Doctor - Codex for OSS Application Readiness

## 1. Repository URL

Public URL: https://github.com/Tom409114/research-repo-doctor

Status: public GitHub repository created under `Tom409114`.

## 2. Release URL

Release URL: https://github.com/Tom409114/research-repo-doctor/releases/tag/v0.1.0

Status: GitHub Release created and published.

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

The public release state is complete:

- Python package and CLI.
- GitHub Action metadata.
- CI and release workflow definitions.
- Documentation, examples, fixtures, and reports.
- Issue templates and initial roadmap issue drafts.
- v0.1.0 GitHub release with wheel and source distribution assets.

GitHub repository publication is complete. CI and Action smoke tests were verified with GitHub CLI on 2026-06-03.

## 6. What is intentionally not yet claimed

- No fabricated stars, forks, downloads, users, or adoption.
- No claim that PyPI is published unless it is actually published.
- No claim of community adoption or community PR activity yet.
- No claim that release asset downloads imply usage.

## 7. Metrics to fill in the form

- Stars: 1
- Forks: 0
- Issues: 12 roadmap issues created
- PRs: 0
- Downloads: 0 GitHub release asset downloads; PyPI publication deferred
- Release URL: https://github.com/Tom409114/research-repo-doctor/releases/tag/v0.1.0

## 8. Copy-ready answer: why this repository qualifies

Research Repo Doctor 面向科研开源生态中的基础痛点：许多论文代码仓库难以复现、审查、引用和二次维护。项目提供确定性 CLI 与 GitHub Action，可在 PR 和发布前自动检查环境、数据、实验入口、Notebook、引用、许可、CI、安全与发布准备。它虽处早期，不声称已有采用量，但定位清晰、规则可测试、文档和维护流程完整，适合作为可长期维护的开源基础设施。

## 9. Copy-ready answer: how API credits will be used

API 额度只用于维护者工作流，不会让终端用户调用 API。计划用途包括：分析误报/漏报 issue，生成最小复现夹具；辅助审查规则 PR 的说明、测试覆盖、安全证据和潜在误报；汇总 issue 与合并记录，起草 release notes、迁移说明和文档更新。核心 CLI 始终本地优先、确定性运行，不依赖 OpenAI API 或网络服务。

## 10. Copy-ready answer: additional notes

项目将持续公开维护路线图、贡献指南、规则作者规范、issue 模板、PR 模板、CI、发布流程和安全政策。我会按误报、漏报、新规则、扫描案例和 bug 分类 triage，要求规则变更配套 fixture 与测试。当前 v0.1.0 已公开发布，CI 通过，self-scan 为 100/100；指标只填写真实数据，不伪造 stars、下载量或用户采用。

## 11. Evidence checklist

- Public repo: complete
- CI passing: complete
- Release created: complete
- GitHub Action metadata: complete in `action.yml`
- README: complete
- Docs: complete
- Roadmap issues: 12 created
- Contribution guide: complete
- Security policy: complete
- Changelog: complete
- Citation file: complete

## 12. Remaining optional improvements

- PyPI publish after Trusted Publishing is configured.
- Docs website deployment.
- More example scans from public or sanitized research repositories.
- Early feedback from researchers and lab maintainers.
