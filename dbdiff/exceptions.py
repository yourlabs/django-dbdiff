"""Exceptions for dbdiff module."""


class DbDiffException(Exception):
    """Base exception for this app."""


class DiffFound(DbDiffException):
    """Raised when a diff is found by the context manager."""

    def __init__(self, cmd, out):
        """Exception for when a diff command had output."""
        super(DiffFound, self).__init__('%s\n%s' % (cmd, out.decode('utf8')))


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
