"""Structural validation for evan-public-data reference files.

Per TRANSLATIONS.md: EN and ZH_CN are product-owned source-of-truth
languages and are NOT wording-locked here — only key coverage/non-empty
values are checked. Any other locale must have a translation-accuracy
contract test (tests/test_<locale>_translation_accuracy.py) or the suite
fails.
"""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'

OWNED_LANGUAGES = {'EN', 'ZH_CN'}
GROUP_IDS = {'shops', 'nature', 'sport_venues', 'arts', 'communities', 'nightlife'}


def load_json(name):
    return json.loads((DATA / name).read_text(encoding='utf-8'))


def locale_files():
    return sorted(
        p.name
        for p in DATA.glob('reference.*.json')
        if p.name != 'reference.json'
        and not p.name.endswith('.schema.json')
    )


def locale_tag(filename):
    return filename.removeprefix('reference.').removesuffix('.json')


class TestReferenceStructural(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = load_json('reference.json')
        cls.activities = {
            a for ids in cls.ref['contexts'].values() for a in ids
        }
        for c in cls.ref['locationCategories']:
            cls.activities.update(c['activityIds'])
        for ids in cls.ref['amenityActivityGrants'].values():
            cls.activities.update(ids)

    def test_required_sections(self):
        for key in (
            'schemaVersion',
            'defaultLanguage',
            'languages',
            'contexts',
            'locationCategories',
            'amenityActivityGrants',
        ):
            self.assertIn(key, self.ref, key)

    def test_required_contexts(self):
        for context in (
            'alone',
            'social_group',
            'friends',
            'family',
            'romantic',
            'adultOnly',
            'parentChild',
        ):
            self.assertIn(context, self.ref['contexts'], context)

    def test_category_ids_unique(self):
        ids = [c['id'] for c in self.ref['locationCategories']]
        self.assertEqual(len(ids), len(set(ids)))

    def test_activity_ids_known(self):
        for c in self.ref['locationCategories']:
            unknown = set(c['activityIds']) - self.activities
            self.assertEqual(unknown, set(), c['id'])
        for grant, ids in self.ref['amenityActivityGrants'].items():
            unknown = set(ids) - self.activities
            self.assertEqual(unknown, set(), grant)

    def test_groups_are_valid(self):
        groups = {
            c['group'] for c in self.ref['locationCategories'] if c.get('group')
        }
        self.assertTrue(groups.issubset(GROUP_IDS), groups - GROUP_IDS)

    def test_icons_are_complete_and_well_formed(self):
        category_icons = self.ref.get('locationCategoryIcons', {})
        group_icons = self.ref.get('locationCategoryGroupIcons', {})
        for c in self.ref['locationCategories']:
            self.assertTrue(
                category_icons.get(c['id'], '').strip(),
                f'category {c["id"]} has no icon key',
            )
        groups = {
            c['group'] for c in self.ref['locationCategories'] if c.get('group')
        }
        for group in groups:
            self.assertTrue(
                group_icons.get(group, '').strip(),
                f'group {group} has no icon key',
            )
        for key in [*category_icons.values(), *group_icons.values()]:
            self.assertRegex(key, r'^[a-z0-9_]+$', key)


class TestLocaleFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = load_json('reference.json')
        cls.activities = {
            a for ids in cls.ref['contexts'].values() for a in ids
        }
        for c in cls.ref['locationCategories']:
            cls.activities.update(c['activityIds'])
        cls.categories = {c['id'] for c in cls.ref['locationCategories']}
        cls.groups = {
            c['group'] for c in cls.ref['locationCategories'] if c.get('group')
        }
        cls.contexts = set(cls.ref['contexts'])

    def test_every_locale_is_complete(self):
        for filename in locale_files():
            with self.subTest(file=filename):
                locale = load_json(filename)
                for section in ('activities', 'contexts', 'locationCategories'):
                    self.assertIn(section, locale, section)
                    self.assertTrue(locale[section], section)
                for activity in sorted(self.activities):
                    self.assertTrue(
                        locale['activities'].get(activity, '').strip(),
                        f'{filename}: activity {activity}',
                    )
                for context in sorted(self.contexts):
                    self.assertTrue(
                        locale['contexts'].get(context, '').strip(),
                        f'{filename}: context {context}',
                    )
                for category in sorted(self.categories):
                    self.assertTrue(
                        locale['locationCategories'].get(category, '').strip(),
                        f'{filename}: category {category}',
                    )
                if self.groups:
                    groups = locale.get('locationCategoryGroups', {})
                    for group in sorted(self.groups):
                        self.assertTrue(
                            groups.get(group, '').strip(),
                            f'{filename}: group {group}',
                        )

    def test_event_ingestion_keywords_and_groups(self):
        ingestion = self.ref.get('eventIngestion')
        self.assertIsNotNone(ingestion, 'eventIngestion section is required in reference.json')
        group_kws = ingestion.get('groupKeywords', {})
        for group in GROUP_IDS:
            self.assertIn(group, group_kws, f'groupKeywords missing group: {group}')
            self.assertTrue(len(group_kws[group]) > 0, f'groupKeywords for {group} must be non-empty')
        pricing = ingestion.get('pricingKeywords', {})
        self.assertIn('free', pricing)
        self.assertIn('bookingRequired', pricing)
        audience = ingestion.get('audienceKeywords', {})
        self.assertIn('adultOnly', audience)
        self.assertIn('kidsFriendly', audience)
        self.assertIn('petsFriendly', audience)

    def test_public_holidays(self):
        holidays = self.ref.get('publicHolidays')
        self.assertIsNotNone(holidays, 'publicHolidays section is required in reference.json')
        self.assertIn('GB', holidays)
        self.assertIn('US', holidays)
        for country, list_of_holidays in holidays.items():
            self.assertTrue(len(list_of_holidays) > 0, f'{country} holidays must not be empty')
            for h in list_of_holidays:
                self.assertTrue(h.get('id'), f'holiday in {country} missing id')
                self.assertTrue(h.get('name'), f'holiday in {country} missing name')
                self.assertGreaterEqual(h.get('leadDaysNotice', 0), 1)
                self.assertTrue(len(h.get('suggestedActivities', [])) > 0)


if __name__ == '__main__':
    unittest.main()
