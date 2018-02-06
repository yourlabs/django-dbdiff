"""Public fixture API."""

import json
import os
import tempfile

from django.apps import apps
from django.core.management import call_command

import ijson

from .exceptions import DiffFound, FixtureCreated
from .utils import (
    diff,
    get_absolute_path,
    get_model_names,
    get_tree,
)


class Fixture(object):
    """
    Is able to print out diffs between database and a fixture.

    .. py:attribute:: path

        Absolute path to the fixture.

    .. py:attribute:: models

        List of models concerned by the fixture.

    .. py:attribute:: database

        Database name to use, 'default' by default.
    """

    def __init__(self, relative_path, models=None, database=None):
        """
        Instanciate a FixtureDiff on a database.

        relative_path is used to calculate :py:attr:`path`, with
        :py:func:`~utils.get_absolute_path`.

        If models is None, then it will be generated from reading the
        fixture file, but generated fixtures will include all models.

        database should be the name of the database to use, `default` by
        default.
        """
        self.path = get_absolute_path(relative_path)
        self.models = models if models else self.parse_models()
        self.database = database or 'default'

    def parse_models(self):
        """Return the list of models inside the fixture file."""
        with open(self.path, 'r') as f:
            return [apps.get_model(i.lower())
                    for i in ijson.items(f, 'item.model')]

    @property
    def exists(self):
        """Return True if :py:attr:`path` exists."""
        return os.path.exists(self.path)

    @property
    def indent(self):
        """Return the indentation of the fixture file or the default indent."""
        if not os.path.exists(self.path):
            return apps.get_app_config('dbdiff').default_indent

        with open(self.path, 'r') as f:
            line = f.readline()

            while line and ':' not in line:
                line = f.readline()

            if not line:
                return apps.get_app_config('dbdiff').default_indent

            return len(line) - len(line.lstrip(' '))

    def diff(self, exclude=None):
        """
        Diff the fixture against a datadump of fixture models.

        If passed, exclude should be a list of field names to exclude from
        being diff'ed.
        """
        fh, dump_path = tempfile.mkstemp('_dbdiff')

        with os.fdopen(fh, 'w') as f:
            self.dump(f)

        with open(self.path, 'r') as e, open(dump_path, 'r') as r:
            expected, result = json.load(e), json.load(r)

        unexpected, missing, different = diff(
            get_tree(expected, exclude),
            get_tree(result, exclude),
        )

        if not unexpected and not missing and not diff:
            os.unlink(dump_path)
            return None

        return unexpected, missing, different

    def load(self):
        """Load fixture into the database."""
        call_command('loaddata', self.path)

    def dump(self, out):
        """Write fixture with dumpdata for fixture models."""
        call_command(
            'dumpdata',
            *get_model_names(self.models),
            format='json',
            traceback=True,
            indent=self.indent,
            stdout=out,
            use_natural_foreign_keys=True
        )

    def assertNoDiff(self, exclude=None):  # noqa
        """Assert that the fixture doesn't have any diff with the database.

        If the fixture doesn't exist then it's written but
        :py:class:`~exceptions.FixtureCreated` is raised.

        If a diff was found it will raise :py:class:`~exceptions.DiffFound`.
        """
        if not self.exists:
            with open(self.path, 'w+') as f:
                self.dump(f)
            raise FixtureCreated(self)

        unexpected, missing, different = self.diff(exclude=exclude)

        if unexpected or missing or different:
            raise DiffFound(self, unexpected, missing, different)

    def __str__(self):
        """Return :py:attr:`path` for string representation."""
        return self.path
