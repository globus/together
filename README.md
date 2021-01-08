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

@together.hook
def together_root_command(config):
    @click.group("sample")
    def sample():
        click.echo("at root")
    return sample

@together.hook
def together_subcommand(config):
    # NOTE: 'foo' is a group, which is important for attaching subcommands to
    # it later
    @click.group("foo")
    def foo():
        click.echo("foo")

    return foo
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
`together_subcommand` hook returning a list of commands:

```python
# in together_subsample.py
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
        # when providing group registrations to `together`, we only need to provide the root
        # of a group we want to include
        spam
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
3. Only the last plugin to register a root command will execute. You should
   only register one root command.

For the most part, this will make the plugin subcommand registration operate in
FIFO order.

## CHANGELOG

### 0.3.0

* Replace `together_subcommand_collection` with support in the
  `together_subcommand` hook for lists of subcommands

### 0.2.1

* Allow hooks to return command registration info without explicitly wrapping
  it in a registration object

### 0.2.0

* Change hook names and support config

### 0.1.0

* Initial release
