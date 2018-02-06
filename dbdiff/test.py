"""Convenience test mixin."""
from django.core.management import call_command
from django.db import connection, models

from .fixture import Fixture


class DbdiffTestMixin(object):
    """
    Convenience mixin with better sequence resetting than TransactionTestCase.

    The difference with using TransactionTestCase with reset_sequences=True is
    that this will reset sequences for the given models to their higher value,
    supporting pre-existing models which could have been created by a
    migration.

    The test case subclass requires some attributes and an implementation of a
    ``dbdiff_test()`` method that does the actual import call that this
    should test. Example usage::

        class FrancedataImportTest(DbdiffTestMixin, test.TestCase):
            dbdiff_models = [YourModel]
            dbdiff_exclude = {'*': ['created']}
            dbdiff_reset_sequences = True
            dbdiff_expected = 'yourapp/tests/yourexpectedfixture.json'
            dbdiff_fixtures = ['your-fixtures.json']

            def dbdiff_test(self):
                fixture = os.path.join(
                    os.path.dirname(__file__),
                    'representatives_fixture.json'
                )

                with open(fixture, 'r') as f:
                    do_your_import.main(f)

    Supports postgresql.
    """

    def test_db_import(self):
        """Actual test method, ran by the test suite."""
        call_command('flush', interactive=False)

        for fixture in getattr(self, 'dbdiff_fixtures', []):
            call_command('loaddata', fixture)

        for model in self.dbdiff_models:
            if connection.vendor == 'postgresql':
                pk_field = None
                for field in model._meta.get_fields():
                    if getattr(field, 'primary_key', False):
                        pk_field = field
                        break

                if not isinstance(pk_field, models.AutoField):
                    continue

                if not pk_field.db_column:
                    continue

                reset = """
                SELECT
                    setval(
                        pg_get_serial_sequence('%(table)s', '%(column)s'),
                        coalesce(max(%(column)s),0) + 1,
                        false
                    )
                FROM %(table)s
                """ % dict(
                    table=model._meta.db_table,
                    column=pk_field.db_column,
                )
            else:
                raise NotImplemented()
            connection.cursor().execute(reset)

        self.dbdiff_test()

        Fixture(
            self.dbdiff_expected,
            models=self.dbdiff_models,
        ).assertNoDiff(
            exclude=self.dbdiff_exclude,
        )
