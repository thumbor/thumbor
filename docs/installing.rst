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
