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
