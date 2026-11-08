# Learning progress

Claude reads this at the start of every session and updates it after each finished assignment (see `CLAUDE.md`).

## Current level

Beginner–intermediate (after lesson 1). Comfortable with loops, f-strings and reading tracebacks once pointed at them; needs work on truthiness, test design and Python idioms. Keep steps small and always ask for a negative test case. Uses Git Bash: give commands in bash syntax.

## Next up

Fix up the existing code before building on it. One assignment each:

1. ~~**Packaging**~~: done 2026-11-08.
2. **Packages and imports:** add the missing `__init__.py` files; rename `accesibility.py` → `accessibility.py`.
3. **Screenshot capture:** make `capture_window()` in `screenshot.py` work with `mss` (context managers, saving PNGs).
4. **First real tests:** pytest tests for `Rect.center` and `WindowInfo`; commit `tests/` without `__pycache__`.
5. **CLI:** replace the placeholder `test` command with `inspect` (argparse subcommands).

After that: milestone M1 in `plan/Project Plan.md` §15 (accessibility tree, observer, input actions, kill switch).

## Done

| Date | Assignment | Concepts | Revisit |
|---|---|---|---|
| 2026-11-08 | Lesson 1: real dependencies in `pyproject.toml` (`mss`, `pywin32`, `dev` extra with pytest); `tests/test_packaging.py` (9 tests) | `[project] dependencies`, optional-dependencies, distribution vs import name, editable install (live code, frozen metadata), egg-info vs dist-info, `importlib.metadata`, pytest basics, helper functions, negative tests | Final helper + negative tests came via `override`. Explained keyword params vs `**kwargs` and `startswith` vs `in` correctly. |

## Weak spots to revisit

- **Truthiness of return values**: used `any(s.find(...))`, where `find` returns 0/-1, so the helper was always `True`. Revisit truthy/falsy values.
- **Tests that can't fail**: didn't see the need for negative tests until shown. Ask "how could this test fail?" in later reviews.
- **Module-level code in test files**: put the logic at import time once. Watch for this.
- Warm-up basics check (dataclass, `@property`, venv, pytest discovery) was never answered, so the level is still not fully assessed.
