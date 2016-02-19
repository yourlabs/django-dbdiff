"""Exceptions for dbdiff module."""
import pprint


class DbDiffException(Exception):
    """Base exception for this app."""


class DiffFound(DbDiffException):
    """Raised when a diff is found by the context manager."""

    def _add_messages(self, msg, title, tree):
        if tree:
            for model, instances in tree.items():
                msg.append(
                    title % (
                        len(instances),
                        model
                    )
                )

                for pk, fields in instances.items():
                    msg.append('#%s:\n%s' % (pk, pprint.pformat(fields)))

    def __init__(self, fixture, unexpected, missing, diff):
        """Exception for when a diff was found."""
        msg = ['Diff found with dump at %s' % fixture.path]

        self._add_messages(
            msg,
            '%s unexpected instance(s) of %s found in the dump:',
            unexpected
        )

        self._add_messages(
            msg,
            '%s expected instance(s) of %s missing from dump:',
            missing
        )

        if diff:
            for model, instances in diff.items():
                msg.append(
                    '%s instance(s) of %s have not expected fields' % (
                        len(instances),
                        model
                    )
                )

                for pk, fields in instances.items():
                    msg.append('#%s:' % pk)

                    for field, values in fields.items():
                        msg.append('  %s:' % field)
                        msg.append('- %s' % pprint.pformat(values[0]))
                        msg.append('+ %s' % pprint.pformat(values[1]))

        super(DiffFound, self).__init__('\n'.join(msg))


class FixtureCreated(DbDiffException):
    """
    Raised when a fixture was created.

    This purposely fails a test, to avoid misleading the user into thinking
    that the test was properly executed against a versioned fixture. Imagine
    one pushes a test without the fixture, it will break because of this
    exception in CI.

    However, this should only happen once per fixture - unless the user in
    question forgets to commit the generated fixture !
    """
