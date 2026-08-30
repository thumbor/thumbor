# Custom Error Handlers

A custom error-handler module must expose a class named `ErrorHandler`.
Thumbor constructs the class once at startup and passes the loaded configuration
to its constructor. `handle_error` is synchronous and is called with the current
request context, the Tornado request handler, and exception information.

```python
import logging


logger = logging.getLogger(__name__)


class ErrorHandler:
    def __init__(self, config):
        self.config = config

    def handle_error(self, context, handler, exception):
        # Thumbor normally passes the tuple returned by sys.exc_info().
        if isinstance(exception, tuple):
            exc_info = exception
        else:
            exc_info = (
                type(exception),
                exception,
                exception.__traceback__,
            )

        logger.error(
            "Error while handling %s",
            handler.request.uri,
            exc_info=exc_info,
        )
```

`context` is thumbor's context for the current request, `handler` is the
Tornado request handler, and `exception` is normally the
`(type, value, traceback)` tuple returned by `sys.exc_info()`. The method is not
awaited, so it must be a regular synchronous method.

Configure the module name, not the class name, and make sure it is importable
from thumbor's Python environment:

```python
USE_CUSTOM_ERROR_HANDLING = True
ERROR_HANDLER_MODULE = "mylib.error_handling"
```
