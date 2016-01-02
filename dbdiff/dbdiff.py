"""Public API for dbdiff."""

from django.apps import apps

from .fixture_diff import FixtureDiff

__all__ = ('diff',)

DEBUG = apps.get_app_config('dbdiff').debug


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
        raise

    if not DEBUG:
        diff.clean()

    return out
