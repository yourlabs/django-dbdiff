"""AppConfig for dbdiff."""

import os

from django.apps import AppConfig
from django.core.serializers import register_serializer


class DefaultConfig(AppConfig):
    """
    Default AppConfig for dbdiff.

    .. py:attribute:: debug

        If True, then diff commands will be printed to stdout and temporary
        files will not be deleted.
    """

    name = 'dbdiff'
    debug = False

    def ready(self):
        """
        Register dbdiff.serializers.json and set debug.

        Enables debug if a DBDIFF_DEBUG environment variable is found.
        """
        self.debug = os.environ.get('DBDIFF_DEBUG', False)
        register_serializer('json', 'dbdiff.serializers.json')
