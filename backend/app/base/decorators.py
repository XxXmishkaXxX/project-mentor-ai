from functools import wraps
from typing import Any, Callable


def with_transaction(method: Callable) -> Callable:
    """Run a manager method inside a shared DB transaction.

    When two or more write operations must be atomic, decorate the
    manager method with ``@with_transaction``.  All ``PgAccessor``
    calls inside will share one session and commit/rollback together.
    """

    @wraps(method)
    async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        async with self.store.pg.begin():
            return await method(self, *args, **kwargs)

    return wrapper
