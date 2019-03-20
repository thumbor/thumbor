import sentry_sdk
from sentry_sdk.integrations.logging import ignore_logger
from sentry_sdk.utils import event_from_exception, exc_info_from_error

from thumbor import __version__


class ErrorHandler(object):
    def __init__(self, config):
        dsn = config.SENTRY_DSN_URL

        if not dsn:
            raise RuntimeError(
                "If you set USE_CUSTOM_ERROR_HANDLING to True, and you are using thumbor.error_handlers.sentry_python, " +
                "then you must specify the Sentry DSN using the SENTRY_DSN_URL configuration."
            )

        kwargs = {
            'dsn': dsn,
            'integrations': [],
        }

        env = config.get('SENTRY_ENVIRONMENT')
        if env is not None:
            kwargs['environment'] = env

        # Logging integration will create duplicates if below not ignored
        ignore_logger('thumbor')
        ignore_logger('tornado.access')

        sentry_sdk.init(**kwargs)

    def handle_error(self, context, handler, exception):
        req = handler.request

        exc_info = exc_info_from_error(exception)

        with sentry_sdk.push_scope() as scope:
            event, hint = event_from_exception(exc_info)
            event["request"] = {
                "url": req.full_url(),
                "method": req.method,
                "data": req.arguments,
                "query_string": req.query,
                "headers": req.headers,
                "body": req.body,
            }
            scope.set_extra('thumbor-version',  __version__)
            sentry_sdk.capture_event(event, hint=hint)
