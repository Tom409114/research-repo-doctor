# Research Reproducibility

Research repositories are often read by people who were not present when the experiments were run: reviewers, future lab members, replication teams, or downstream users. Small gaps compound quickly.

Common problems include:

- Missing runtime or dependency versions.
- Data availability instructions that live outside the repository.
- Experiment commands known only to one author.
- Notebooks with hidden state, large outputs, or local paths.
- Results directories without provenance.
- Missing citation or release metadata.

## Practical checklist

- Document setup and one minimal successful command.
- Record dependency and runtime versions.
- Explain data access, preprocessing, and licensing.
- Provide experiment entrypoints and configuration files.
- Set and document random seeds where they matter.
- Keep notebooks clean and executable top-to-bottom.
- Add smoke tests and CI.
- Include license, citation metadata, changelog, and release tags.

Research Repo Doctor cannot prove scientific correctness. It helps maintainers find reproducibility gaps before release.
