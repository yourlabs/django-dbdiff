"""Public API tests."""

from __future__ import unicode_literals

import os

from django import test
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Group

import mock

import six

from . import base
from .project.decimal_test.models import TestModel as DecimalTestModel
from .. import dbdiff
from ..exceptions import DiffFound


@mock.patch('dbdiff.dbdiff.FixtureDiff')
class CleanTest(test.TestCase):
    def setUp(self):
        self.old_debug = dbdiff.DEBUG

    def tearDown(self):
        dbdiff.DEBUG = self.old_debug

    def make_get_diff_raise(self, FixtureDiff):  # noqa
        setattr(
            FixtureDiff(fixture=base.TEST_FIXTURE).get_diff,
            'side_effect',
            Exception('BOOOM!!')
        )

    def test_exception_raised_and_debug_true_does_not_clean(self, FixtureDiff):  # noqa
        dbdiff.DEBUG = True
        self.make_get_diff_raise(FixtureDiff)
        with self.assertRaises(Exception):
            dbdiff.diff('aoeu')
        FixtureDiff(fixture=base.TEST_FIXTURE).clean.assert_not_called()

    def test_exception_raised_and_debug_false_cleans(self, FixtureDiff):  # noqa
        dbdiff.DEBUG = False
        self.make_get_diff_raise(FixtureDiff)
        with self.assertRaises(Exception):
            dbdiff.diff('aeou')
        FixtureDiff(fixture=base.TEST_FIXTURE).clean.assert_called_once_with()

    def test_debug_true_does_not_clean(self, FixtureDiff):  # noqa
        dbdiff.DEBUG = True
        dbdiff.diff(base.TEST_FIXTURE)
        FixtureDiff(fixture=base.TEST_FIXTURE).clean.assert_not_called()

    def test_debug_false_cleans(self, FixtureDiff):  # noqa
        dbdiff.DEBUG = False
        dbdiff.diff(base.TEST_FIXTURE)
        FixtureDiff(fixture=base.TEST_FIXTURE).clean.assert_called_once_with()


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


class ResetModelsTest(test.TestCase):
    def test_pk_reset(self):
        fixture = 'dbdiff/fixtures/dbdiff_test_group.json'
        Group.objects.create(name='noise')

        with dbdiff.exact(fixture):
            Group.objects.create(name='initial_name')

        with dbdiff.exact(fixture, reset_models=False):
            pass

        with self.assertRaises(DiffFound) as e:
            with dbdiff.exact(fixture):
                Group.objects.create(name='different_name')

        expected = six.b('''
@@ -3,3 +3,3 @@
     "fields": {
-        "name": "initial_name",
+        "name": "different_name",
         "permissions": []
''').lstrip()

        if six.PY2:
            assert e.exception.message == expected
        else:
            assert e.exception.args[0] == expected


class DecimalDiffTest(test.TestCase):
    fixtures = ['decimal_test_fixture']
    expected = os.path.join(
        'dbdiff',
        'tests',
        'project',
        'decimal_test',
        'fixtures',
        'decimal_test_expected.json'
    )
    model = DecimalTestModel

    def test_data_diff_is_empty(self):
        assert not dbdiff.diff(self.expected)

    def test_data_diff_has_changed(self):
        model = self.model.objects.first()
        model.test_field = '3.100'
        model.save()

        assert not dbdiff.diff(self.expected.replace('_expected', '_changed'))
