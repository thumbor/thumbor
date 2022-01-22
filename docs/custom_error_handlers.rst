Custom Error Handlers
=====================

Writing your own error handler is very simple. Just create a class
called ``ErrorHandler``, like the one below:

.. code-block:: python

    # Class that lives in mylib.error_handling
    class ErrorHandler:
        def __init__(self, config):
            # perform any initialization needed
            pass

        def handle_error(self, context, handler, exception):
            # do your thing here
            # context is thumbor's context for the current request
            # handler is tornado's request handler for the current request
            # exception is the error that occurred

When you have your handler done, just put it's full name in thumbor.conf
and make sure thumbor can import it (it's somewhere in PYTHONPATH).
You also need to set ``USE_CUSTOM_ERROR_HANDLING`` to ``True``.

.. code:: python

   USE_CUSTOM_ERROR_HANDLING = True
   ERROR_HANDLER_MODULE = 'mylib.error_handling'
