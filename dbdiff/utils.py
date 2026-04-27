"""Utils for dbdiff."""

import os
from importlib.util import find_spec

from django.apps import apps
from django.db import connections


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


def diff(expected, result, ignore_pk=False):  # noqa: C901
    """Return unexpected, missing and diff between expected and result.

    When ignore_pk is True, records are matched by their field values (content)
    instead of primary key. Records with the same content but different pks
    are considered matching.
    """
    missing, different = {}, {}

    if ignore_pk:
        unexpected, missing, different = _diff_by_content(expected, result)
        return unexpected, missing, different

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

            different.setdefault(model, {}).setdefault(pk, {})

            for expected_field, expected_value in expected_fields.items():
                result_value = result_fields[expected_field]

                if expected_value == result_value:
                    continue

                different[model][pk][expected_field] = (
                    expected_value,
                    result_value
                )
    return unexpected, missing, different


def _diff_by_content(expected, result):  # noqa: C901
    """Diff by matching records on field content instead of primary key."""
    unexpected, missing, different = {}, {}, {}

    for model in set(expected.keys()) | set(result.keys()):
        expected_list = list(expected.get(model, {}).items())
        result_list = list(result.get(model, {}).items())
        matched_result_indices = set()

        for exp_pk, exp_fields in expected_list:
            found = False
            for i, (res_pk, res_fields) in enumerate(result_list):
                if i in matched_result_indices:
                    continue
                if exp_fields == res_fields:
                    matched_result_indices.add(i)
                    found = True
                    break
            if not found:
                missing.setdefault(model, {})
                missing[model][exp_pk] = exp_fields

        for i, (res_pk, res_fields) in enumerate(result_list):
            if i not in matched_result_indices:
                unexpected.setdefault(model, {})
                unexpected[model][res_pk] = res_fields

    return unexpected, missing, different


def get_absolute_path(path):
    """Return the absolute path to an app-relative path."""
    if path.startswith('/'):
        return path

    if path.startswith('.'):
        module_path = '.'
    else:
        spec = find_spec(path.split('/')[0])
        module_path = spec.submodule_search_locations[0]

    return os.path.abspath(os.path.join(
        module_path,
        *path.split('/')[1:]
    ))


def get_model_names(model_classes):
    """Return model names for model classes."""
    return [
        m if isinstance(m, str)
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
    """Monkeypatch TransactionTestCase._reset_sequences to support SQLite.

    Safe to call once, from AppConfig.ready(). Calling it a second time would
    wrap the already-patched classmethod again; the inner _needs_explicit_cls
    check would then see a classmethod and call _original(db_name), passing
    db_name correctly, so double-patching doesn't break anything — but callers
    should avoid it anyway.
    """
    import inspect

    from django.test.testcases import TransactionTestCase

    _raw = inspect.getattr_static(TransactionTestCase, '_reset_sequences')
    # Capture the already-resolved callable before we replace it.
    # For classmethod/staticmethod, the descriptor protocol strips the
    # wrapper so TransactionTestCase._reset_sequences(db_name) works.
    # For a plain function (Django 4.x), it needs an explicit first arg.
    _needs_explicit_cls = not isinstance(_raw, (classmethod, staticmethod))
    _original = TransactionTestCase._reset_sequences

    def _sqlite_reset(db_name):
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

    # Always install as @classmethod so Django 5.x (which calls
    # cls._reset_sequences(db_name)) passes db_name in the right position.
    # Django 4.x calls self._reset_sequences(db_name) on instances, which
    # also works because classmethods accept both call styles.
    @classmethod
    def new_reset_sequences(cls, db_name):  # noqa: N805
        if _needs_explicit_cls:
            _original(cls, db_name)
        else:
            _original(db_name)
        _sqlite_reset(db_name)

    TransactionTestCase._reset_sequences = new_reset_sequences
