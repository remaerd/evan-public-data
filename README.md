# Frienday Activity Category Data

Per-country activity reference data for Frienday. Bundled into the app at build time — NOT stored in the database (per ADR-0038 D1).

## Structure

```
data/
├── global.json          # Base activities (language-agnostic)
├── countries/
│   ├── GB.json          # United Kingdom (age threshold: 18)
│   ├── US.json          # United States (age threshold: 21 for some activities)
│   └── ...
└── schema.json          # JSON Schema for validating activity data
```

## Activity Object

```json
{
  "id": "coffee",
  "display_name": "Coffee meetup",
  "category_group": "social",
  "min_age": 18,
  "sort_order": 1
}
```

### Fields

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier (kebab-case) |
| `display_name` | string | Human-readable label |
| `category_group` | string | Grouping: social, active, creative, outdoor, food, culture, volunteering |
| `min_age` | integer | Minimum age for this activity in this country (per local regulation) |
| `sort_order` | integer | Display order |

### Notes

- No `on_my_own` section (per ADR-0038 — activities are about doing things together)
- No `is_age_gated` boolean — replaced with `min_age` integer per country regulation
- The app fetches activities for the user's country at build time
- Activity data is versioned via git (not a database table)