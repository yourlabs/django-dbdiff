"""Smarter model pk sequence reset."""
from django.db import connection, models


def pk_sequence_get(model):
    """Return a list of table, column tuples which should have sequences."""
    for field in model._meta.get_fields():
        if not getattr(field, 'primary_key', False):
            continue
        if not isinstance(field, models.AutoField):
            continue
        return (field.db_column or field.column, field.model._meta.db_table)
    return (None, None)


def sequence_reset(model):
    """
    Better sequence reset than TransactionTestCase.

    The difference with using TransactionTestCase with reset_sequences=True is
    that this will reset sequences for the given models to their higher value,
    supporting pre-existing models which could have been created by a
    migration.
    """
    pk_field, table = pk_sequence_get(model)
    if not pk_field:
        return

    if connection.vendor == 'postgresql':
        reset = """
        SELECT
            setval(
                pg_get_serial_sequence('{table}', '{column}'),
                coalesce(max({column}),0) + 1,
                false
            )
        FROM {table}
        """
    elif connection.vendor == 'sqlite':
        reset = """
        UPDATE sqlite_sequence
        SET seq=(SELECT max({column}) from {table})
        WHERE name='{table}'
        """
    elif connection.vendor == 'mysql':
        cursor = connection.cursor()
        cursor.execute(
            'SELECT MAX({column}) + 1 FROM {table}'.format(
                column=pk_field, table=table
            )
        )
        result = cursor.fetchone()[0] or 0
        reset = 'ALTER TABLE {table} AUTO_INCREMENT = %s' % result

    connection.cursor().execute(
        reset.format(column=pk_field, table=table)
    )
