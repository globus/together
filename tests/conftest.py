import shlex

import pytest
from click.testing import CliRunner


@pytest.fixture
def run_cmd():
    def func(cli, line, assert_exit_code=0):
        args = shlex.split(line)
        assert args[0] == cli.name

        result = CliRunner().invoke(
            cli, args[1:], catch_exceptions=bool(assert_exit_code)
        )
        if result.exit_code != assert_exit_code:
            raise Exception(
                f"Failed to run '{line}'.\n"
                f"result.exit_code={result.exit_code} (expected {assert_exit_code})\n"
                f"Output:\n{result.output}"
            )
        return result

    return func
