# together

Build CLIs which `click` `together` using `pluggy`.

> **WARNING**: Experimental. This module is an initial proof of concept and
> may change significantly.

## Usage

Define a TogetherCLI by registering plugins which register either click.Group
or click.Command objects. Then, build and invoke the CLI. See `example.py` for
a complete standalone example.

Basic usage follows.

Define a package which provides your hook implementation as a setuptools
entrypoint named `"together"`:

```python
# in setup.py
from setuptools import setup, find_packages

setup(
    name="together-sample",
    install_requires="together",
    entry_points={"together": ["root = together_sample"]},
    py_modules=["together_sample"]
)
```

Then define the `together_sample` module to provide a root command and one
subcommand.

```python
# in together_sample.py
import click
import together

@click.group("sample")
def sample():
    click.echo("at root")

@together.hook
def register_root_command():
    return sample

@together.hook
def register_subcommand():
    # NOTE: 'foo' is a group, which is important for attaching subcommands to
    # it later
    @click.group("foo")
    def foo():
        click.echo("foo")

    return together.SubcommandRegistration(foo)
```

Multiple other plugins can provide subcommands for `sample`. Create
`together-subsample` in another directory:

```python
# in setup.py
from setuptools import setup, find_packages

setup(
    name="together-subsample",
    install_requires="together",
    entry_points={"together": ["subsample = together_subsample"]},
    py_modules=["together_subsample"]
)
```

and the plugin itself, which registers multiple commands using the
`register_subcommand_collection` hook:

```python
# in together_subsample.py
import click
import together


@together.hook
def register_subcommand_collection():
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
        together.SubcommandRegistration(bar, ['sample', 'foo']),
        # when providing group registrations to `together`, we only need to provide the root
        # of a group we want to include
        together.SubcommandRegistration(spam)
    ]
```

Now, with both `together_sample` and `together_subsample` installed
(e.g. `pip install -e ./together_sample/; pip install -e ./together_subsample/`)
we can invoke the resulting CLI by building and running:

```python
# sample.py
import together

runme = together.TogetherCLI().build()
runme()
```

And we should then be able to run

```bash
python sample.py foo
python sample.py foo bar
python sample.py fruit banana
```

## Plugin Order and Execution

Several rules govern how plugins execute and their ordering.

1. Plugins are `pluggy` plugins and hooks _execute_ in LIFO order
2. `together` reverses the order of the resulting registrations to produce FIFO ordering
3. All `register_subcommand` registrations are added to the CLI before
   `register_subcommand_collection` registrations are added
4. Only the last plugin to register a root command will execute. You should
   only register one root command.

> **NOTE**: register_subcommand_collection hooks do not have their contents
> reversed. Rather, if there are two subcommand collections registered in
> pluginA and pluginB, with pluginA registered before pluginB, then the
> following will happen:
> 1. pluginB was the last registered plugin, so its
>    register_subcommand_collection hook runs
> 2. pluginA was the first registered plugin, so its
>    register_subcommand_collection hook runs next
> 3. pluginB results are appended to pluginA results (so A's registrations will
>    take effect first!)

For the most part, this will make the plugin subcommand registration operate in
FIFO order. However, if your plugin attempts to inspect the status of the
current CLI object, you must be aware of the execution order.
