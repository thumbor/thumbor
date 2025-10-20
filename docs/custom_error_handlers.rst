Custom Error Handlers
=====================

Thumbor allows you to implement custom error handling to integrate with external
monitoring services, customize error responses, or implement custom logging strategies.

Basic Implementation
--------------------

Writing your own error handler is very simple. Just create a class
called ``ErrorHandler``, like the one below:

.. code-block:: python

    # Class that lives in mylib.error_handling
    class ErrorHandler:
        def __init__(self, config):
            # perform any initialization needed
            # config is the thumbor configuration object
            pass

        def handle_error(self, context, handler, exception):
            # do your thing here
            # context is thumbor's context for the current request
            # handler is tornado's request handler for the current request
            # exception is the error that occurred
            pass

When you have your handler done, just put it's full name in thumbor.conf
and make sure thumbor can import it (it's somewhere in PYTHONPATH).
You also need to set ``USE_CUSTOM_ERROR_HANDLING`` to ``True``.

.. code:: python

   USE_CUSTOM_ERROR_HANDLING = True
   ERROR_HANDLER_MODULE = 'mylib.error_handling'

Practical Examples
------------------

Example 1: Logging to External Service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example shows how to send errors to an external logging service:

.. code-block:: python

    import requests
    from thumbor.utils import logger

    class ErrorHandler:
        def __init__(self, config):
            self.webhook_url = config.get('ERROR_WEBHOOK_URL', None)
            self.environment = config.get('ENVIRONMENT', 'production')

        def handle_error(self, context, handler, exception):
            logger.error(f"Error processing request: {exception}")

            if self.webhook_url:
                payload = {
                    'environment': self.environment,
                    'error_type': type(exception).__name__,
                    'error_message': str(exception),
                    'request_path': handler.request.path,
                    'request_method': handler.request.method,
                }

                try:
                    requests.post(self.webhook_url, json=payload, timeout=5)
                except Exception as e:
                    logger.warning(f"Failed to send error to webhook: {e}")

Example 2: Sentry Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integrate with Sentry for comprehensive error tracking:

.. code-block:: python

    import sentry_sdk
    from thumbor.utils import logger

    class ErrorHandler:
        def __init__(self, config):
            sentry_dsn = config.get('SENTRY_DSN', None)
            if sentry_dsn:
                sentry_sdk.init(
                    dsn=sentry_dsn,
                    environment=config.get('SENTRY_ENVIRONMENT', 'production'),
                    traces_sample_rate=config.get('SENTRY_TRACES_SAMPLE_RATE', 0.1),
                )
            self.sentry_enabled = bool(sentry_dsn)

        def handle_error(self, context, handler, exception):
            logger.error(f"Error in thumbor: {exception}")

            if self.sentry_enabled:
                with sentry_sdk.push_scope() as scope:
                    # Add context information
                    scope.set_tag("request_path", handler.request.path)
                    scope.set_tag("request_method", handler.request.method)
                    scope.set_context("request", {
                        "url": handler.request.full_url(),
                        "headers": dict(handler.request.headers),
                    })

                    # Capture the exception
                    sentry_sdk.capture_exception(exception)

Example 3: Custom Error Response
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Customize the error response sent to clients:

.. code-block:: python

    import json
    from thumbor.utils import logger

    class ErrorHandler:
        def __init__(self, config):
            self.debug_mode = config.get('DEBUG', False)

        def handle_error(self, context, handler, exception):
            logger.error(f"Request failed: {exception}")

            # Set appropriate HTTP status code
            status_code = getattr(exception, 'status_code', 500)
            handler.set_status(status_code)

            # Build error response
            error_response = {
                'error': True,
                'message': 'An error occurred processing your image',
            }

            # Include details in debug mode
            if self.debug_mode:
                error_response['details'] = {
                    'type': type(exception).__name__,
                    'message': str(exception),
                    'path': handler.request.path,
                }

            handler.set_header('Content-Type', 'application/json')
            handler.write(json.dumps(error_response))
            handler.finish()

Example 4: Metrics and Monitoring
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Track error rates and types for monitoring:

.. code-block:: python

    from thumbor.utils import logger

    class ErrorHandler:
        def __init__(self, config):
            self.statsd_client = None

            # Initialize StatsD if configured
            statsd_host = config.get('STATSD_HOST', None)
            if statsd_host:
                import statsd
                self.statsd_client = statsd.StatsClient(
                    host=statsd_host,
                    port=config.get('STATSD_PORT', 8125),
                    prefix='thumbor.errors'
                )

        def handle_error(self, context, handler, exception):
            error_type = type(exception).__name__
            logger.error(f"Error {error_type}: {exception}")

            # Increment error counter
            if self.statsd_client:
                self.statsd_client.incr(f'{error_type}')
                self.statsd_client.incr('total')

Common Error Types
------------------

When implementing error handlers, you may encounter these common exception types:

* ``IOError``: File I/O errors, image loading failures
* ``RuntimeError``: General runtime errors, image processing failures
* ``ValueError``: Invalid parameter values
* ``tornado.web.HTTPError``: HTTP-specific errors with status codes
* ``LoaderError``: Errors loading images from remote sources
* ``StorageError``: Errors reading/writing to storage backends

Error Propagation
-----------------

Thumbor's error handling follows this flow:

1. An exception occurs during image processing
2. If ``USE_CUSTOM_ERROR_HANDLING`` is ``True``, your custom handler is called
3. Your handler can log, report, or transform the error
4. If your handler doesn't finish the response, Thumbor's default error handling continues
5. An error response is sent to the client

Best Practices
--------------

1. **Don't suppress errors silently**: Always log errors even if you handle them
2. **Handle your handler's errors**: Wrap external service calls in try-except blocks
3. **Set appropriate timeouts**: Don't let error reporting slow down error responses
4. **Include context**: Add request details to help debug issues
5. **Test error scenarios**: Verify your handler works with different exception types
6. **Finish responses**: Call ``handler.finish()`` if you write custom responses

Troubleshooting
---------------

**Handler not being called**
    Verify ``USE_CUSTOM_ERROR_HANDLING = True`` in your config

**Import errors**
    Ensure your module is in PYTHONPATH or installed via pip

**Handler called but errors still appear**
    Your handler should either finish the response or let Thumbor's default handling continue

**Performance issues**
    Use timeouts for external service calls and consider async operations

Configuration Reference
-----------------------

Related configuration options:

.. code-block:: python

    # Enable custom error handling
    USE_CUSTOM_ERROR_HANDLING = True

    # Path to your error handler module
    ERROR_HANDLER_MODULE = 'mylib.error_handling'

    # Example custom configuration for your handler
    SENTRY_DSN = 'https://your-sentry-dsn'
    ERROR_WEBHOOK_URL = 'https://your-webhook-endpoint'
