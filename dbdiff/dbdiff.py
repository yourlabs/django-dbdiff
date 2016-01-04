"""Public API for dbdiff."""

from django.apps import apps
from django.core.management.color import no_style
from django.db import connections

from .exceptions import DiffFound
from .fixture_diff import FixtureDiff

__all__ = ('diff',)

DEBUG = apps.get_app_config('dbdiff').debug


class exact(object):  # noqa
    """
    Context manager interface for dbdiff.

    To clean up the database from any model that's provided by the fixture on
    context enter, and raise a :py:class:`~dbdiff.exceptions.DiffFound` on
    context enter if any diff was found::

        with dbdiff.exact('your_app/tests/your_test_expected.json'):
            # do stuff

    .. py:attribute:: diff

        :py:class:`~dbdiff.fixture_diff.FixtureDiff` instance for fixture.

    .. py:attribute:: database

        Database to use, 'default' by default.

    .. py:attribute:: reset_models

        If False, do not delete models and reset PK sequences on context enter.
    """

    def __init__(self, fixture, reset_models=True, database=None):
        """Instanciate with a fixture."""
        self.diff = FixtureDiff(fixture)
        self.database = database if database else 'default'
        self.reset_models = reset_models

    def __enter__(self):
        if not self.reset_models:
            return self

        tables = set()

        for model_name in self.diff.fixture_models:
            model = apps.get_model(model_name)
            tables.add(model._meta.db_table)
            tables.update(f.m2m_db_table() for f in
                          model._meta.local_many_to_many)

        connection = connections[self.database]

        statements = connection.ops.sql_flush(
            no_style(),
            list(tables),
            connection.introspection.sequence_list(),
            True
        )
        if connection.settings_dict['ENGINE'] == 'django.db.backends.sqlite3':
            # Initially, we were just doing a model.objects.all().delete() in
            # this method, and it worked only in SQLite:
            # https://travis-ci.org/yourlabs/django-dbdiff/builds/100059628
            # That's why this method now uses sqlflush method, but then PKs are
            # not reset anymore in SQLite:
            # http://stackoverflow.com/questions/24098733/why-doesnt-django-reset-sequences-in-sqlite3  # noqa
            statements += [
                "UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='%s';" % t
                for t in tables
            ]
        cursor = connection.cursor()

        for statement in statements:
            cursor.execute(statement)

        return self

    def __exit__(self, exception_type, exception_value, traceback):
        out = self.diff.get_diff()

        if not out:
            self.diff.clean()
        else:
            print(self.diff.cmd)
            raise DiffFound(out)


def diff(fixture):
    """
    Return the diff between the database and a fixture file as a string.

    .. py:param:: fixture

        Name of the fixture to compare, in ``app_name/path/to/fixture.json``
        format. The path to app_name will be detected by importing its module,
        this enables one project to reuse a fixture from an app even if it is
        not in the fixtures directory of the app, ie. in
        app_name/tests/some_test/fixture.json.
    """
    diff = FixtureDiff(fixture=fixture)

    try:
        out = diff.get_diff()
    except:
        if not DEBUG:
            diff.clean()
        else:
            print(diff.cmd)
        raise

    if not DEBUG:
        diff.clean()

    return out
