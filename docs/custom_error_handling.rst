Automated Error Handling
========================

For many companies it make a lot of sense to have a centralized solution
for handling errors in production, like
`sentry <https://github.com/getsentry/sentry>`__ or
`squash <http://squash.io>`__.

Thumbor must support this type of error handling in order to better
integrate itself to it's users environments.

Enabling Custom Error Handling
------------------------------

Enabling it is as simple as setting the configuration
``USE_CUSTOM_ERROR_HANDLING`` to ``True``.

After that you need to set the custom error handler you want to use with
the ``ERROR_HANDLER_MODULE`` configuration. Please note that this is the
module full name, not the class full name.

Thumbor comes pre-packaged with sentry's custom error handler:
``thumbor.error_handlers.sentry``. If you decide to use it, please read
below on how to configure it.

Sentry - thumbor.error\_handlers.sentry
---------------------------------------

If you choose to use sentry custom error handler, all you need to do is
fill the ``SENTRY_DSN_URL`` configuration with sentry's DSN URL, which
can be found in the admin page for your sentry project, like the one in
the image below:

.. image:: images/thumbor-sentry-get-dsn.png
    :alt: In Sentry, go to your project admin page, click Python.
