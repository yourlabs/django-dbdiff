import os

from django import test
from django.conf import settings

from . import base
from ..exceptions import EmptyFixtures
from ..fixture_diff import FixtureDiff


class FixtureDiffTest(test.TestCase):
    def setUp(self):
        self.diff = FixtureDiff(base.TEST_FIXTURE)

    def test_fixture_path(self):
        assert self.diff.fixture_path == os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '..',
            'fixtures',
            'dbdiff_test.json'
        ))

    def test_indent(self):
        assert self.diff.fixture_indent == 4

        with self.assertRaises(EmptyFixtures):
            FixtureDiff('dbdiff/fixtures/empty.json').fixture_indent

    def test_get_models(self):
        assert len(self.diff.fixture_models) == 1
        # Unfortunnately django's default AUTH_USER_MODEL is auth.user but
        # fixtures use auth.User.
        assert (self.diff.fixture_models[0]
                == settings.AUTH_USER_MODEL.lower())

    def test_clean(self):
        self.diff.get_diff()
        assert os.path.exists(self.diff.dump_path)
        self.diff.clean()
        assert not os.path.exists(self.diff.dump_path)
