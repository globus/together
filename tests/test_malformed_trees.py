import click
import pytest

from together import TogetherCLI, hook


def test_non_group_root_is_type_error():
    class BasePlugin:
        @hook
        def together_root_command(self, config):
            @click.command("mycli")
            def mycli():
                click.echo("hi")

            return mycli

    class MyCLI(TogetherCLI):
        def register_plugins(self):
            self.plugin_manager.register(BasePlugin())

    with pytest.raises(TypeError) as excinfo:
        MyCLI().build()

    assert "Cannot register a non-MultiCommand root" in str(excinfo.value)
