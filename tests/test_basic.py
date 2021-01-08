import click

from together import TogetherCLI, hook


class BasePlugin:
    @hook
    def together_root_command(self, config):
        @click.group("mycli", invoke_without_command=True)
        def mycli():
            click.echo("hi")

        return mycli


class FooPlugin:
    @hook
    def together_subcommand(self, config):
        @click.command("foo")
        def foo():
            click.echo("in foo")

        return foo


class BarPlugin:
    @hook
    def together_subcommand(self, config):
        @click.group("bar")
        def bar():
            click.echo("in bar")

        return bar


class BazPlugin:
    @hook
    def together_subcommand(self, config):
        @click.command("baz")
        def baz():
            click.echo("in baz")

        return (baz, ["mycli", "bar"])


class MyCLI(TogetherCLI):
    def register_plugins(self):
        """override plugin registration, which defaults to using the 'together'
        setuptools entry point, in order to explicitly use these plugins"""
        self.plugin_manager.register(BasePlugin())
        self.plugin_manager.register(FooPlugin())
        self.plugin_manager.register(BarPlugin())
        self.plugin_manager.register(BazPlugin())


def test_can_build():
    main = MyCLI().build()
    assert isinstance(main, click.Group)


def test_invoke_root(run_cmd):
    main = MyCLI().build()
    result = run_cmd(main, "mycli")
    assert result.output == "hi\n"
