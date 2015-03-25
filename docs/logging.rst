Logging
=======

thumbor uses the built-in Python logging mechanisms. In order to
configure log-level check the :doc:`running` page.

Configuring log format
----------------------

Configuring the log format is as easy as including these keys in your
``thumbor.conf`` file:

THUMBOR\_LOG\_FORMAT
~~~~~~~~~~~~~~~~~~~~

Log Format to be used by thumbor when writing log messages.

*Defaults to*: %(asctime)s %(name)s:%(levelname)s %(message)s

THUMBOR\_LOG\_DATE\_FORMAT
~~~~~~~~~~~~~~~~~~~~~~~~~~

Date Format to be used by thumbor when writing log messages.

*Defaults to*: %Y-%m-%d %H:%M:%S
