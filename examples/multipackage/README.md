# Multipackage Example

This example defines multiple distinct packages which provide `together`
entrypoints, along with a TogetherCLI instance which loads the plugins via
these entrypoints (the default behavior) and invokes the result.

The subpackages are in `together-sample/` and `together-subsample/` and the
TogetherCLI which joins them is `main.py`

In a virtualenv, installing each of the subpackages and `together` results in
the desirable CLI being built and run.

`./install.sh` is a simple example install script. In the resulting virtualenv,
use `python example.py` to see the results.

Once everything is installed, you will be able to run

```bash
python sample.py foo
python sample.py foo bar
python sample.py fruit banana
```

## together-sample

This directory contains a package defining the root command for the resulting
CLI.

`together-sample/main.py` defines the root command for this plugin. See
`together-sample/setup.py` for how it is automatically loaded.

## together-subsample

This directory contains a package defining a subcommand of the resulting CLI.

`together-subsample/main.py` defines a subcommand for this plugin. See
`together-subsample/setup.py` for how it is automatically loaded.

## example.py

This file defines a CLI instance and invokes it.
It will load plugins from the `together` entry points and build the CLI from
this data.
