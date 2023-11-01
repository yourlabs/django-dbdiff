"""Public API tests."""

import os
import tempfile

from django import test
from django.contrib.auth.models import Group

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
        expected = '''
1 instance(s) of auth.group have not expected fields
#1:
  name:
- 'testgroup'
+ 'BOOM'
'''

        with self.assertRaises(DiffFound) as result:
            fixture.assertNoDiff()
        self.assert_message_is(expected, result)

        # Excluding the name parameter, there should be no diff
        fixture.assertNoDiff(exclude={'auth.group': ['name']})

        # Assert it finds unexpected model
        Group.objects.create(name='unexpected')
        expected = '''
1 unexpected instance(s) of auth.group found in the dump:
#2:
{'name': 'unexpected', 'permissions': []}
1 instance(s) of auth.group have not expected fields
#1:
  name:
- 'testgroup'
+ 'BOOM'
'''

        with self.assertRaises(DiffFound) as result:
            fixture.assertNoDiff()
        self.assert_message_is(expected, result)

        # Assert it finds missing model
        Group.objects.get(pk=1).delete()
        expected = '''
1 unexpected instance(s) of auth.group found in the dump:
#2:
{'name': 'unexpected', 'permissions': []}
1 expected instance(s) of auth.group missing from dump:
#1:
{'name': 'testgroup', 'permissions': []}
'''

        with self.assertRaises(DiffFound) as result:
            fixture.assertNoDiff()
        self.assert_message_is(expected, result)

    def assert_message_is(self, expected, result):
        msg = result.exception.args[0]
        out = '\n'.join(msg.split('\n')[1:])
        assert out.strip() == expected.strip()
