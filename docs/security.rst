Security
========

thumbor's team is very concerned about security and vulnerabilities of
the service. Even though the team strives to cover most scenarios, if
you find any flaws or vulnerabilities, please contact the team or
`create an issue <https://github.com/thumbor/thumbor/issues>`__.

URL Tampering
-------------

Consider the following URL for an image:
``http://some.server.com/unsafe/300x300/smart/path/to/image.jpg``.

Now let's say that some malicious user wants to overload your service.
He can easily ask for other sizes in loops or worse, like:

::

    http://some.server.com/unsafe/300x301/smart/path/to/image.jpg
    http://some.server.com/unsafe/300x302/smart/path/to/image.jpg
    http://some.server.com/unsafe/300x303/smart/path/to/image.jpg
    ...
    http://some.server.com/unsafe/300x9999/smart/path/to/image.jpg
    ...
    http://some.server.com/unsafe/9999x9999/smart/path/to/image.jpg

And that's not even counting varying the available options.

Other than that, the user can ask for images that do not exist, thus
forcing us to perform useless http GET operations or filesystem
operations.

We classified both scenarios above as **URL Tampering**.

Stopping Tampering
~~~~~~~~~~~~~~~~~~

In order to prevent users from tampering with the URL, thumbor provides
a configuration called ``SECURITY_KEY``. This is the key used to
generate a `hash-based message authentication
code <http://en.wikipedia.org/wiki/Hash-based_message_authentication_code>`__.

The process is very straightforward. The web server that has the page
using thumbor's image generates an authentication code for the options
and image url, using the **SECURITY\_KEY**.

When end-users access the page and thus load the image, thumbor
generates an authentication code for the same options and image url,
using the same **SECURITY\_KEY**. If both authentication codes match,
thumbor processes it.

The secure endpoint looks like this:
``/<authentication code with 28 characters>/300x200/smart/path/to/image.jpg``.

HMAC method
~~~~~~~~~~~

We intend to supply toolkits in many languages that automate the signing
process, but we might need help from the community in this direction.

**thumbor uses standard HMAC with SHA1 signing.**

Let's use as an example the url
``http://some.server.com/unsafe/300x200/smart/path/to/image.jpg``.

In order to convert that to a "safe" url, we must sign the part
``300x200/smart/path/to/image.jpg``:

1. Generate a ``signature`` of that part using HMAC-SHA1 with the
   **SECURITY\_KEY**.
2. Encode the ``signature`` as base64. thumbor uses
   ``urlsafe_b64encode`` method of the native python's base64 module.
   This method replaces some characters in the base64 string so it
   becomes more url friendly.
3. Append the ``encoded_signature`` to the beginning of the URL, like:
   ``/1234567890123456789012345678/300x200/smart/path/to/image.jpg``.

That last part gives you the new url:
http://thumbor-server/1234567890123456789012345678/300x200/smart/path/to/image.jpg.
Notice that the url includes the options part ``300x200/smart``. That's
required for thumbor to generate an authentication code to match the one
that signs the image (``1234567890123456789012345678``).

**The code included in this documentation is illustrational and should
not be used for any purposes.**

The description of the base64 method is:
`reference <http://docs.python.org/library/base64.html>`__

::

    base64.urlsafe_b64encode(s)
    Encode string s using a URL-safe alphabet, which substitutes
    - instead of + and _ instead of / in the standard Base64 alphabet.
    The result can still contain =.

Loading Images over HTTPS
-------------------------

The default http_loader loads images by default over http. To change the
default to https, use the https_loader instead. To enforce https, use the
strict_https_loader. Check the :doc:`image_loader` page for more details.

Libraries
---------

There are implementations of url generators in various languages, take a
look at the :doc:`libraries` page to find information
about them.
