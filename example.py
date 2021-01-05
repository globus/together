import click

from together import SubcommandRegistration, TogetherCLI, hook


class BasePlugin:
    @hook
    def register_root_command(self):
        @click.group("mycli")
        def mycli():
            click.echo("hi")

        return mycli


class FooPlugin:
    @hook
    def register_subcommand(self):
        @click.command("foo")
        def foo():
            click.echo("in foo")

        return SubcommandRegistration(foo, path=["mycli"])


class BarPlugin:
    @hook
    def register_subcommand(self):
        @click.group("bar")
        def bar():
            click.echo("in bar")

        return SubcommandRegistration(bar, path=["mycli"])


class BazPlugin:
    @hook
    def register_subcommand(self):
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
