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
