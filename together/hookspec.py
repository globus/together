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

    @spec_marker
    def together_exception_handler(self, config):
        """
        Register an additional exception handler by returning a 3-tuple of the
        form ``(predicate, callback, priority_level)`` or a 2-tuple of the form
        ``(predicate, callback)``.

        ``predicate`` must be either (1) an Exception subclass against which the
        hook will match and run or (2) a callable which accepts an exception
        object and returns `True` if the hook should be run

        ``priority_level`` is an integer. Higher priority hooks are evaluated
        before lower priority hooks. The default (when not provided) is 0.

        ``callback`` is the function to invoke when the exception is handled.
        It should return an integer, which will be used as the application exit
        code.

        If you wish to register multiple handlers, return a list of such
        values instead.
        """
