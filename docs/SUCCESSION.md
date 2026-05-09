# Succession & Continuity Plan

> Living document. Last reviewed 2026-05-09.
>
> Read this if the original maintainer is no longer reachable, or before
> stepping away from the project for an extended period. The goal is that
> the Atlas can survive transition: stay reachable at its DOI, keep its
> tests passing, and accept patches.

---

## Why this document exists

Solo academic web tools have a known failure mode: the maintainer moves
on, hosting bills go unpaid, the URL 404s, and citations in published
papers rot. The DOI badge on Zenodo still resolves, but it points to
source code that no one can run because the deployment is gone.

This file documents the keys, knobs, and contacts needed to keep the
Aramaic Root Atlas alive without the original maintainer present.

---

## Inheritance — who has access

The original maintainer is **Jose Fresco Benaim** (`jossif@gmail.com`,
ORCID [0009-0000-2026-0836](https://orcid.org/0009-0000-2026-0836),
website [jossifresco.com](https://jossifresco.com)).

If the original maintainer is incapacitated, the following accounts
control the live deployment and citable artifacts:

### GitHub repository

- **URL:** https://github.com/Jossifresben/aramaic-root-atlas
- **License:** Apache-2.0 (code) + per-corpus licenses (data; see
  `LICENSE-DATA.md`)
- **Owner account:** `Jossifresben` (the maintainer's personal GitHub)
- **What to do on transition:**
  - Add a designated successor as a repository **Collaborator** with
    Admin rights
  - Or transfer ownership to an institutional org (preferred for
    long-term continuity — see "Institutional anchor" below)
  - The repository can be cloned and re-hosted by anyone (Apache-2.0);
    the data licenses still apply per-file

### Render hosting

- **Live URL:** https://aramaic-root-atlas.onrender.com
- **Tier:** Pro plan, always-on, no cold starts
- **Account:** the maintainer's Render account (linked to GitHub)
- **Auto-deploy:** every push to `main` triggers a redeploy
- **What to do on transition:**
  - Add a successor as a **team member** with Owner role on the Render
    workspace
  - Or migrate the deployment to another Render account / hosting
    provider; this repo's `render.yaml` makes the deployment
    reproducible
  - If hosting lapses, the static fallback (zip of last release) on
    Zenodo still preserves the source code, but the live tool goes
    dark

### Zenodo deposits

- **Concept DOI:** [10.5281/zenodo.19358625](https://doi.org/10.5281/zenodo.19358625)
  (always resolves to the latest version)
- **Per-version DOIs:** v3.0.2 → `10.5281/zenodo.20089274`,
  v3.0.1 → similar pattern, etc. (see Zenodo "Versions" sidebar)
- **Zenodo account:** linked to the maintainer's Zenodo profile via the
  GitHub integration
- **Auto-deposit trigger:** a new Zenodo record is minted whenever a
  GitHub Release is created (not just a tag push — the Release object
  fires the webhook)
- **What to do on transition:**
  - Zenodo deposits are immutable. They will continue to resolve at
    their DOIs regardless of GitHub ownership
  - To mint *new* versions after transition, the GitHub Release must
    be created by an account with Zenodo's GitHub integration enabled
  - The successor should connect their own Zenodo account to the
    transferred GitHub repo via Zenodo's GitHub Settings page

### Domain & DNS

- The Atlas does **not** use a custom domain — it lives at the
  Render-provided subdomain `aramaic-root-atlas.onrender.com`. No DNS
  records to maintain.
- If a custom domain is added later (e.g. `aramaic.atlas.org`),
  document the registrar and renewal date here.

### Google Analytics

- **Property ID:** `G-XWZC618EC4`
- **Account:** the maintainer's Google account
- **Status:** consent-gated (opt-in only); see `/privacy` page for the
  policy
- **What to do on transition:** either transfer the GA property to the
  successor's Google account, or remove the property reference from
  `templates/base.html` to disable analytics entirely. The site works
  fine without GA.

### Anthropic API (for cognate generation)

- The Atlas uses the Claude API for cognate generation (see
  `scripts/generate_new_cognates.py`). This is **not required for the
  live tool to run** — only for re-running the cognate-generation
  pipeline when adding new corpora.
- The maintainer's Anthropic API key is in their personal account.
  Successor can use any working Claude API key when they need to
  regenerate cognates.

---

## Recommended institutional anchor

The most durable transition is to a recognized academic institution
that publishes computational-Aramaic tools. Candidates, in approximate
order of fit:

1. **Eep Talstra Centre for Bible and Computer (ETCBC)**, Vrije
   Universiteit Amsterdam. Hosts the Peshitta OT data already used by
   the Atlas.
2. **Beth Mardutho Syriac Institute**. Hosts SEDRA (already used).
   Established Syriac digital humanities home.
3. **Hebrew Union College (CAL — Comprehensive Aramaic Lexicon)**.
   Most-cited Aramaic lexicon project.
4. **Leiden Peshitta Institute**. The Peshitta OT critical edition's
   editorial home.
5. **Notre Dame, Ancient Israel Studies / Tübingen, Semitistik**.
   General academic Semitic-studies homes.

Approach with: the v3.0+ release at the live URL, `docs/VALIDATION.md`
disclosing limitations, the test suite as evidence of engineering
seriousness, the planned cognate-audit work as offer.

---

## Minimum survival kit

If the maintainer is gone, the project survives if **any** of the
following is true:

1. A successor has Admin access to the GitHub repo (can accept PRs,
   create releases, transfer Zenodo integration).
2. The repo is forked by a competent maintainer (Apache-2.0 + per-file
   data licenses make this legally clear; see `LICENSE-DATA.md`).
3. An institutional partner adopts the project (preferred — see above).

**The data deposit on Zenodo is immutable**, so even in the worst case
("everything goes dark"), the citable record at
[10.5281/zenodo.19358625](https://doi.org/10.5281/zenodo.19358625)
preserves source code, the indexed corpus CSVs, and the documentation
exactly as released. Anyone can rebuild the live tool from that.

---

## How to keep the project healthy as a successor

```bash
# Clone, install, run
git clone https://github.com/Jossifresben/aramaic-root-atlas.git
cd aramaic-root-atlas
pip install -r requirements.txt
PORT=5002 python3 app.py     # local dev on http://localhost:5002

# Test before any commit / deploy
python3 -m pytest tests/     # 150 tests as of v3.0.2

# Deploy on push (Render auto-deploys main)
git push origin main

# Cut a new release (mint a new Zenodo DOI)
git tag -a v3.X -m "Release notes here"
git push origin v3.X
gh release create v3.X --title "..." --notes "..."   # required for Zenodo

# Update CITATION.cff version + date before tagging
```

Critical rule the original maintainer asked to be enforced:
**never `git push` without explicit user instruction.** Document any
in-flight work, then stop and ask.

---

## What's still pending (as of 2026-05-09)

The full plan lives in `docs/ROADMAP-v3.1.md`. Most-blocking items for
long-term credibility:

- **Phase 2.1**: gold-standard test set (300 hand-annotated verses,
  60 per corpus). Without this, no published precision/recall numbers
  exist.
- **Phase 2.4**: cognate audit against authoritative lexicons. ~1,584
  entries × 6 lexicons (HALOT, BDB, Sokoloff, Brockelmann, Lane,
  Wehr).
- **Phase 3.1**: institutional partner adoption (see above).

Both Phase 2 items require Aramaic-specialist work and won't happen
under solo maintenance. **Securing an institutional partner is the
single highest-leverage move for project longevity.**

---

## Reviewing this document

Re-read at least every 6 months, and immediately after any of:
- Hosting provider change
- Tag/release process change
- Successor identified or removed
- Institutional partner secured
- DOI scheme change at Zenodo

---

*If you are reading this as a successor: thank you for keeping it
alive. The project is small but useful, and a small amount of
maintenance preserves a citable academic resource.*
