"""Public API tests."""

from __future__ import unicode_literals

from django import test
from django.apps import apps
from django.conf import settings

import six

from . import base
from .. import dbdiff


class DiffTest(test.TestCase):
    fixtures = ['dbdiff_test']

    def setUp(self):
        self.model = apps.get_model(settings.AUTH_USER_MODEL)

    def test_data_diff_is_empty(self):
        assert not dbdiff.diff(base.TEST_FIXTURE)

    def test_data_diff_has_changed(self):
        self.model.objects.all().update(username='test')
        assert dbdiff.diff(base.TEST_FIXTURE) == six.b('''
@@ -14,3 +14,3 @@
         "user_permissions": [],
-        "username": "jake"
+        "username": "test"
     },
''').lstrip()
