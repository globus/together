"""
The pluggy hookspec for TogetherCLI plugins
"""
import pluggy

spec_marker = pluggy.HookspecMarker("together")


class TogetherSpec:
    """hook specification for `together`"""

    @spec_marker(firstresult=True)
    def register_root_command(self):
        """
        Register the root command by returning a click.MultiCommand
        Only the first hook result is used.
        """

    @spec_marker
    def register_subcommand(self):
        """
        Register a subcommand by returning a SubommandRegistration.
        """

    @spec_marker
    def register_subcommand_collection(self):
        """
        Register a subcommand by returning an iterable collection of
        SubommandRegistration objects, to allow a single plugin to register
        multiple commands.
        """
