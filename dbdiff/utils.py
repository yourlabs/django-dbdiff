"""Utils for dbdiff."""

import imp
import os

from django.apps import apps
from django.db import connections

import six


def get_tree(dump, exclude=None):
    """Return a tree of model -> pk -> fields."""
    exclude = exclude or {}
    tree = {}

    for instance in dump:
        if instance['model'] not in tree:
            tree[instance['model']] = {}

        exclude_fields = exclude.get(instance['model'], [])
        exclude_fields += exclude.get('*', [])

        tree[instance['model']][instance['pk']] = {
            name: value for name, value in instance['fields'].items()
            if name not in exclude_fields
        }

    return tree


def _get_unexpected(expected, result):
    unexpected = {}

    for model, result_instances in result.items():
        expected_pks = expected.get(model, {}).keys()

        for pk, result_fields in result_instances.items():
            if pk in expected_pks:
                continue

            unexpected.setdefault(model, {})
            unexpected[model][pk] = result_fields

    return unexpected


def diff(expected, result):
    """Return unexpected, missing and diff between expected and result."""
    missing, diff = {}, {}

    unexpected = _get_unexpected(expected, result)

    for model, expected_instances in expected.items():
        for pk, expected_fields in expected_instances.items():
            if pk not in result.get(model, {}):
                missing.setdefault(model, {})
                missing[model][pk] = expected_fields
                continue

            result_fields = result[model][pk]
            if expected_fields == result_fields:
                continue

            diff.setdefault(model, {})
            diff[model].setdefault(pk, {})

            for expected_field, expected_value in expected_fields.items():
                result_value = result_fields[expected_field]

                if expected_value == result_value:
                    continue

                diff[model][pk][expected_field] = (
                    expected_value,
                    result_value
                )
    return unexpected, missing, diff


def get_absolute_path(path):
    """Return the absolute path to an app-relative path."""
    if path.startswith('/'):
        return path

    if path.startswith('.'):
        module_path = '.'
    else:
        module_path = imp.find_module(path.split('/')[0])[1]
    return os.path.abspath(os.path.join(
        module_path,
        *path.split('/')[1:]
    ))


def get_model_names(model_classes):
    """Return model names for model classes."""
    return [
        m if isinstance(m, six.string_types)
        else '%s.%s' % (m._meta.app_label, m._meta.model_name)
        for m in model_classes
    ]


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
