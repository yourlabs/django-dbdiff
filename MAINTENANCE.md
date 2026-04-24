# Maintenance Plan — django-dbdiff

> Generated on 2026-04-23 from the actual state of the repository.
> Repo: https://github.com/yourlabs/django-dbdiff

---

## Current State

| Item | Value |
|---|---|
| Latest published version | 0.9.6 |
| Latest commit | "Add ignore_pk option to Fixture and diff functions" |
| License | MIT |
| Python support (declared) | 3.8 to 3.12 |
| Python support (target) | 3.10, 3.11, 3.13, 3.14 |
| Django support (declared) | 3.2, 4.0, 4.1, 4.2, 5.0 |
| Django support (target) | 4.2, 5.2 LTS, 6.0 |
| Tested databases | SQLite, MySQL, PostgreSQL |
| CI | GitHub Actions (`django.yml`) — active |
| CHANGELOG | "Unreleased Refresh supported dependencies and support" at the top — unpublished work in progress |
| Dependencies | `ijson`, `json_delta` |
| Stars | ~30 |

**Strengths:**
- GitHub Actions CI with multi-DB matrix
- Good baseline coverage (pytest + pytest-cov)
- `ignore_pk` feature recently added

**Concerns:**
- Python 3.8 (EOL Oct 2024) and 3.9 (EOL Oct 2025) still in the matrix
- Django 4.0 and 4.1 EOL still listed as supported
- Python 3.13 and 3.14 missing
- Django 5.2 LTS and 6.0 missing
- GitHub Actions using outdated versions (`checkout@v1`, `setup-python@v4`)
- `setup.py` still used (no `pyproject.toml`)
- `codecov` CLI used in CI (deprecated, replaced by the official Action)
- README badges point to Travis CI (dead)

---

## Phase 1 — Critical Bug to Fix Immediately

### Silent bug in `fixture.py` — always-False condition

**File:** `dbdiff/fixture.py`, line 129
**Priority: HIGH — possible false negative in `diff()`**

```python
# Current (incorrect):
if not unexpected and not missing and not diff:

# Correct:
if not unexpected and not missing and not different:
```

`diff` here is the **imported function** from `utils`, never `None`, and therefore always truthy. The `os.unlink(dump_path)` + `return None` branch is **never reached**. As a result, the temporary file is never deleted on this path. Additionally, `assertNoDiff()` receives a `None` return value (line 165: `unexpected, missing, different = self.diff(...)`) when the database exactly matches the fixture, causing a `TypeError` at runtime.

**Actions:**
- [x] Fix `fixture.py` line 129: replace `not diff` with `not different`
- [x] Add a regression test: the case where the database matches the fixture exactly should pass without error
- [ ] Publish `v0.9.7` after the fix

---

## Phase 2 — CI Modernization

### GitHub Actions: outdated action versions

The `.github/workflows/django.yml` workflow uses very old actions:

| Current action | Recommended version |
|---|---|
| `actions/checkout@v1` | `actions/checkout@v4` |
| `actions/setup-python@v4` | `actions/setup-python@v5` |

`checkout@v1` dates from 2019 and does not correctly support modern runners (particularly `GITHUB_TOKEN` permissions).

**Actions:**
- [x] Update `actions/checkout@v1` → `v4`
- [x] Update `actions/setup-python@v4` → `v5`
- [x] Replace the `codecov` CLI step with `codecov/codecov-action@v4`

### README badges pointing to Travis CI

`README.rst` contains Travis CI badges (`travis-ci.org`) pointing to a dead service.

**Actions:**
- [x] Replace the Travis CI badge with a GitHub Actions badge
- [x] Update the Codecov badge with the current URL (`app.codecov.io`)

---

## Phase 3 — Python and Django Compatibility

### Add Python 3.10, 3.11, 3.13, 3.14 and Django 4.2, 5.2, 6.0

Python 3.13 released October 2024; Python 3.14 in beta (stable expected October 2026). Django 5.2 LTS released April 2025; Django 6.0 is the next major release.

**Actions:**
- [x] Add `py310`, `py311`, `py313`, `py314` to `tox.ini` (envlist) and `django.yml` (matrix)
- [x] Add `django42`, `django52`, `django60` to `tox.ini`
- [ ] Verify that `ijson` and `json_delta` are compatible with Python 3.13 and 3.14
- [ ] Verify Django 6.0 compatibility (check for deprecated APIs removed in 6.0)
- [x] Update classifiers in `pyproject.toml`

### Drop EOL versions

- Python 3.8: EOL October 2024
- Python 3.9: EOL October 2025
- Django 4.0 and 4.1: EOL

**Actions:**
- [x] Remove `py38`, `py39` from `tox.ini` and CI
- [x] Remove `django40`, `django41` from `tox.ini`
- [x] Remove corresponding classifiers from `pyproject.toml`
- [x] Update README: "Python 3.10 to 3.14 / Django 4.2, 5.2, 6.0"

---

## Phase 4 — Packaging Modernization

### Migrate to `pyproject.toml`

The project still uses `setup.py`. PEP 517/518 has been the standard for several years.

**Actions:**
- [x] Migrate to `pyproject.toml` (build-backend `setuptools>=61`)
- [x] Move classifiers, dependencies, and metadata into `pyproject.toml`
- [x] Remove `setup.py` and `MANIFEST.in` if applicable
- [ ] Verify PyPI publishing with the new format

### Release management

- [ ] Publish the CHANGELOG entry as `v0.9.7` after the fixes
- [x] Add a GitHub Action for automatic PyPI publishing on tag push (`pypa/gh-action-pypi-publish`)

---

## Phase 5 — Code Quality

### Modernize `tox.ini` — `qa` env

The `qa` env is based on `python3.8` (EOL) and uses `flake8`. Consider migrating to `ruff`, which is faster and actively maintained.

**Actions:**
- [x] Change `basepython = python3.8` → `python3.12` in `[testenv:qa]`
- [ ] Evaluate migrating from `flake8` to `ruff` (covers flake8 + isort + pyupgrade)
- [ ] Verify that `--max-complexity=7` rules are still relevant

---

## Summary by Priority

### Critical (bug)
- [x] **[BUG]** `fixture.py:129` — fix `not diff` → `not different` (false negative + temp file leak)
- [x] **[BUG]** Add regression test: empty diff must pass without error
- [ ] **[REL]** Publish `v0.9.7`

### High priority (CI)
- [x] **[CI]** Update `actions/checkout@v1` → `v4` and `setup-python@v4` → `v5`
- [x] **[CI]** Replace `codecov` CLI with `codecov/codecov-action@v4`
- [x] **[DOC]** Replace Travis CI badges with GitHub Actions badges in README

### Normal priority (compatibility)
- [x] **[COMPAT]** Add Python 3.10, 3.11, 3.13, 3.14 to tox.ini and CI
- [x] **[COMPAT]** Add Django 4.2, 5.2 LTS, and 6.0
- [x] **[COMPAT]** Drop Python 3.8, 3.9, Django 4.0, 4.1 (all EOL)
- [x] **[DOC]** Update README with current supported versions

### Normal priority (modernization)
- [x] **[MOD]** Migrate from `setup.py` to `pyproject.toml`
- [x] **[MOD]** GitHub Action for automatic PyPI release on tag push

### Low priority
- [ ] **[QA]** Migrate `flake8` → `ruff` in the `qa` env
- [x] **[QA]** Update `basepython` in `[testenv:qa]` to Python 3.12+

### Remaining (manual verification needed)
- [ ] Verify `ijson` and `json_delta` compatibility with Python 3.13 and 3.14
- [ ] Verify Django 6.0 API compatibility (check for removed deprecated APIs)
- [ ] Configure PyPI Trusted Publishing (OIDC) for the repo on pypi.org
- [ ] Publish `v0.9.7` tag to trigger the new release workflow
