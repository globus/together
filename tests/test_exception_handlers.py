import click

from together import TogetherCLI, hook


def valueerror_handler(exception):
    msg = exception.args[0] if len(exception.args) == 1 else exception.args
    click.echo(f"Bad value: {msg}", err=True)
    return 3


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

    @hook
    def together_exception_handler(self, config):
        return (ValueError, valueerror_handler)


class BarPlugin:
    @hook
    def together_subcommand(self, config):
        @click.command("bar")
        def bar():
            click.echo("in bar")
            raise ValueError("in bar")

        return bar


class MyCLI(TogetherCLI):
    def register_plugins(self):
        """override plugin registration, which defaults to using the 'together'
        setuptools entry point, in order to explicitly use these plugins"""
        self.plugin_manager.register(BasePlugin())
        self.plugin_manager.register(FooPlugin())
        self.plugin_manager.register(BarPlugin())


def test_can_build():
    cli = MyCLI()
    assert isinstance(cli.build(), click.Group)


def test_invoke_no_handler(run_cmd):
    main = MyCLI()
    result = run_cmd(main, "mycli")
    assert result.output == "hi\n"


def test_invoke_handler(run_cmd):
    main = MyCLI()
    result = run_cmd(main, "mycli bar", assert_exit_code=3)
    assert result.stderr == "Bad value: in bar\n"
