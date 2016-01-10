"""AppConfig for dbdiff."""

import os

from django.apps import AppConfig
from django.core.serializers import register_serializer

from .utils import patch_transaction_test_case


class DefaultConfig(AppConfig):
    """
    Register patched serializers and patch TransactionTestCase for sqlite.

    .. py:attribute:: debug

        If True, then diff commands will be printed to stdout and temporary
        files will not be deleted.
    """

    name = 'dbdiff'
    debug = False
    default_indent = 4

    def ready(self):
        """
        Register dbdiff.serializers.json and set debug.

        Enables debug if a DBDIFF_DEBUG environment variable is found.

        It is important to use serializers which dump data in a predictible way
        because this app relies on diff between an expected - user-generated
        and versioned - fixture and dumped database data. This method also
        overrides the default json serializer with dbdiff's.

        When dbdiff is installed, ``dumpdata`` will use its serializers which
        have predictible output and cross-database support, so fixtures dumped
        without dbdiff installed will have to be regenerated after dbdiff is
        installed to be usable with dbdiff.

        """
        self.debug = os.environ.get('DBDIFF_DEBUG', False)
        register_serializer('json', 'dbdiff.serializers.json')
        patch_transaction_test_case()
