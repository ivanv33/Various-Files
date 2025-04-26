# Python Packaging & Env Cheat‑Sheet

> A quick refresher on everything we discussed while bootstrapping **Game‑AI**. Keep it open when you forget a flag or wonder which file does what.

---

## 1 · Virtual Environments

| Tool | Command | What it does |
|------|---------|--------------|
| **venv** (built‑in) | `python3.13 -m venv .venv` | Creates an isolated Python *folder* called `.venv/` with its own interpreter + `site‑packages`.
| **Activate** | `source .venv/bin/activate` (macOS/Linux)<br>` .\.venv\Scripts\activate` (Windows) | Prepends the venv to `$PATH`; prompt shows `(.venv)`.
| **Deactivate** | `deactivate` | Restores the global interpreter.

Why keep using a venv?
* Keeps project deps from polluting system Python.
* Easy to nuke: `rm -rf .venv`.

---

## 2 · `pyproject.toml` vs `requirements.txt`

| Aspect | `pyproject.toml` | `requirements.txt` |
|--------|------------------|--------------------|
| Purpose | Declare **package metadata + deps** (PEP 621) and **build backend** (PEP 518). | Snapshot of *exact* wheels to install (deployment / CI freeze).
| Editable install? | Yes → `pip install -e .` | N/A (no build step).
| Extras support | First‑class (`.[dev]`) | Clunky markers.
| Recommended use | Packaging, libraries, dev work. | Locked environments (`pip-compile`, Docker images).

---

## 3 · Editable Install & Extras

* `-e` → builds a **PEP 660 editable wheel** that points to your source tree; changes are live.
* `'[dev]'` → installs optional *extras* listed under `[project.optional-dependencies]`.
* **zsh gotcha**: quote or escape brackets → `pip install -e '.[dev]'`.

Common combos
```bash
pip install -e .            # runtime deps only
pip install -e '.[dev]'     # runtime + dev (pytest, click…)
pip install .               # frozen wheel (prod images)
```

---

## 4 · Setuptools & Wheel (how pip builds/installs)

```
source tree  ─[setuptools]─►  my_pkg‑0.1‑py3‑none‑any.whl  ─[pip]─►  venv/site‑packages
```

* **setuptools** – build backend (PEP 517). Reads *pyproject.toml*, compiles C/Cython, bundles files.
* **wheel** – artefact format (PEP 427). A zip with built code + metadata, tagged by Python/OS/ABI.
* Pip always tries to install a wheel; if none exists it asks the backend to build one.

---

## 5 · Typical Game‑AI Workflow

```bash
# 1 · create venv (once per clone)
python3.13 -m venv .venv && source .venv/bin/activate

# 2 · install project in dev mode
python -m pip install -U pip
python -m pip install -e '.[dev]'

# 3 · hack away; code changes are live
pytest -q             # run tests
game-ai hello         # CLI smoke‑test

# 4 · freeze environment (optional)
pip freeze > requirements.txt
```

---

## 6 · Cheat‑Sheet Commands

| Task | Command |
|------|---------|
| Upgrade pip | `python -m pip install -U pip` |
| Install runtime deps only | `pip install -e .` |
| Install dev extras | `pip install -e '.[dev]'` |
| Build wheel & sdist | `python -m build` |
| Publish wheel (PyPI) | `twine upload dist/*` |

---

## 7 · Troubleshooting Snippets

* **`zsh: no matches found`** → quote: `pip install -e '.[dev]'`.
* **Package visible outside venv** → forgot to activate `.venv`.
* **Wheels missing for Python 3.13** → fallback to 3.12 venv or pin an earlier package version.

---
