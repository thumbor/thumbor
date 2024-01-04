Hosting
=======

Let's see how would you run thumbor in different environments.

Development Environment
-----------------------

For running it locally you just need to get a proper :doc:`configuration`
file. You can put it at ``/etc/thumbor.conf``, ``~/thumbor.conf`` (home folder)
or specify it when starting thumbor.

To verify if you have thumbor, just type:

.. code:: bash

    thumbor --version

It should return the version you've installed. Starting thumbor is as
easy as:

.. code:: bash

    thumbor

For more options check the :doc:`configuration` page.

Production Environment
----------------------

Other than having the proper :doc:`configuration` file for your
environment, we have some recommendations on how to run thumbor in
production.

Our first recommendation is to run more than one instance of it. You can
specify different ports using thumbor easily. This will make sure that
your service stays responsive even if one of the processes die.

We also recommend having some form of load balance that distributes the
load between the aforementioned processes. We are using NGINX to do it,
but there are more sophisticated load balance softwares around. thumbor
supports health checking under the ``/healthcheck`` URI if you need to
use it.

Other than that, you run it using the thumbor console app specifying the
arguments, like this:

.. code:: bash

    thumbor --port=8888 --conf="~/mythumbor.conf"

We recommend using an application such as Supervisor
(http://supervisord.org/index.html) to monitor your services. An
example of a ``supervisord.conf`` file would be:

.. code::

    [supervisord]
    logfile = /home/thumbor/logs/supervisord.log
    logfile_maxbytes = 50MB
    logfile_backups=10
    loglevel = info
    pidfile = /home/thumbor/supervisord.pid
    user = thumbor

    [program:thumbor]
    command=thumbor --port=800%(process_num)s --conf=/etc/thumbor800%(process_num)s.conf
    process_name=thumbor800%(process_num)s
    numprocs=4
    user=thumbor
    directory=/home/thumbor/
    autostart=true
    autorestart=true
    startretries=3
    stopsignal=TERM
    stdout_logfile=/home/thumbor/logs/thumbor800%(process_num)s.stdout.log
    stdout_logfile_maxbytes=1MB
    stdout_logfile_backups=10
    stderr_logfile=/home/thumbor/logs/thumbor800%(process_num)s.stderr.log
    stderr_logfile_maxbytes=1MB
    stderr_logfile_backups=10

This configuration file makes sure that supervisor starts 4 processes of
thumbor on the 8000, 8001, 8002 and 8003 ports, each with a different
configuration file (thumbor8000.conf, thumbor8001.conf,
thumbor8002.conf, thumbor8003.conf all under /etc folder). The other
settings are optional, but if you need help with supervisor's settings
it has extensive documentation online
(http://supervisord.org/introduction.html).

Thumbor in the Cloud
--------------------

Running with Docker
~~~~~~~~~~~~~~~~~~~

Running thumbor with docker is as easy as::

   $ docker run -p 8888:80 ghcr.io/minimalcompact/thumbor:latest
   ...
   $ curl http://localhost:8888/healthcheck
   WORKING%

For more details check the `MinimalCompact thumbor docker image <https://github.com/MinimalCompact/thumbor>`_.

.. TODO::
   update this instructions as they are severely outdated
   Creating your thumbor install in heroku
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   You can deploy and test Thumbor in the cloud. It's quite easy with
   `Heroku <http://www.heroku.com>`__ :

   -  Create an account like described at
      http://devcenter.heroku.com/articles/quickstart
   -  Install the heroku Toolbelt as described in the same page
   -  Log to Heroku in your shell
   -  Create a small git project for the configuration of your Thumbor
      instance.

   The whole script to deploy and start an instance :

   .. code:: bash

       mkdir heroku
       cd heroku/
       echo "thumbor>=2.7.0" >> requirements.txt # let heroku deploy and compile prerequisite package via PIP
       echo "web: thumbor -p $PORT" >> Procfile # listening port is automatically affected at deployment (we use here the default config)
       git init
       git add .
       git commit -m "init"
       heroku create --stack cedar
       git push heroku master

   Basically, adding thumbor in requirements.txt will install everything
   you need on Heroku, and you just need to run thumbor -p $PORT to run
   thumbor on Heroku. In order to run process on Heroku, you need to write
   down the command in Procfile. Procfile looks like following (make sure
   there are no "" inside both files):

   ::

       $ cat Procfile
       web: thumbor -p $PORT

   Your heroku folder (or whatever you named, I named it thumbor) should
   look like following (only contains two files):

   ::

       ~/thumbor(master)$ ls
       Procfile        requirements.txt

   -  Start the instance (Remember: 1 heroku web instance is free of
      charges, so don't try with more yet):

      heroku scale web=1

   -  Verify your new instance is up (in the case of our sample project is
      stormy-stone-5336.herokuapp.com):

      heroku ps

   -  Now if you point your browser to the server name, you'll get a 404
      HTTP Error. Just try with an URL that thumbor understands. To open
      your web browser pointing to the new server:

      heroku open

   -  Then try something like:

   `<http://stormy-stone-5336.herokuapp.com/unsafe/300x200/http://s.glbimg.com/jo/g1/f/original/2012/03/16/supersonic-skydiver_fran.jpg>`_

   (notice there is no listening port specified)

   If you need to scale thumbor server, read more about it in Heroku's
   documentation.

   The sample implementation for the above links can be found at
   https://github.com/heynemann/thumbor-heroku and is open-source and MIT
   Licensed.

   Another Thumbor/Heroku configuration
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   `This blog post <http://hyperthese.net/post/thumbor-and-heroku/>`__ and
   the attached repositories
   (`Jetpack <https://github.com/ActivKonnect/jetpack>`__ and
   `thumbor-heroku <https://github.com/ActivKonnect/thumbor-heroku>`__)
   explain a more advanced Heroku deployment, that support the ``smart``
   URL feature.

Thumbor on OpenShift
--------------------

.. warning::

   This may be outdated since thumbor moved to python 3.

There's a project showing how to deploy a working version on
`OpenShift <https://www.openshift.com/>`__
https://github.com/rafaelcaricio/thumbor-openshift-example

Thumbor behind CloudFront
-------------------------

.. warning::

   This may be outdated since thumbor moved to python 3.

The awesome people at `yipit <http://yipit.com>`__ are using thumbor
behind the CloudFront
`CDN <http://en.wikipedia.org/wiki/Content_delivery_network>`__ at
Amazon.

The detailed information on how to do it can be seen at `this blog
post <http://tech.yipit.com/2013/01/03/how-yipit-scales-thumbnailing-with-thumbor-and-cloudfront/>`__.
