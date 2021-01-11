import warnings

import click


class CommandState:
    """
    A CommandState object is intended to be the main Click object defined via
    `Context.ensure_object` and similar methods. It can be used as a general
    parameter store so that certain options -- e.g. verbosity, output formats
    -- can be defined once, exposed at multiple levels of a command tree, and
    still have their resulting values exposed to the ultimate command which
    runs.

    By default, the CommandState only defines `CommandState.verbosity` and the
    `CommandState.verbose_option` decorator. You may subclass this object to
    allow further parametrization.

    Primarily, the CommandState allows easy access to the config object which
    may have been written by plugins. It also allows dict storage of command
    values.
    """

    def __init__(self, *, config=None):
        self.data = {}
        self.config = config

    def set(self, optname, value):
        self.data[optname] = value

    def get(self, optname, default=None):
        return self.data.get(optname, default)


def get_state():
    """
    This function just pulls the current Click context object, like
    click.pass_obj

    Since in a normally defined `together` CLI this will be a CommandState
    object, it is called get_state
    """
    return click.get_current_context().obj


def get_verbosity():
    """get the verbosity value set via verbose_option"""
    state = get_state()
    return state.get("verbosity", 0)


def verbose_option(f):
    def callback(ctx, param, value):
        state = get_state()
        if not state:
            warnings.warn(
                "verbose_option was used, but no state object was found. "
                "you have probably modified the root state object incorrectly "
                "or you should not use verbose_option. verbose flag will be "
                "ignored."
            )
            return

        current_value = state.get("verbosity", 0)
        # set state verbosity value from option, allow it to be added up if
        # counted at multiple parts of a command heirarchy (multiple
        # callback invocations)
        state.set("verbosity", current_value + value)

    return click.option(
        "-v",
        "--verbose",
        count=True,
        expose_value=False,
        callback=callback,
        is_eager=True,
        help="Control level of output",
    )(f)
