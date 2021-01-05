import typing

import click
import pluggy

from together.hookspec import TogetherSpec

hook = pluggy.HookimplMarker("together")


def _traverse_click(cur, path, parent_ctx=None):
    if not path:
        return cur

    name = path[0]
    with click.Context(cur, info_name=name, parent=parent_ctx) as ctx:
        nextcmd = cur.get_command(ctx, name)
        return _traverse_click(nextcmd, path[1:], parent_ctx=ctx)


def _traverse_click_tree_to_parent(root_cmd, path):
    if path[0] != root_cmd.name:
        raise ValueError(
            f"expected name for root to be {root_cmd.name}, "
            f"but path started with {path[0]}"
        )
    return _traverse_click(root_cmd, path[1:])


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


class TogetherCLI:
    def __init__(self):
        self.plugin_manager = pluggy.PluginManager("together")
        self.plugin_manager.add_hookspecs(TogetherSpec)
        self.register_plugins()

        self.root_command = None
        self.subcommands = None
        self.subcommand_collections = None
        self.all_subcommands = None

    def register_plugins(self):
        """
        By default, `together` loads plugins from entry points under the
        'together' namespace in setuptools entrypoints. However, you can
        subclass TogetherCLI and override this method in order to provide
        custom plugin loading.
        """
        self.plugin_manager.load_setuptools_entrypoints("together")

    def build(self):
        self.root_command = self.plugin_manager.hook.register_root_command()
        if not isinstance(self.root_command, click.MultiCommand):
            raise TypeError(
                f"Cannot register a non-MultiCommand root: {self.root_command}"
            )

        # plugins will fire in LIFO order (part of the pluggy specification),
        # but we want to register subcommands in FIFO order
        # therefore, reverse the order of the subcommands for registration
        self.subcommands = reversed(self.plugin_manager.hook.register_subcommand())
        # repeat this activity, but with sets of subcommands
        self.subcommand_collections = reversed(
            self.plugin_manager.hook.register_subcommand_collection()
        )

        self.all_subcommands = list(self.subcommands) + [
            c for cs in self.subcommand_collections for c in cs
        ]

        for registration in self.all_subcommands:
            cmd, path = registration.command, registration.path

            # traverse the path to find the parent command
            if not path:
                parent = self.root_command
            else:
                parent = _traverse_click_tree_to_parent(self.root_command, path)

            parent.add_command(cmd)

        return self.root_command
