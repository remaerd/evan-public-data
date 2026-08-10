# Frienday Public Activity & Venue Data

Context-first public reference data for Frienday. `reference.json` is structural (IDs only) and `reference.{LOCALE}.json` files hold display text. This is the runtime source of truth per ADR-0038 D1 and ADR-0055 Option C — not a database table.

## Structure

```
data/
├── reference.json                    # Structural, context-first reference (IDs only)
├── reference.EN.json                 # English display names
├── reference.ZH_CN.json              # Simplified Chinese display names
├── reference.schema.json             # JSON Schema for reference.json
└── reference-language.schema.json    # JSON Schema for locale files
```

## reference.json

Activities are simple IDs. **`contexts` is the primary index**: it maps who is joining (`alone`, `social_group`, `friends`, `family`, `romantic`) to the activity IDs that fit.

```json
{
  "schemaVersion": 3,
  "defaultLanguage": "EN",
  "languages": ["EN", "ZH_CN"],
  "contexts": {
    "friends": ["coffee", "dinner", "picnic", "walk", "cinema"],
    "romantic": ["coffee", "dinner", "walk", "dating"]
  },
  "locationCategories": [
    {"id": "park", "isPublicVenue": true, "sourceTags": ["park", "garden"], "activityIds": ["walk", "picnic", "parade"]},
    {"id": "shopping_centre", "isPublicVenue": true, "sourceTags": ["shopping_mall"], "group": "shops", "activityIds": ["shopping", "coffee", "food_tour", "sightseeing"]}
  ],
  "amenityActivityGrants": {
    "cafe": ["coffee", "brunch", "lunch"]
  }
}
```

### Key points

- Activities do **not** store contexts or category groups; contexts are the top-level index.
- `adultOnly` is a first-class context; it is only surfaced in the frontend after age verification.
- `parentChild` is a first-class context for activities parents and children can do together.
- Nature locations (`beach`, `forest`, `lake`, `mountain`, `nature_reserve`, `river`, `botanical_garden`) and expanded Home/Workplace activities are included in `locationCategories`/`contexts`.
- Shopping is split by product type (`supermarket`, `department_store`, `boutique`, `bookstore`, `electronics_store`, `toy_store`, `home_decor_store`, `antique_market`) with matching shopping activities.
- `sort_order` is not needed; ordering is driven by context.
- `min_age` is not part of the reference schema; age is handled app-wide.
- `locationCategories` are the canonical location types (public venues plus Home, Workplace, Institution) and their compatible activity IDs.
- Optional `group` on a location category merges fine-grained categories into one user-facing section: `shops`, `nature`, `sport_venues`, `arts`, `communities`. The IDs and `sourceTags` stay fine-grained for ingestion; consumers use `locationCategoryGroups` for the merged display name.
- `locationCategoryIcons` / `locationCategoryGroupIcons` map each category/group to a Material icon key (e.g. `shopping_bag`, `forest`, `church`). The frontend keeps only a small key→glyph table; which key applies to which venue/group is data-driven, so new venues adapt without code changes.
- `amenityActivityGrants` add activities a venue can support based on detected amenities (e.g. a museum with a cafeteria gains `coffee`).

## reference.EN.json / reference.ZH_CN.json

Localized display text is keyed by the same IDs:

```json
{
  "contexts": { "friends": "Friends", "romantic": "Romantic" },
  "activities": { "coffee": "Coffee", "picnic": "Picnic in the park" },
  "locationCategories": { "park": "Park & open space", "church": "Church" },
  "locationCategoryGroups": {
    "shops": "Shops",
    "nature": "Nature",
    "sport_venues": "Sport Venues",
    "arts": "Arts",
    "communities": "Communities"
  }
}
```

## Consumption

- **Runtime source of truth (ADR-0055, Option C):** backend fetches `reference.json`; frontend fetches `reference.json` + `reference.{LOCALE}.json`. Default URL: `https://raw.githubusercontent.com/remaerd/evan-public-data/main/data`, overridable with `PUBLIC_DATA_BASE_URL`.
- **Backend** (`evan-backend`) uses `locationCategories` and `amenityActivityGrants` during venue ingestion to derive `ingestion.venues.activity_tags`.
- **Frontend** (`evan_frontend_mobile`) uses `contexts` first for activity suggestions, then intersects with the selected location category and amenity grants.
- **Fallback:** `python3 scripts/generate_snapshots.py` regenerates the bundled TS/Dart fallback snapshots; they are resilience caches only.
- Changing data here takes effect on the next backend re-ingestion/revalidation and the next frontend fetch — no consumer code release is required.

## Testing policy

English (`reference.EN.json`) and Chinese (`reference.ZH_CN.json`) are the
product-owned source-of-truth languages: their wording is maintained directly
and is **not** locked by unit tests. Any other language is a
translation-accuracy contract with exact-value tests. See
[`TRANSLATIONS.md`](TRANSLATIONS.md) and
[`tests/README.md`](tests/README.md).

```bash
python3 -m unittest discover -s tests -v
```
