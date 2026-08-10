# Translation testing policy (evan-public-data)

## Who maintains which languages

- **English (`reference.EN.json`) and Chinese (`reference.ZH_CN.json`)** are
  the default languages and the **source of truth** for display text. They
  are maintained directly by the product owner. **No unit tests assert their
  exact wording** — wording-locking tests would churn with every edit.
  Structural tests (key coverage, non-empty values, group/label parity) stay.
- **Languages outside the owner's scope** (Arabic today; any future language
  the owner has not learned) are **translation-accuracy contracts**: every
  key in the locale file MUST be covered by a unit test that asserts the
  exact translated value, so contributors cannot silently break accuracy the
  owner cannot see.

## Rules

1. Do not write wording-assertion tests for `EN` / `ZH_CN`.
2. For every non-scope language, maintain
   `tests/test_<locale>_translation_accuracy.py` covering **100%** of:
   - `activities`
   - `contexts`
   - `locationCategories`
   - `locationCategoryGroups`
3. Structural validation in `tests/test_reference.py` runs for every locale:
   key parity with `reference.json`, non-empty values, and a hard gate that
   fails when a non-EN/ZH locale file exists without its accuracy test.
4. When a translation must change, update the locale file AND the accuracy
   test together; the test is the reviewer for the languages the owner
   cannot read.

## Audit status (2026-08-11)

- EN and ZH have full structural coverage (no wording locks).
- No non-EN/ZH locale files exist yet; the accuracy-contract gate is ready
  for the first language (e.g. `reference.AR.json` +
  `tests/test_ar_translation_accuracy.py`).

## Adding a new language

1. Create `data/reference.<LOCALE>.json` with full key coverage
   (`activities`, `contexts`, `locationCategories`,
   `locationCategoryGroups`).
2. Write `tests/test_<locale>_translation_accuracy.py` from a native-speaker
   review (see `tests/README.md` for the template).
3. Run `python3 -m unittest discover -s tests -v`.
4. Register the locale in `reference.json` → `languages` and, when the app
   enables it, the frontend `AppLocales`/catalogs.
