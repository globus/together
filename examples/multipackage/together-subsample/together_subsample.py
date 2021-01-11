import click
import together


@together.hook
def together_subcommand(config):
    @click.command("bar")
    def bar():
        click.echo("bar")

    @click.group("fruit")
    def spam():
        click.echo("fruit")

    # we can still attach subcommands using normal click mechanisms
    @spam.command("banana")
    def banana():
        click.echo("banana")

    return [
        # for `bar` to be a subcommand of `foo`, and not the root, we must
        # provide its path within the application
        (bar, ['sample', 'foo']),
        # when providing group registrations to `together`, we only need to provide the
        # root of a group we want to include
        spam
    ]
