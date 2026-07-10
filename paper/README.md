# JOSS Paper Draft

This directory contains living draft materials for a possible Journal of Open
Source Software submission:

- [paper.md](paper.md): JOSS-style Markdown manuscript.
- [paper.bib](paper.bib): bibliography used by the manuscript.

The draft is not a submitted manuscript. It uses project-level maintainer
attribution and avoids unverified adoption claims. Before any formal submission,
replace that metadata with the final author names, affiliations, and ORCID
identifiers, and update the impact statement only with external use,
integrations, publications, or corpus results that are true at submission time.

## Current eligibility status

As of 2026-07-10, this project is **not ready for JOSS submission**. The
[current JOSS screening criteria](https://joss.readthedocs.io/en/latest/submitting.html#pre-review-screening-criteria)
require more than six months of public history, with active and iterative
development across that period. This repository became public on 2026-06-03,
so its earliest calendar eligibility date is 2026-12-04, and reaching that date
alone will not satisfy the requirement.

Before submission, the project must also show concrete research use rather than
future intent, preserve meaningful open development over time, and replace the
draft metadata with real, consented authorship and conflict-of-interest details.
The [JOSS AI usage policy](https://joss.readthedocs.io/en/latest/policies.html#ai-usage-policy)
also requires a complete inventory of the tools/models used, the scope of their
assistance, and a truthful human-author review and validation attestation. The
current generic disclosure is a draft and must not be treated as that final
attestation.

The paper can be previewed with the Open Journals tooling. With Docker from the
repository root:

```bash
docker run --rm --volume "${PWD}/paper:/data" --env JOURNAL=joss openjournals/inara
```

Before submission, run the public readiness gate from the repository root and
preview the paper PDF:

```bash
python scripts/check.py
docker run --rm --volume "${PWD}/paper:/data" --env JOURNAL=joss openjournals/inara
```

Keep the manuscript claims aligned with current evidence: no adoption claims
without external use, no corpus counts without a fresh reviewed scan, and no
dynamic reproducibility claims unless `rrdoctor verify --run` was exercised on a
trusted target.
