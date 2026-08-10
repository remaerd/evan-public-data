# evan-public-data tests

Run the suite with:

```bash
python3 -m unittest discover -s tests -v
```

## What is tested

`test_reference.py` is **structural** for every locale:

- `reference.json` shape: unique category IDs, known activity IDs, valid
  `group` values, and grant references.
- Locale files (`reference.EN.json`, `reference.ZH_CN.json`, …): every
  activity/context/category/group key from `reference.json` has a non-empty
  label.
- **Accuracy gate:** any locale outside `EN` / `ZH_CN` must have a matching
  `tests/test_<locale>_translation_accuracy.py`. This forces a
  translation-accuracy contract before a language the owner cannot audit
  ships.

## Why EN/ZH have no wording tests

English and Chinese are product-owned source-of-truth languages. Their
exact wording is maintained directly and must not be locked by tests — see
[`TRANSLATIONS.md`](../TRANSLATIONS.md).

## Adding a language the owner cannot audit (e.g. Arabic)

1. Add `data/reference.AR.json` with full key coverage.
2. Create `tests/test_ar_translation_accuracy.py` and assert **every**
   translated value. Template:

```python
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ar = json.loads((ROOT / 'data' / 'reference.AR.json').read_text())

class ArTranslationAccuracy(unittest.TestCase):
    def test_activities(self):
        self.assertEqual(ar['activities']['coffee'], '<native translation>')
        # ... every activity key ...

    def test_contexts(self):
        self.assertEqual(ar['contexts']['friends'], '<native translation>')
        # ... every context key ...

    def test_location_categories(self):
        self.assertEqual(ar['locationCategories']['cafe'], '<native translation>')
        # ... every category key ...

    def test_location_category_groups(self):
        self.assertEqual(ar['locationCategoryGroups']['shops'], '<native translation>')
        # ... every group key ...
```

3. Run the suite; the accuracy gate in `test_reference.py` will also confirm
   the file exists.
