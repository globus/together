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
# in together-sample/setup.py
from setuptools import setup, find_packages

setup(
    name="together-sample",
    install_requires="together",
    entry_points={"together": ["root = main"]},
    py_modules=["main"]
)
```

Then define the `together_sample` module to provide a root command and one
subcommand.

```python
# in together-sample/main.py
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
# in together-subsample/setup.py
from setuptools import setup, find_packages

setup(
    name="together-subsample",
    install_requires="together",
    entry_points={"together": ["subsample = main"]},
    py_modules=["main"]
)
```

and the plugin itself, which registers multiple commands using the
`together_subcommand` hook returning a list of commands:

```python
# in together-subsample/main.py
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

Now, with both `together-sample` and `together-subsample` installed
(e.g. `pip install -e ./together-sample/; pip install -e ./together-subsample/`)
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

### Using CommandState

`together` automatically defines a class, `together.CommandState` which
implements stateful tracking of option data as it is parsed. This allows the
value which was passed to a parent command or the root command to be recorded
on the click context and accessed by child command callbacks.

For example, if you wish to support arguments like `--format=[json|text]` in
your commands, and allow usage like `mycli --format=json foo` to be valid, you
need to save and retrieve that option. `CommandState` implements this logic and
is automatically registered as the context object for commands.

To implement such an option, define a click decorator which uses a callback to
get the state object and use it for storage. You can also write an easy getter
function to get back the stored value. Like so:

```python
import click
from together import get_state

def format_option(f):
    def callback(ctx, param, value):
        state = get_state()
        state.set("format", value)
    return click.option(
        "--format", type=click.Choice(["json", "text"]), callback=callback
    )(f)


def get_format():
    return get_state().get("format")
```

> **NOTE**: `get_state()` requires that there is an active Click Context
> it therefore can only normally execute inside of running Click commands

#### Using CommandState to access Config

The configuration object produced by your `together_configure` hooks is
attached to the CommandState for easy access. All you need to do is get the
state object and look at its `config` attribute:

```python
def was_configured_to_foobar():
    state = get_state()
    return state.config.get("foobar") is True
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

### 0.4.0

* Add the CommandState object supporting arbitrary storage (in an inner dict)
  and the `get_state` helper

* Add `verbose_option` and `get_verbosity` built on the CommandState object

This can be used to implement the common pattern of defining a single central
object which is pulled off of the click context to record options which might
be valid at multiple levels of a command heirarchy.

### 0.3.1

* Bugfix: incorrectly unpacking subcommand lists

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
