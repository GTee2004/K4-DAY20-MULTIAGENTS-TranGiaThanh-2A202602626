---
name: safe-python-maintenance
description: Use when fixing bugs in a Python package with repository tests and release documentation.
---
- Inspect the implementation and run the existing tests before editing.
- Treat existing files under `tests/` as read-only; add new tests instead of changing them.
- Add a public function’s type annotations to every parameter and its return value.
- Add one regression test for each bug fixed, with at least three regression tests when required.
- Record every fix under `## Unreleased` in `CHANGELOG.md`, using one `- fix(<function name>): <short description>` bullet per fix.
- Run the full test suite and confirm the new regression tests pass.
