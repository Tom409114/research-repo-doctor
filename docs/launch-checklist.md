# Launch checklist — exact manual steps (Windows / PowerShell)

These are the steps only you can do, because they need your accounts and credentials.
The code, docs, and tests are already merged and green. Repo: `Tom409114/research-repo-doctor`,
version `0.3.0`. Run every command below from the project folder:

```powershell
cd "c:\Users\thuah\Documents\Codex\2026-06-03\files-mentioned-by-the-user-txt\research-repo-doctor"
```

---

## Step 0 — Commit the merge and push to GitHub

The consolidation is currently uncommitted (19 changed files on top of the v0.2.0 commit).

1. Set your git identity once (so the commit is attributed to you, not a bot):
   ```powershell
   git config user.name  "Tom409114"
   git config user.email "tom409114@gmail.com"
   ```
2. Review what changed (optional but recommended):
   ```powershell
   git status
   git diff --stat
   ```
3. Commit:
   ```powershell
   git add -A
   git commit -m "Merge AE layer into v0.2.0; bump to 0.3.0"
   ```
4. Push to your GitHub. If your credentials are saved this just works:
   ```powershell
   git push origin main
   ```
   - If it asks to log in, a browser window opens — sign in to GitHub and approve.
   - If it rejects with an auth error, create a Personal Access Token:
     GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) →
     Generate new token → scope `repo` → copy it, and use it as the password when prompted
     (username = `Tom409114`).

After this, https://github.com/Tom409114/research-repo-doctor shows v0.3.0.

---

## Step 1 — Publish to PyPI (do this first; it removes the install friction)

### 1a. One-time account setup
1. Create accounts: https://test.pypi.org/account/register/ and https://pypi.org/account/register/
2. Enable 2FA on both (required).
3. Create API tokens (you'll paste these when uploading):
   - TestPyPI: https://test.pypi.org/manage/account/token/ → "Add API token" → scope
     "Entire account" → **copy the whole token including the `pypi-` prefix**.
   - PyPI: https://pypi.org/manage/account/token/ → same.

### 1b. Build the package
```powershell
python -m pip install --upgrade build twine
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
python -m build
python -m twine check dist\*
```
You should see `PASSED` for both the `.whl` and the `.tar.gz`.

### 1c. Upload to TestPyPI and verify in a clean environment
```powershell
python -m twine upload --repository testpypi dist\*
```
- Username: `__token__`
- Password: paste your **TestPyPI** token (the `pypi-...` string).

Verify it actually installs and runs from a throwaway venv:
```powershell
python -m venv "$env:TEMP\rrdtest"
& "$env:TEMP\rrdtest\Scripts\pip.exe" install --index-url https://test.pypi.org/simple/ `
  --extra-index-url https://pypi.org/simple "rrdoctor==0.3.0"
& "$env:TEMP\rrdtest\Scripts\rrdoctor.exe" --help
```
If `--help` prints the command list, the package is good.

### 1d. Upload to the real PyPI
```powershell
python -m twine upload dist\*
```
- Username: `__token__`
- Password: paste your **PyPI** token.

### 1e. Confirm the one-line install works
```powershell
uvx rrdoctor scan .
```
Then add a PyPI version badge under the title in `README.md`:
```markdown
[![PyPI](https://img.shields.io/pypi/v/rrdoctor.svg)](https://pypi.org/project/rrdoctor/)
```
Commit and push that small change.

> Later, to never paste tokens again, set up PyPI **Trusted Publishing** (OIDC) so the
> `release.yml` workflow publishes automatically: https://docs.pypi.org/trusted-publishers/

---

## Step 2 — Tag the release on GitHub

```powershell
git tag -a v0.3.0 -m "v0.3.0: artifact-evaluation profiles, verify ladder, appendix, MCP"
git push origin v0.3.0
```
Then create the Release in the browser:
1. Go to https://github.com/Tom409114/research-repo-doctor/releases/new
2. "Choose a tag" → select `v0.3.0`.
3. Title: `v0.3.0`. Description: paste the `## Unreleased (0.3.0)` section from `CHANGELOG.md`.
4. Click **Publish release**.

---

## Step 3 — Publish the GitHub Action to the Marketplace

1. On the same Release page (or re-open the v0.3.0 release → Edit), check
   **"Publish this Action to the GitHub Marketplace"**.
2. Accept the agreement, choose a primary category (e.g. *Code quality*).
3. The page validates `action.yml` (already at the repo root) and publishes.
4. Move the floating major tag so users can pin `@v0`:
   ```powershell
   git tag -f v0
   git push -f origin v0
   ```

---

## Step 4 — Get a citable DOI (Zenodo)

1. Go to https://zenodo.org and "Log in" → with GitHub.
2. Open https://zenodo.org/account/settings/github/ and flip the switch **ON** for
   `Tom409114/research-repo-doctor`.
3. Make a new GitHub Release (or re-publish v0.3.0) — Zenodo mints a DOI automatically.
4. Copy the DOI badge from Zenodo into `README.md`, and update `CITATION.cff` with the DOI.
   Commit and push.

---

## Step 5 — Submit a JOSS paper (academic credibility flywheel)

1. The software must be archived (Step 4 done) and openly licensed (MIT — done).
2. Add `paper.md` + `paper.bib` to the repo following
   https://joss.readthedocs.io/en/latest/submitting.html
   (a Summary, a Statement of Need, ~250–1000 words; cite related tools).
3. Commit, push, then submit at https://joss.theoj.org/papers/new — the review is public on GitHub.

---

## Step 6 — Get listed in community indexes (each beats ten tweets)

Open a PR / submission to each:
- awesome-reproducible-research
- The Turing Way (tools chapter)
- pyOpenSci software submission (and rOpenSci if you deepen R support)
- everse.software RSQKit
- CodeRefinery tool lists

Frame rrdoctor as a **diagnostic self-check**, never a ranking/leaderboard — the research
software community reacts badly to "name and shame" scoring.

---

## Step 7 — Approach Artifact Evaluation chairs (highest-leverage outreach)

For conferences with near deadlines (NeurIPS, ICML, CCS, ASPLOS, SC, MICRO, MobiSys…):
- Email the AE/AEC chairs offering rrdoctor as a recommended **pre-submission self-check**.
- Point them at `rrdoctor appendix --profile acm` and the badge mapping — it reduces reviewer
  load, which chairs want.
- Offer a short "preparing your artifact" paragraph for their call for papers.

---

## Step 8 — Write the data-driven post (after some scan volume)

Aggregate **anonymously** ("I scanned 100 NeurIPS artifacts; reproduction breaks most on these
5 things"). Never name specific repos. Cross-post to the indexes from Step 6, not just HN.

---

## Quick order of operations
1. Commit + push the merge (Step 0).
2. `python -m build` → `twine upload` to PyPI (Step 1).
3. Tag `v0.3.0`, cut the GitHub Release, publish the Action to Marketplace (Steps 2–3).
4. Turn on Zenodo, make the release mint a DOI (Step 4).
5. JOSS, community lists, AEC outreach, content — outreach you drive (Steps 5–8).

> Cleanup: I preserved two stale v0.1.0 application drafts in
> `..\_rrd-0.1.0-archived-docs\`. They are not part of the repo; delete that folder if you
> don't want them.
