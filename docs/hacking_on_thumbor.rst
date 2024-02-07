Hacking on Thumbor
==================

So you want to contribute with thumbor? Welcome onboard!

There are a few things you'll need in order to properly start hacking on
it.

First step is to `fork it <http://help.github.com/fork-a-repo/>`__ and
create your own clone of thumbor.

Dependencies
------------

We seriously advise you to use
`virtualenv <http://pypi.python.org/pypi/virtualenv>`__ since it will
keep your environment clean of thumbor's dependencies and you can choose
when to "turn them on".

You'll also need python >= 3.9 and `python poetry <https://python-poetry.org/>`_.

Installing poetry should be as easy as ``pip install poetry``, but you can find more about it in their website.

Other than that, you'll also need `redis-server <https://redis.io>`` installed (for queued detector unit tests).

Initializing the Environment
----------------------------

Once you've created your virtualenv, and installed poetry, make sure you can use poetry::

    $ poetry --version
    Poetry version 1.0.3

You should see something similar. After that we just need to download all python packages with::

    $ make setup

Running the Tests
-----------------

Running the tests is as easy as::

    $ make test

You should see the results of running your tests after an instant.

If you are experiencing "Too many open files" errors while running the
tests, try increasing the number of open files per process, by running
this command::

    $ ulimit -S -n 2048

Read
http://superuser.com/questions/433746/is-there-a-fix-for-the-too-many-open-files-in-system-error-on-os-x-10-7-1
for more info on this.

Linting your code
-----------------

Please ensure that your editor is configured to use `black <https://github.com/psf/black>`_, `flake8 <https://flake8.pycqa.org/en/latest/>`_ and `pylint <https://www.pylint.org/>`_.

Even if that's the case, don't forget to run ``make flake pylint`` before commiting and fixing any issues you find. That way you won't get a request for doing so in your PR.

Pull Requests
-------------

After hacking and testing your contribution, it is time to make a pull
request. Make sure that your code is already integrated with the master
branch of thumbor before asking for a pull request.

To add thumbor as a valid remote for your repository::

    $ git remote add thumbor git://github.com/thumbor/thumbor.git

To merge thumbor's master with your fork::

    $ git pull thumbor master

If there was anything to merge, just run your tests again. If they pass,
`send a pull request <http://help.github.com/send-pull-requests/>`__.

Introducing a new Dependency
----------------------------

If we introduce a new dependency, the testing docker images need to be updated.

If the new dependency requires changes to the docker image, make sure to update the TestDockerfile36, TestDockerfile37, TestDockerfile38 and TestDockerfile39 files.

Then build and publish with::

    make test-docker-build test-docker-publish

Remember that you must be logged in with your docker hub account and you must be part of the `thumbororg <https://hub.docker.com/repository/docker/thumbororg/thumbor-test>` team of administrators.

Running tests in docker
-----------------------

If you do not wish to configure your environment with thumbor's dependencies, you can use our docker image to run tests with::

    make test-docker-run

Or if you want to run a specific python version with your tests::

    make test-docker-39-run

Just replace '39' with the python version you want: 36, 37, 38 or 39.
