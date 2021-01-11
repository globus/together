import warnings

import click
import pluggy

from together.click_tools import traverse_click
from together.hookspec import TogetherSpec
from together.registration import SubcommandRegistration
from together.state import CommandState

hook = pluggy.HookimplMarker("together")


class TogetherCLI:
    def __init__(self):
        self.plugin_manager = pluggy.PluginManager("together")
        self.plugin_manager.add_hookspecs(TogetherSpec)
        self.register_plugins()

        # configuration starts at default (which usually means empty dict), but
        # may be populated by plugins
        self.config = self.get_default_config()
        self.plugin_manager.hook.together_configure(config=self.config)

        # other CLI attributes will be populated during the build
        self.root_command = None
        self.subcommands = None
        self.all_subcommands = None

    def register_plugins(self):
        """
        By default, `together` loads plugins from entry points under the
        'together' group in setuptools entrypoints. However, you can
        subclass TogetherCLI and override this method in order to provide
        custom plugin loading for your CLI.

        For example, replace with

        >>> def register_plugins(self):
        >>>     self.plugin_manager.load_setuptools_entrypoints("mygroup")

        to load plugins under the entrypoint group "mygroup".
        """
        self.plugin_manager.load_setuptools_entrypoints("together")

    def get_default_config(self):
        """The default configuration object. Override to provide a custom config
        object."""
        return {}

    def define_state_object_at_root(self):
        """
        This method is called immediately after the root command is registered.

        `together` will decorate the root command callback to ensure that there is a
        `together.CommandState` object attached at the root context. The command state
        object will carry a reference to the config object.
        """
        if "obj" in self.root_command.context_settings:
            warnings.warn(
                "root_command used obj in context_settings "
                "it will be overwritten by "
                "TogetherCLI.define_state_object_at_root"
            )
        self.reload_command_state_object()

    def reload_command_state_object(self):
        """reload hook for the command state; tests can use this to reset to a
        fresh object (but with the same config"""
        self.root_command.context_settings["obj"] = CommandState(config=self.config)

    def build(self):
        self.root_command = self.plugin_manager.hook.together_root_command(
            config=self.config
        )
        if not isinstance(self.root_command, click.MultiCommand):
            raise TypeError(
                f"Cannot register a non-MultiCommand root: {self.root_command}"
            )
        self.define_state_object_at_root()

        # plugins will fire in LIFO order (part of the pluggy specification),
        # but we want to register subcommands in FIFO order
        # therefore, reverse the order of the subcommands for registration
        self.subcommands = reversed(
            self.plugin_manager.hook.together_subcommand(config=self.config)
        )

        # conversion produces lists of commands; flatten that out
        self.all_subcommands = [
            c for x in self.subcommands for c in SubcommandRegistration.convert(x)
        ]

        for registration in self.all_subcommands:
            cmd, path = registration.command, registration.path

            # traverse the path to find the parent command
            if not path:
                parent = self.root_command
            else:
                parent = traverse_click(self.root_command, path)

            parent.add_command(cmd)

        return self.root_command
