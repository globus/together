import typing

import click


class SubcommandRegistration:
    """
    A command registration defines a command to attach to the CLI and an
    optional command path.

    The command path is a list of command names which must be traversed in
    order to attach the command to the CLI.
    For example, if the root command is `foo`, and you wish to register
    `foo bar`, `foo baz`, and `foo bar buzz`, you will want to produce the
    registrations

    >>> CommandRegistration(barcmd, ["foo"])
    >>> CommandRegistration(bazcmd, ["foo"])
    >>> CommandRegistration(buzzcmd, ["foo", "bar"])

    Furthermore, `barcmd` must be a MultiCommand.

    The path may be omitted, in which case it defaults to a registration to
    attach a command to the root command.

    Use ``SubcommandRegistration``s when registering commands.
    """

    def __init__(
        self, command: click.BaseCommand, path: typing.Optional[typing.List[str]] = None
    ):
        self.command = command
        self.path = path

    @classmethod
    def convert(cls, hook_output):
        """convert hook output, which can be a command, tuple of (cmd, path),
        SubcommandRegistration, or any non-tuple iterable of the aforementioned
        types (e.g. a list)

        the result will always be a list of SubcommandRegistrations"""
        if isinstance(hook_output, click.BaseCommand):
            return [cls(hook_output)]
        if isinstance(hook_output, tuple):
            return [cls(*hook_output)]

        try:
            iterator = iter(hook_output)
        except TypeError:  # not iterable
            return [hook_output]
        else:
            # recurse and unpack one layer of nesting to produce a flattened
            # list
            return [y for x in iterator for y in cls.convert(x)]
