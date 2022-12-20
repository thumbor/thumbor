Installing
==========

Installing thumbor is really easy because it supports the distutils form
of packaging (http://docs.python.org/distutils/setupscript.html).

.. warning::
    Thumbor v7.0.0 and later only supports python 3.7+.
    This change was important to improve our codebase and ensure
    it's easier to change in future releases.
    More breaking changes will come, but we do not anticipate any
    as big as this one. Please refer to
    `release notes <https://github.com/thumbor/thumbor/releases>`_
    for details on how to upgrade.

Stable
------

The latest stable version of thumbor is always published in the Python
Package Index (http://pypi.python.org/pypi), so it can be easily
installed using ``pip install thumbor`` or ``easy_install thumbor``.

Ubuntu/Debian using aptitude (apt-get)
--------------------------------------

There's now an officially supported ppa for thumbor if you are using
aptitude.

To install using aptitude, add the following lines to your sources list:

::

    deb http://ppa.launchpad.net/thumbor/ppa/ubuntu <your release> main
    deb-src http://ppa.launchpad.net/thumbor/ppa/ubuntu <your release> main

If you are using ubuntu 12.10 (quantal), it would be:

::

    deb http://ppa.launchpad.net/thumbor/ppa/ubuntu quantal main
    deb-src http://ppa.launchpad.net/thumbor/ppa/ubuntu quantal main

Or you can add the repository to you sources list via the command line:

::

    sudo add-apt-repository ppa:thumbor/ppa

After that just update your sources:

::

    sudo aptitude update

And install using plain old aptitude install:

::

    sudo aptitude install thumbor

A service will be created for you that gets started when the machine
starts up (using upstart).

By default thumbor will be disabled. Open ``/etc/default/thumbor`` and
change (or remove) the flag ``enabled`` to ``1`` or use the command
``sudo service thumbor start force=1`` (force\_start=1 for
thumbor<3.7.0) to temporarily start thumbor. You can also override other
defaults like the location of the configuration file by editing
``/etc/default/thumbor``.

The configuration for thumbor will be at ``/etc/thumbor.conf`` and the
security key at ``/etc/thumbor.key``. There will be one instance running
at ``http://localhost:8888``.

If you want to run many instances of thumbor you'll need to run it in
many ports. That means you'll need to use some form of load balancing
(NGINX, Apache, Varnish, Haproxy, etc).

Running many instances of thumbor is as simple as editing
``/etc/default/thumbor`` and changing the ``port`` key to as many ports
as you want, comma-separated: ``port=8888,8889,8890`` (for
thumbor>3.7.0).

If you need more detail head to
https://launchpad.net/~thumbor/+archive/ppa.

From the source of a stable release
-----------------------------------

Download the latest stable source-code version here on GitHub or PyPI
and decompress it.

In the path you decompressed, execute ``pip install .`` or
``python setup.py install``.

From the latest version of the source
-------------------------------------

Clone thumbor's repository and install it using one of the following:

``pip install git+git://github.com/thumbor/thumbor.git``

or

.. code:: bash

    git clone git://github.com/thumbor/thumbor.git

    cd thumbor

    python setup.py install
