import shlex

import pytest
from click.testing import CliRunner


# a class to contain a TogetherCLI and make it conform to the interface
# expected by CliRunner.invoke
class CliInterfaceWrapper:
    def __init__(self, real_cli):
        # force build if not done already
        root = real_cli.build()

        self.real_cli = real_cli
        self.name = root.name

    def main(self, *args, **kwargs):
        return self.real_cli(*args, **kwargs)


@pytest.fixture
def run_cmd():
    def func(cli, line, assert_exit_code=0):
        wrapped = CliInterfaceWrapper(cli)

        args = shlex.split(line)
        assert args[0] == wrapped.name

        result = CliRunner(mix_stderr=False).invoke(
            wrapped, args[1:], catch_exceptions=bool(assert_exit_code)
        )
        if result.exit_code != assert_exit_code:
            raise Exception(
                f"Failed to run '{line}'.\n"
                f"result.exit_code={result.exit_code} (expected {assert_exit_code})\n"
                f"stdout:\n{result.stdout}"
                f"stderr:\n{result.stderr}"
            )
        return result

    return func
