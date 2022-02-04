So you want to contribute with thumbor? Awesome! Welcome aboard!

## First things first

What kind of contribution are you aiming for? Features, documentation and
bug fixes are always welcome.

**Please note**: we dropped feature-support for thumbor 6. That said, no
new features are going to be added on thumbor 6.x. If you still want to
contribute (a bug fix), please head at `fixes/6.7.x`.

## Steps

There are a few things you'll need in order to properly start hacking on it.

1. [Fork it](http://help.github.com/fork-a-repo/)
2. Install dependencies and initialize environment
3. Hack, in no particular order:
   - Write enough code
   - Write tests for that code
   - Check that other tests pass
   - Repeat until you're satisfied
4. Submit a pull request

## Install Dependencies

You'll need [redis-server](https://redis.io)
installed (for queued detector unit tests).

Other than that, we seriously advise you to use
[virtualenv](http://pypi.python.org/pypi/virtualenv) since it will keep
your environment clean of thumbor's dependencies and you can choose when
to "turn them on".

The project requires Python 3.7+, and in this version virtualenv is already installed by default, to create a virtual environment follow the next steps:


1. Create a virtual environment, in the folder .venv, located in the user's home folder
```
$ python3 -m venv ~/.venv/<my_env_name>
```

2. Activate the virtual environment
```
$ source ~/.venv/<my_env_name>/bin/activate
```

3. Now you can install the dependencies in your virtual environment
4. In case you want deactivate your virtual environment:
```
$ deactivate
```

## Initializing the Environment

You can install thumbor dev dependencies with:

    $ make setup

## Running the Tests

Running the tests is as easy as:

    $ make test

You should see the results of running your tests after an instant.

If you are experiencing "Too many open files" errors while running the
tests, try increasing the number of open files per process, by running
this command:

    $ ulimit -S -n 2048

Read
<http://superuser.com/questions/433746/is-there-a-fix-for-the-too-many-open-files-in-system-error-on-os-x-10-7-1>
for more info on this.

## Linting your code

Please ensure that your editor is configured to use
[black](https://github.com/psf/black),
[flake8](https://flake8.pycqa.org/en/latest/) and
[pylint](https://www.pylint.org/).

Even if that's the case, don't forget to run `make flake pylint` before
committing and fixing any issues you find. That way you won't get a
request for doing so in your PR.

## Pull Requests

After hacking and testing your contribution, it is time to make a pull
request. Make sure that your code is already integrated with the `master`
branch of thumbor before asking for a pull request.

To add thumbor as a valid remote for your repository:

    $ git remote add thumbor git://github.com/thumbor/thumbor.git

To merge thumbor's master with your fork:

    $ git pull thumbor master

If there was anything to merge, just run your tests again. If they pass,
[send a pull request](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request).

The latest version of this document can be found at [Hacking on thumbor](https://thumbor.readthedocs.io/en/latest/hacking_on_thumbor.html).
