import click

from together import TogetherCLI, get_verbosity, hook, verbose_option


class BasePlugin:
    @hook
    def together_root_command(self, config):
        @click.group("mycli")
        @verbose_option
        def mycli():
            pass

        return mycli


class FooPlugin:
    @hook
    def together_subcommand(self, config):
        @click.command("foo")
        @verbose_option
        def foo():
            click.echo(f"verbosity={get_verbosity()}")

        return foo


class MyCLI(TogetherCLI):
    def register_plugins(self):
        """override plugin registration, which defaults to using the 'together'
        setuptools entry point, in order to explicitly use these plugins"""
        self.plugin_manager.register(BasePlugin())
        self.plugin_manager.register(FooPlugin())


def test_can_run(run_cmd):
    main = MyCLI().build()
    assert isinstance(main, click.Group)
    result = run_cmd(main, "mycli foo")
    assert result.output == "verbosity=0\n"


def test_verbose_option_on_root(run_cmd):
    cli_instance = MyCLI()
    main = cli_instance.build()
    result = run_cmd(main, "mycli --verbose foo")
    assert result.output == "verbosity=1\n"
    cli_instance.reload_command_state_object()  # reset verbosity
    result = run_cmd(main, "mycli -vvv foo")
    assert result.output == "verbosity=3\n"


def test_verbose_option_mixed(run_cmd):
    main = MyCLI().build()
    result = run_cmd(main, "mycli -v foo -v")
    assert result.output == "verbosity=2\n"
