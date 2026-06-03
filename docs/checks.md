# Checks

Rules are deterministic and local-first. Severity can be overridden in `.rrdoctor.yml`.

| ID | Name | Category | Severity | Profiles |
| --- | --- | --- | --- | --- |
| RRD001 | README missing | documentation | error | minimal, standard, strict, ml |
| RRD002 | README lacks installation/setup section | documentation | warning | minimal, standard, strict, ml |
| RRD003 | README lacks quickstart or usage section | documentation | warning | minimal, standard, strict, ml |
| RRD004 | README lacks reproducibility section | reproducibility | warning | minimal, standard, strict, ml |
| RRD010 | LICENSE missing | governance | error | minimal, standard, strict, ml |
| RRD011 | CONTRIBUTING guide missing | governance | warning | strict |
| RRD012 | SECURITY policy missing | governance | warning | strict |
| RRD013 | CODE_OF_CONDUCT missing | governance | info | strict |
| RRD020 | Citation instructions missing | citation | warning | standard, strict, ml |
| RRD021 | Paper metadata not documented | citation | warning | standard, strict, ml |
| RRD030 | No dependency manifest found | environment | error | minimal, standard, strict, ml |
| RRD031 | Dependency manifest lacks version hint | environment | warning | minimal, standard, strict, ml |
| RRD032 | Dockerfile or devcontainer missing | environment | info | strict |
| RRD040 | Data availability documentation missing | data | error | minimal, standard, strict, ml |
| RRD041 | data directory lacks README | data | warning | standard, strict, ml |
| RRD042 | Large data files detected | data | warning | standard, strict, ml |
| RRD043 | Potential local absolute data path detected | data | warning | standard, strict, ml |
| RRD050 | No experiment entrypoint found | experiments | error | minimal, standard, strict, ml |
| RRD051 | No configuration files found | experiments | warning | ml |
| RRD052 | Randomness used without obvious seed setting | reproducibility | warning | standard, strict, ml |
| RRD053 | Results provenance documentation missing | experiments | warning | standard, strict, ml |
| RRD060 | Notebook files detected with large outputs | notebooks | warning | standard, strict, ml |
| RRD061 | Notebook execution counts appear out of order | notebooks | warning | standard, strict, ml |
| RRD062 | Notebook contains absolute local paths | notebooks | warning | standard, strict, ml |
| RRD063 | Notebook contains possible secret-like output | security | error | standard, strict, ml |
| RRD064 | Notebook has no paired script or execution instructions | notebooks | info | strict |
| RRD070 | No tests directory or test files found | testing | warning | standard, strict, ml |
| RRD071 | No test runner/configuration detected | testing | warning | standard, strict, ml |
| RRD080 | No CI workflow detected | ci | warning | standard, strict, ml |
| RRD081 | CI lacks obvious test or lint step | ci | warning | standard, strict, ml |
| RRD090 | Potential committed secret detected | security | error | standard, strict, ml |
| RRD091 | .gitignore missing common research artifacts | security | warning | standard, strict, ml |
| RRD100 | CHANGELOG missing | release | warning | standard, strict, ml |
| RRD101 | No version metadata found | release | warning | standard, strict, ml |
| RRD102 | No release or packaging workflow found | release | info | strict |
| RRD110 | Python project metadata incomplete | metadata | warning | standard, strict, ml |
| RRD111 | Repository lacks topic/keyword guidance in README | metadata | info | standard, strict, ml |
