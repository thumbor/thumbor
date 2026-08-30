# Custom Handler Lists

Handler Lists are responsible for adding new handlers to thumbor.

Even thumbor's own handlers (other than the default image crop handler) are
added using handler lists(healthcheck, blacklist...).

## Built-in Handler Lists

Thumbor comes with three handler lists built-in:

- `thumbor.handler_lists.healthcheck`;
- `thumbor.handler_lists.upload`;
- `thumbor.handler_lists.blacklist`.

The healthcheck handler list adds a handler at whatever is in the
`HEALTHCHECK_ROUTE` config.

The blacklist handler list adds a `/blacklist` handler that can be used to
blacklist images.

The upload handler list adds two handlers for uploading and retrieving uploaded
images.

## Writing a new Handler List

A handler list is an importable Python module with a synchronous
`get_handlers(context)` function. The function receives thumbor's application
context and returns a list of Tornado handler specifications.

The third item in a handler specification is passed to the handler's
`initialize` method. Handlers that inherit from `ContextHandler` should receive
thumbor's context using `{"context": context}`.

```python
from typing import Any

from thumbor.handler_lists import HandlerList
from thumbor.handlers import ContextHandler


class IndexHandler(ContextHandler):
    async def get(self):
        self.write("Hello from my handler")


def get_handlers(context: Any) -> HandlerList:
    if not context.config.get("SOMETHING_ENABLED", False):
        return []

    return [
        (r"/my-url/?", IndexHandler, {"context": context}),
    ]
```

After your handler list can be imported with python (check with
`python -c 'import <<your handler list module>>'`), just add it to thumbor's
config:

```python
from thumbor.handler_lists import BUILTIN_HANDLERS

# Two things worth noticing here:
# 1) Handler list order indicates precedence. The first match is executed.
# 2) Include thumbor's built-ins to preserve thumbor functionality.
HANDLER_LISTS = BUILTIN_HANDLERS + [
    "my.handler_list",
]
```

Handler lists are evaluated in configuration order, and the first matching
route is used. The built-in imaging route is appended after every configured
handler list. Keep `BUILTIN_HANDLERS` unless you intentionally want to remove
thumbor's healthcheck, upload, and blacklist routes.
