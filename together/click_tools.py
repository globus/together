import click


def _recursive_traverse_click(cur, path, parent_ctx=None):
    if not path:
        return cur

    name = path[0]
    with click.Context(cur, info_name=name, parent=parent_ctx) as ctx:
        nextcmd = cur.get_command(ctx, name)
        return _recursive_traverse_click(nextcmd, path[1:], parent_ctx=ctx)


def traverse_click(root_cmd, path):
    if path[0] != root_cmd.name:
        raise ValueError(
            f"expected name for root to be {root_cmd.name}, "
            f"but path started with {path[0]}"
        )
    return _recursive_traverse_click(root_cmd, path[1:])
