import os

from django import test
from django.contrib.auth.models import Group

from ..fixture import Fixture


class FixtureTest(test.TransactionTestCase):
    def setUp(self):
        self.fixture = Fixture('dbdiff/fixtures/dbdiff_test_group.json')

    def test_fixture_path(self):
        assert self.fixture.path == os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '..',
            'fixtures',
            'dbdiff_test_group.json'
        ))

    def test_indent(self):
        assert self.fixture.indent == 4

    def test_models(self):
        assert self.fixture.models == [Group]

    def test_diff_exact_match_returns_none(self):
        # Regression: the always-False `not diff` (imported function) bug
        # caused diff() to never return None, leaking temp files and breaking
        # assertNoDiff() with a TypeError on exact matches.
        # Fixture: # [{"model": "auth.group", "pk": 1,
        # "fields": {"name": "initial_name"}}]
        Group.objects.create(id=1, name='initial_name')
        assert self.fixture.diff() is None
