# JOSS Paper Draft

This directory contains draft materials for a possible Journal of Open Source
Software submission:

- [paper.md](paper.md): JOSS-style Markdown manuscript.
- [paper.bib](paper.bib): bibliography used by the manuscript.

Before a formal submission, replace the maintainer placeholder in `paper.md`
with the real author names, affiliations, and ORCID identifiers. Also update the
research impact statement with any external use, integrations, publications, or
corpus results that are true at submission time.

The paper can be previewed with the Open Journals tooling. With Docker:

```bash
docker run --rm ^
  --volume %cd%/paper:/data ^
  --env JOURNAL=joss ^
  openjournals/inara
```

On Linux or macOS, replace `%cd%` with `$(pwd)`.
