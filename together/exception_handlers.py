def _validate_handler(handlerval):
    if not isinstance(handlerval, tuple):
        raise TypeError(
            f"exception_handler registrations must be tuples, got bad val: {handlerval}"
        )
    if len(handlerval) not in (2, 3):
        raise ValueError(
            "exception_handler registrations must of length 2 or 3, "
            f"got bad val: {handlerval}"
        )
    predicate, callback = handlerval[0], handlerval[1]
    if not (
        (isinstance(predicate, type) and issubclass(predicate, Exception))
        or callable(predicate)
    ):
        raise TypeError(
            "exception_handler must have an Exception subclass or callable as the "
            f"first component. got bad predicate: {predicate}"
        )
    if not callable(callback):
        raise TypeError(
            "exception_handler must have a callable as the second component. "
            f"got bad callback: {callback}"
        )
    if len(handlerval) == 3:
        priority = handlerval[2]
        if not isinstance(priority, int):
            raise TypeError(
                "exception_handler priority must be an int if provided. "
                f"got bad priority: {priority}"
            )


def _flatten_lists(xs):
    # expand lists to their elements, and non-list elements are preserved
    # so [[1,2],[3,4],5,6] -> [1,2,3,4,5,6]
    return [y for x in xs for y in (x if isinstance(x, list) else [x])]


class ExceptionHandlerCollection:
    def __init__(self, handlers_raw):
        handlers_raw = _flatten_lists(handlers_raw)
        # validate all
        for x in handlers_raw:
            _validate_handler(x)
        # expand to include priority=0 for any missing it
        with_priorities = [x if len(x) == 3 else (*x, 0) for x in handlers_raw]
        # descending sort by the priority
        self.by_priority = sorted(with_priorities, key=lambda x: x[2], reverse=True)

    def find_callback(self, exception):
        for predicate, callback, _priority in self.by_priority:
            if isinstance(predicate, type):
                if isinstance(exception, predicate):
                    return callback
            elif predicate(exception):
                return callback
        return None
