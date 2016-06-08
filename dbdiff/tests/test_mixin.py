from dbdiff.test import DbdiffTestMixin

from django import test
from django.contrib.contenttypes.models import ContentType
from django.db import connection


class ContentTypeTestCase(DbdiffTestMixin, test.TestCase):
    dbdiff_models = [ContentType]
    dbdiff_exclude = {'*': ['created']}
    dbdiff_reset_sequences = True
    dbdiff_expected = 'dbdiff/tests/test_mixin.json'

    def test_db_import(self):
        if connection.vendor != 'postgresql':
            return  # not supported for now
        super(ContentTypeTestCase, self).test_db_import()
        self.assertTrue(self.dbdiff_test_executed)

    def dbdiff_test(self):
        ContentType.objects.create()
        self.dbdiff_test_executed = True
