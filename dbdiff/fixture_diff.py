"""Internal API for dbdiff."""

import imp
import os
import subprocess
import tempfile

from django.apps import apps
from django.core.management import call_command

import ijson

from .exceptions import EmptyFixtures


class FixtureDiff(object):
    """
    Is able to print out diffs between database and a fixture.

    .. py:attribute:: fixture

        Formated path of the fixture to compare, it should be in the format of
        app_name/relative/path/to/fixture.json.

    .. py:attribute:: database

        Database name to use, 'default' by default.
    """

    def __init__(self, fixture, database=None):
        """Instanciate a FixtureDiff on a database."""
        self.database = database or 'default'
        self.fixture = fixture

    @property
    def fixture_path(self):
        """Return the absolute path to a fixture."""
        module_path = imp.find_module(self.fixture.split('/')[0])[1]
        return os.path.abspath(os.path.join(
            module_path,
            *self.fixture.split('/')[1:]
        ))

    @property
    def fixture_models(self):
        """Return the list of models inside the fixture file."""
        with open(self.fixture_path, 'r') as f:
            return [i.lower() for i in ijson.items(f, 'item.model')]

    @property
    def fixture_indent(self):
        """Return the indentation of the fixture file."""
        with open(self.fixture_path, 'r') as f:
            line = f.readline()

            while line and ':' not in line:
                line = f.readline()

            if not line:
                raise EmptyFixtures(self.fixture_path)

            return len(line) - len(line.lstrip(' '))

    def get_diff(self):
        """Dumpdata and return the diff output."""
        self.dump_fb, self.dump_path = tempfile.mkstemp('_dbdiff')

        with os.fdopen(self.dump_fb, 'w') as f:
            call_command('dumpdata', *self.fixture_models, format='json',
                         traceback=True, indent=self.fixture_indent,
                         stdout=f)

        self.cmd = 'diff -u1 %s %s | sed "1,2 d"' % (
            self.fixture_path, self.dump_path)

        if apps.get_app_config('dbdiff').debug:  # pragma: no cover
            print(self.cmd)

        proc = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, shell=True)
        out, err = proc.communicate()

        return out

    def clean(self):
        """Remove temporary files."""
        if getattr(self, 'dump_path', False):
            os.unlink(self.dump_path)
