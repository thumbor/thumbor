Running thumbor server
======================

Running thumbor server is as easy as typing "thumbor" (considering you
went through the proper :doc:`installing` procedures).

The Server application takes some parameters that will help you tailor
the thumbor Server to your needs. If you want to find out what the
thumbor Server arguments are, just type:

.. code:: bash

    thumbor --help

-i or --ip
~~~~~~~~~~

The address that Tornado will listen for incoming request. It defaults
to *0.0.0.0* (listening on localhost and current IP).

-p or --port
~~~~~~~~~~~~

The port that Tornado will listen for incoming request. It defaults to
*8888*.

-c or --conf
~~~~~~~~~~~~

The full path for the configuration file for this server.

-k or --keyfile
~~~~~~~~~~~~~~~

The full path for the file containing the security key to be used for
this server.

-l or --log-level
~~~~~~~~~~~~~~~~~

The log level to be used. Possible values are: *debug*, *info*,
*warning*, *error*, *critical* or *notset*. More on that at
http://docs.python.org/library/logging.html. It defaults to
*warning*.

--processes
~~~~~~~~~~~

Number of processes to run. By default equals 1 and means no forks created.
Set to 0 to detect the number of cores available on this machine.
Set > 1 to start that specified number of processes.

-a or --app
~~~~~~~~~~~

Allows the user to specify the application class to be used. This is a
very advanced usage of thumbor. This argument is specified like:
"namespace1.namespace2.class\_name" as in
"myproj.thumbor\_support.MyProjThumborApp".

Signing thumbor urls
--------------------

To help users create signed URLs (mostly for debugging purposes, since
we recommend using the :doc:`libraries`), thumbor comes with an application
called thumbor-url.

In order to use it, type ``thumbor-url -h`` and it will present all
options available.
