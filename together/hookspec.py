"""
The pluggy hookspec for TogetherCLI plugins
"""
import pluggy

spec_marker = pluggy.HookspecMarker("together")


class TogetherSpec:
    """hook specification for `together`"""

    @spec_marker(firstresult=True)
    def together_root_command(self, config):
        """
        Register the root command by returning a click.MultiCommand
        Only the first hook result is used.
        """

    @spec_marker
    def together_subcommand(self, config):
        """
        Register a subcommand by returning one of
        - a SubcommandRegistration
        - a click command (or group)
        - a 2-tuple of a click command and its path in the command tree

        You may also return a list of any of the above to register multiple
        commands.
        """

    @spec_marker
    def together_configure(self, config):
        """
        Add or modify data in the existing configuration object.
        """
