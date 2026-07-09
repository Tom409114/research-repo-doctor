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

The paper can be previewed with the Open Journals tooling. With Docker:

```bash
docker run --rm ^
  --volume %cd%/paper:/data ^
  --env JOURNAL=joss ^
  openjournals/inara
```

On Linux or macOS, replace `%cd%` with `$(pwd)`.

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
