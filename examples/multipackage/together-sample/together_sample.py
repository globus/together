import click

import together


@together.hook
def together_root_command(config):
    @click.group("sample")
    def sample():
        click.echo("at root")

    # NOTE: 'foo' is a group, which is important for attaching subcommands to
    # it later
    #
    # also, important: `foo` is registered when the root is registered
    # if it were registered in a `together_subcommand` hook instead, we could
    # not guarantee that it would be registered before `together_subsample`
    # hooks run, and therefore could not register `bar` as a subcommand of it
    # reliably
    @sample.group("foo")
    def foo():
        click.echo("foo")

    return sample
