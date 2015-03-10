So you want to contribute with thumbor? Welcome onboard!

There are a few things you'll need in order to properly start hacking on it.

First step is to fork it at http://help.github.com/fork-a-repo/ and create your own clone of thumbor.

## Dependencies

We seriously advise you to use virtualenv (http://pypi.python.org/pypi/virtualenv) since it will keep your environment clean of thumbor's dependencies and you can choose when to "turn them on".

You'll also need python >= 2.7 and < 3.0.

The following packages are required:

* Tornado >= 2.3.0
* pyCrypto >= 2.4.1
* pycurl >= 7.19.0
* Pillow >= 2.3.0
* redis >= 2.4.11
* pymongo >= 2.1.1
* pyvows
* tornado_pyvows
* argparse
* gevent >= 0.13.6 (requires libevent - http://libevent.org/)

You'll also need a recent version of OpenCV (http://opencv.willowgarage.com/wiki/) installed. When installing OpenCV, it will create a python binding. Make sure this binding is visible to your current virtualenv (if you are using it).

Other than that, you'll also need a mongo database running, as well as a redis database running. Both are trivial to setup at modern linux or mac os systems.

## Running the Tests

Running the tests is as easy as:

    make test

You should see the results of running your tests after an instant.

If you are experiencing "Too many open files" errors while running the tests, try increasing the number of open files per process, by running this command:

    ulimit -S -n 2048

Read http://superuser.com/questions/433746/is-there-a-fix-for-the-too-many-open-files-in-system-error-on-os-x-10-7-1 for more info on this.

## Pull Requests

After hacking and testing your contribution, it is time to make a pull request. Make sure that your code is already integrated with the master branch of thumbor before asking for a pull request.

To add thumbor's remote as a valid remote for your repository:

    git remote add thumbor git://github.com/thumbor/thumbor.git

To merge thumbor's master with your fork:

    git pull thumbor master

If there was anything to merge, just run your tests again. If they pass, send a pull request (http://help.github.com/send-pull-requests/).

The latest version of this document can be found at [Hacking on thumbor](https://github.com/thumbor/thumbor/wiki/Hacking-on-thumbor).
