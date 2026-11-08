# Learning progress

Claude reads this at the start of every session and updates it after each finished assignment (see `CLAUDE.md`).

## Current level

Not assessed yet. The first session should start with a short check of Python basics (functions, classes, dataclasses, imports/packages, virtual environments, pytest) to set the difficulty.

## Next up

Fix up the existing code before building on it. One assignment each:

1. **Packaging:** declare real dependencies in `pyproject.toml`; understand `src/` layout, editable installs, entry points.
2. **Packages and imports:** add the missing `__init__.py` files; rename `accesibility.py` → `accessibility.py`.
3. **Screenshot capture:** make `capture_window()` in `screenshot.py` work with `mss` (context managers, saving PNGs).
4. **First real tests:** pytest tests for `Rect.center` and `WindowInfo`; commit `tests/` without `__pycache__`.
5. **CLI:** replace the placeholder `test` command with `inspect` (argparse subcommands).

After that: milestone M1 in `plan/Project Plan.md` §15 (accessibility tree, observer, input actions, kill switch).

## Done

| Date | Assignment | Concepts | Revisit |
|---|---|---|---|
| | | | |

## Weak spots to revisit

- (none yet)
