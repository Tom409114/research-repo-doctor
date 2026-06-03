# Research Repo Doctor - Codex for OSS Application Packet

This document is the single application packet for Research Repo Doctor. It is written to be copied into the Codex for OSS application form and to give reviewers fast evidence that the project is real, public, maintained, deterministic, and useful to the open-source research software ecosystem.

Last updated: 2026-06-03

## 1. Project Identity

| Field | Value |
| --- | --- |
| Project name | Research Repo Doctor |
| Package / CLI name | `rrdoctor` |
| Repository | https://github.com/Tom409114/research-repo-doctor |
| Release | https://github.com/Tom409114/research-repo-doctor/releases/tag/v0.1.0 |
| Current version | `0.1.0` |
| License | MIT |
| Default branch | `main` |
| Primary adoption path | GitHub Action: `Tom409114/research-repo-doctor@v0.1.0` |
| Core design | Deterministic, local-first, no OpenAI API key required |
| PyPI status | Deferred; installable from GitHub/source and release artifacts |

## 2. One-Sentence Summary

Research Repo Doctor is a deterministic CLI and GitHub Action that helps research software maintainers audit whether code repositories are reproducible, reviewable, citable, secure enough to publish, and ready for public release.

## 3. Copy-Ready Project Summary

### Chinese

Research Repo Doctor 是面向科研代码仓库的开源 CLI 与 GitHub Action，帮助研究者、学生和实验室团队在发布前检查可复现性、数据说明、环境依赖、实验入口、Notebook 卫生、引用信息、许可、CI、测试、安全和发布准备。核心扫描器确定性、本地优先，不需要 OpenAI API key；GitHub Action 是主要采用路径。

Character count: 183.

### English

Research Repo Doctor is an open-source CLI and GitHub Action for auditing research repositories before public release. It checks reproducibility, data documentation, environments, experiment entrypoints, notebooks, citation metadata, licensing, CI, tests, security hygiene, and release readiness. The core scanner is deterministic, local-first, and does not require an OpenAI API key.

## 4. Copy-Ready Answer: Why This Repository Qualifies

Research Repo Doctor 面向科研开源生态中的基础痛点：许多论文代码仓库难以复现、审查、引用和二次维护。项目提供确定性 CLI 与 GitHub Action，可在 PR 和发布前自动检查环境、数据、实验入口、Notebook、引用、许可、CI、安全与发布准备。它虽处早期，不声称已有采用量，但定位清晰、规则可测试、文档完整，且已有公开 release、绿色 CI 和 12 个维护路线图 issue。

Character count: 209.

## 5. Copy-Ready Answer: How API Credits Will Be Used

API 额度只用于维护者工作流，不会让终端用户调用 API。计划用途包括：分析误报/漏报 issue，生成最小复现夹具；辅助审查规则 PR 的说明、测试覆盖、安全证据和潜在误报；汇总 issue 与合并记录，起草 release notes、迁移说明和文档更新。核心 CLI 始终本地优先、确定性运行，不依赖 OpenAI API 或网络服务。

Character count: 172.

## 6. Copy-Ready Answer: Additional Notes

项目将持续公开维护路线图、贡献指南、规则作者规范、issue 模板、PR 模板、CI、发布流程和安全政策。我会按误报、漏报、新规则、扫描案例和 bug 分类 triage，要求规则变更配套 fixture 与测试。当前 v0.1.0 已公开发布，CI 通过，self-scan 为 100/100；指标只填写真实数据，不伪造 stars、下载量或用户采用。

Character count: 178.

## 7. Ecosystem Importance Argument

Research reproducibility depends on more than code being public. Reviewers, students, and future maintainers often need environment versions, dependency manifests, data availability notes, experiment entrypoints, notebook hygiene, citation metadata, CI, tests, and release records before they can even attempt to reproduce results.

Research Repo Doctor turns those recurring gaps into deterministic checks and actionable remediation. It is useful for:

- Researchers preparing code for a paper release.
- PhD students and research assistants maintaining experiment repositories.
- Labs standardizing reproducibility practices across many repositories.
- Reviewers who need a quick repository health report.
- Open-source research projects that want a GitHub Action quality gate.

The project is intentionally not a closed AI product. It is local-first open-source infrastructure whose main adoption path is a reusable GitHub Action.

## 8. Current Real Metrics

Checked with GitHub CLI on 2026-06-03.

| Metric | Current value | Notes |
| --- | ---: | --- |
| Stars | 1 | Real GitHub value at time of check |
| Forks | 0 | Real GitHub value at time of check |
| Open roadmap issues | 12 | Maintainer-created public roadmap issues |
| Pull requests | 0 | No PR activity yet; do not imply community PRs |
| GitHub Release | 1 | `v0.1.0` |
| Release assets | 2 | sdist and wheel |
| PyPI downloads | N/A | PyPI publication intentionally deferred |
| Release asset downloads | 0 | Initial release; do not claim downloads |

Recommended form wording for metrics:

- Stars: `1`
- Forks: `0`
- Issues: `12 open maintainer roadmap issues`
- PRs: `0 so far`
- Downloads: `PyPI not published yet; release assets available on GitHub`
- Early user feedback: `not collected yet; planned after initial outreach`

## 9. Published Evidence

| Evidence | Link |
| --- | --- |
| Public repository | https://github.com/Tom409114/research-repo-doctor |
| v0.1.0 release | https://github.com/Tom409114/research-repo-doctor/releases/tag/v0.1.0 |
| CI workflow status | https://github.com/Tom409114/research-repo-doctor/actions/workflows/ci.yml |
| Action smoke test workflow status | https://github.com/Tom409114/research-repo-doctor/actions/workflows/action-smoke-test.yml |
| Release workflow | https://github.com/Tom409114/research-repo-doctor/actions/workflows/release.yml |
| README | https://github.com/Tom409114/research-repo-doctor/blob/main/README.md |
| Contribution guide | https://github.com/Tom409114/research-repo-doctor/blob/main/CONTRIBUTING.md |
| Security policy | https://github.com/Tom409114/research-repo-doctor/blob/main/SECURITY.md |
| Changelog | https://github.com/Tom409114/research-repo-doctor/blob/main/CHANGELOG.md |
| Citation metadata | https://github.com/Tom409114/research-repo-doctor/blob/main/CITATION.cff |
| Roadmap | https://github.com/Tom409114/research-repo-doctor/blob/main/ROADMAP.md |
| Initial issue drafts | https://github.com/Tom409114/research-repo-doctor/blob/main/docs/initial-issues.md |
| Self-scan report | https://github.com/Tom409114/research-repo-doctor/blob/main/examples/reports/self-scan-report.md |

## 10. Roadmap Issues

The repository has 12 public maintainer roadmap issues:

1. Add R project environment detection: https://github.com/Tom409114/research-repo-doctor/issues/1
2. Add Julia project environment detection: https://github.com/Tom409114/research-repo-doctor/issues/2
3. Add Snakemake and Nextflow workflow detection: https://github.com/Tom409114/research-repo-doctor/issues/3
4. Improve CITATION.cff validation: https://github.com/Tom409114/research-repo-doctor/issues/4
5. Add Zenodo DOI and archive metadata checks: https://github.com/Tom409114/research-repo-doctor/issues/5
6. Add support for repo-level reproducibility badges: https://github.com/Tom409114/research-repo-doctor/issues/6
7. Add false-positive regression fixture format: https://github.com/Tom409114/research-repo-doctor/issues/7
8. Add Markdown table report for category scores: https://github.com/Tom409114/research-repo-doctor/issues/8
9. Add pre-commit hook example: https://github.com/Tom409114/research-repo-doctor/issues/9
10. Add docs website deployment workflow: https://github.com/Tom409114/research-repo-doctor/issues/10
11. Add machine learning checkpoint hygiene checks: https://github.com/Tom409114/research-repo-doctor/issues/11
12. Add anonymized scan corpus for rule evaluation: https://github.com/Tom409114/research-repo-doctor/issues/12

These are maintainer roadmap issues, not fabricated community activity.

## 11. Maintainer Plan

### Issue Triage

Issues are separated into bug reports, false positives, false negatives, rule requests, scan cases, and feature requests. Rule-related issues should include repository shape, expected behavior, deterministic evidence, and likely false positives.

### PR Review

Rule PRs will be reviewed for:

- Deterministic behavior.
- Evidence quality.
- Secret masking.
- Profile and severity fit.
- Fixture coverage.
- Documentation updates.
- No network dependency in the core scanner.

### Release Workflow

Each release should include:

- `pytest`
- `ruff check .`
- `ruff format --check .`
- `rrdoctor scan . --profile standard --fail-on none`
- GitHub Action smoke test.
- Changelog update.
- Release notes.
- Release assets generated by GitHub workflow or local build.

### Security Hygiene

The scanner avoids network calls during normal scans, masks secret-like evidence, and includes a security policy. Maintainers should not paste private repositories, real secrets, or private datasets into AI-assisted workflows.

## 12. Responsible API Credit Use

API credits should support maintainer productivity, not become a user-facing dependency.

Allowed maintainer uses:

- Summarize and classify false-positive or false-negative reports.
- Draft minimal synthetic fixtures from user descriptions.
- Review rule PRs for test coverage and likely false positives.
- Draft release notes and migration notes from changelog entries.
- Generate documentation improvements after human review.
- Analyze failing CI logs and propose deterministic tests.

Not allowed:

- Requiring end users to have an OpenAI API key.
- Adding network calls to the core scanner.
- Uploading real secrets, private data, or confidential repository content.
- Claiming AI-verified reproducibility.
- Fabricating adoption metrics or community activity.

## 13. What Is Intentionally Not Yet Claimed

- No claim of broad adoption.
- No claim of real user testimonials yet.
- No claim of PyPI downloads.
- No claim that the tool proves scientific correctness.
- No claim that SARIF support is complete.
- No claim that external DOI or archive URLs are verified online.

## 14. Reviewer Quick Path

A reviewer can verify the project quickly:

```bash
git clone https://github.com/Tom409114/research-repo-doctor.git
cd research-repo-doctor
python -m pip install -e ".[dev]"
pytest
rrdoctor scan . --profile standard --fail-on none
rrdoctor list-rules
rrdoctor explain RRD001
```

Expected result:

- Tests pass.
- Self-scan score is 100/100.
- Rules are listed.
- Rule explanations are human-readable.
- No API key is required.

## 15. Form Field Mapping

If the application form asks for a short project description:

```text
Research Repo Doctor is an open-source CLI and GitHub Action that audits research code repositories for reproducibility, reviewability, citation readiness, security hygiene, and public release readiness. It is deterministic, local-first, and useful without any AI API key.
```

If the form asks why the project matters:

```text
Research code often becomes public before it is reproducible by others. Research Repo Doctor helps maintainers catch missing environment metadata, data documentation, experiment entrypoints, notebook hygiene issues, citation gaps, CI/test gaps, and release-readiness problems before publication.
```

If the form asks how Codex/API credits will help:

```text
Credits will support maintainer workflows: issue triage, false-positive analysis, fixture drafting, PR review, release-note drafting, docs improvements, and CI failure analysis. The core CLI will remain deterministic and will not require users to call an API.
```

## 16. Submission Checklist

- [x] Public GitHub repo exists.
- [x] v0.1.0 release exists.
- [x] CI passing.
- [x] GitHub Action smoke test passing.
- [x] 12 roadmap issues created.
- [x] README complete.
- [x] Contribution guide complete.
- [x] Security policy complete.
- [x] Changelog complete.
- [x] Citation metadata complete.
- [x] Codex/API use described responsibly.
- [x] No fabricated adoption metrics.
- [x] PyPI status described honestly as deferred.

## 17. Final Recommended Application Notes

Use the real metrics as they are today. If stars/forks change before submission, update them from GitHub rather than guessing.

Best emphasis for the application:

- This is open-source infrastructure for research reproducibility.
- The GitHub Action makes it easy for labs to adopt across repositories.
- The scanner is deterministic and local-first, so credits are not needed by end users.
- API credits will improve maintainer throughput and quality, not power a closed product.
- The project already has public release evidence, CI, docs, issues, and a maintainable rule system.

## 18. Remaining Optional Improvements After Submission

- Configure PyPI Trusted Publishing and publish `rrdoctor`.
- Deploy documentation with MkDocs or GitHub Pages.
- Add more public or anonymized example scan cases.
- Collect early feedback from researchers and lab maintainers.
- Add R, Julia, Snakemake, Nextflow, Zenodo, and ML checkpoint rule improvements from the public roadmap.
