# together

Build CLIs which `click` `together` using `pluggy`.

> **WARNING**: Experimental. This module is an initial proof of concept and
> may change significantly.

## Usage

Define a TogetherCLI by registering plugins which register either click.Group
or click.Command objects. Then, build and invoke the CLI. See `examples/` for
complete examples of standalone and multi-package usage.

### Minimal Usage

Possibly the smallest usage example possible defines a single command with a
single subcommand in one file. Each plugin is implemented as a class (though
implementing plugins as modules is also supported).

```python
# in mycli.py
import together


class BasePlugin:
    @together.hook
    def together_root_command(self, config):
        @click.group("mycli")
        def mycli():
            pass

        return mycli


class FooPlugin:
    @together.hook
    def together_subcommand(self, config):
        @click.command("foo")
        def foo():
            click.echo("running foo")

        return foo


class MyCLI(together.TogetherCLI):
    # customize plugin loading to specify these plugins
    def register_plugins(self):
        self.plugin_manager.register(BasePlugin())
        self.plugin_manager.register(FooPlugin())


# build the CLI
runme = MyCLI()
# run it
runme()
```

This would allow usage like `python mycli.py foo`.

### Changing Plugin Loading

By default, plugins are loaded by looking up the `together` setuptools
entrypoint. To define custom plugin loading, override the
`TogetherCLI.register_plugins` method in a subclass.

For example, you could load a mix of explicit plugins and setuptools
entrypoints with a custom name like so:

```python
import mypackage.plugins

class MyCLI(together.TogetherCLI):
    def register_plugins(self):
        # self.plugin_manager is a pluggy.PluginManager instance
        self.plugin_manager.register(mypackage.plugins.Foo)
        self.plugin_manager.register(mypackage.plugins.Bar)
        self.plugin_manager.load_setuptools_entrypoints("mypackage")
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

### 0.5.1

* Convert from `poetry` to simple `setup.cfg` data

### 0.5.0

* Add the `together_exception_handler` hook for registering exception handlers
  which can be matched against errors when invoking the CLI app

 * Exception handlers combine exception matching functions (predicates),
   exception handling callbacks, and optional priority levels (to ensure early
   or late matching)

 * Predicates may be boolean functions or exception classes, which will be
   checked with `isinstance`

* You can (and should) now invoke a TogetherCLI by calling it, not relying upon
    the `build()` function output

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
