import click

from together import SubcommandRegistration, TogetherCLI, hook


class BasePlugin:
    @hook
    def together_root_command(self, config):
        @click.group("mycli")
        def mycli():
            click.echo("hi")

        return mycli


class FooPlugin:
    @hook
    def together_subcommand(self, config):
        @click.command("foo")
        def foo():
            click.echo("in foo")

        return SubcommandRegistration(foo, path=["mycli"])


class BarPlugin:
    @hook
    def together_subcommand(self, config):
        @click.group("bar")
        def bar():
            click.echo("in bar")

        return SubcommandRegistration(bar, path=["mycli"])


class BazPlugin:
    @hook
    def together_subcommand(self, config):
        @click.command("baz")
        def baz():
            click.echo("in baz")

        return SubcommandRegistration(baz, path=["mycli", "bar"])


class MyCLI(TogetherCLI):
    def register_plugins(self):
        self.plugin_manager.register(BasePlugin())
        self.plugin_manager.register(FooPlugin())
        self.plugin_manager.register(BarPlugin())
        self.plugin_manager.register(BazPlugin())


runme = MyCLI().build()
runme()
