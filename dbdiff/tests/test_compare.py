"""Public API tests."""

from __future__ import unicode_literals

import os
import tempfile

from django import test
from django.contrib.auth.models import Group

import six

from ..exceptions import DiffFound, FixtureCreated
from ..fixture import Fixture


class SmokeTest(test.TransactionTestCase):
    def setUp(self):
        fd, self.fixture_path = tempfile.mkstemp(suffix='_dbdiff')

    def test_000_fixture_auto_create(self):
        fixture = Fixture(self.fixture_path, models=[Group])

        # Should auto-create the diff
        if fixture.exists:
            os.unlink(fixture.path)

        Group.objects.create(name='testgroup')

        with self.assertRaises(FixtureCreated):
            fixture.assertNoDiff()

        assert fixture.exists

        with open(self.fixture_path, 'r') as f:
            result = f.read()

        expected = '''[
{
    "fields": {
        "name": "testgroup",
        "permissions": []
    },
    "model": "auth.group",
    "pk": 1
}
]'''

        assert expected.strip() == result.strip()

        # It should pass now
        fixture.assertNoDiff()

        # It should break now !
        Group.objects.all().update(name='BOOM')
        with self.assertRaises(DiffFound) as e:
            fixture.assertNoDiff()

        expected = '''
@@ -3,3 +3,3 @@
     "fields": {
-        "name": "testgroup",
+        "name": "BOOM",
         "permissions": []
'''.lstrip()

        diff = e.exception.message if six.PY2 else e.exception.args[0]
        result = '\n'.join(diff.split('\n')[1:])
        assert result == expected
