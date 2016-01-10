"""Utils for dbdiff."""

import imp
import os
import subprocess

from django.apps import apps
from django.db import connections


def diff(first, second):
    """Return the command and diff output between first and second paths."""
    cmd = 'diff -u1 %s %s | sed "1,2 d"' % (first, second)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out, err = proc.communicate()
    return cmd, out


def get_absolute_path(path):
    """Return the absolute path to an app-relative path."""
    if path.startswith('/'):
        return path

    module_path = imp.find_module(path.split('/')[0])[1]
    return os.path.abspath(os.path.join(
        module_path,
        *path.split('/')[1:]
    ))


def get_model_names(model_classes):
    """Return model names for model classes."""
    return ['%s.%s' % (m._meta.app_label, m._meta.model_name)
            for m in model_classes]


def get_models_tables(models):
    """Return the list of tables for the given models."""
    tables = set()

    for model in models:
        tables.add(model._meta.db_table)
        tables.update(f.m2m_db_table() for f in
                      model._meta.local_many_to_many)

    return list(tables)


def patch_transaction_test_case():
    """Monkeypatch TransactionTestCase._reset_sequences to support SQLite."""
    from django.test.testcases import TransactionTestCase
    TransactionTestCase.old_reset_sequences = \
        TransactionTestCase._reset_sequences

    def new_reset_sequences(self, db_name):
        self.old_reset_sequences(db_name)
        connection = connections[db_name]

        if connection.vendor != 'sqlite':
            return

        tables = get_models_tables(apps.get_models())
        statements = [
            "UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='%s';" % t
            for t in tables
        ]

        cursor = connection.cursor()

        for statement in statements:
            cursor.execute(statement)

    TransactionTestCase._reset_sequences = new_reset_sequences
