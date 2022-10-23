How to upload Images
====================

Thumbor provides a ``/image`` REST end-point to upload your images and
manage it.

This way you can send thumbor your original images by doing a simple
post to its urls.

Configuration
-------------

The table below show all configuration parameters to manage image upload:

+-----------------------------+----------------------------------+--------------------------------------------------------+
| Configuration parameter     | Default                          | Description                                            |
+=============================+==================================+========================================================+
| UPLOAD\_ENABLED             | False                            | Indicates whether thumbor should enable File uploads   |
+-----------------------------+----------------------------------+--------------------------------------------------------+
| UPLOAD\_PUT\_ALLOWED        | False                            | Indicates whether image overwrite should be allowed    |
+-----------------------------+----------------------------------+--------------------------------------------------------+
| UPLOAD\_DELETE\_ALLOWED     | False                            | Indicates whether image deletion should be allowed     |
+-----------------------------+----------------------------------+--------------------------------------------------------+
| UPLOAD\_PHOTO\_STORAGE      | thumbor.storages.file\_storage   | The type of storage to store uploaded images with      |
+-----------------------------+----------------------------------+--------------------------------------------------------+
| UPLOAD\_DEFAULT\_FILENAME   | image                            | Default filename for image uploaded                    |
+-----------------------------+----------------------------------+--------------------------------------------------------+
| UPLOAD\_MAX\_SIZE           | 0                                | Max size in Kb for images uploaded to thumbor          |
+-----------------------------+----------------------------------+--------------------------------------------------------+
| MIN\_WIDTH                  | 1                                | Min width in pixels for images uploaded                |
+-----------------------------+----------------------------------+--------------------------------------------------------+
| MIN\_HEIGHT                 | 1                                | Min height in pixels for images uploaded               |
+-----------------------------+----------------------------------+--------------------------------------------------------+

Thumbor comes with the ``/image`` REST end-point to upload disabled by
default. In order to enable it, just set the ``UPLOAD_ENABLED``
configuration in your thumbor.conf file to ``True``.

Thumbor will then use the storage specified in the
``UPLOAD_PHOTO_STORAGE`` configuration to save your images. You can use
an existing storage (filesystem, redis, mongo, hbase...) or
:doc:`create your own storage <create_my_own_storage>` if needed .

You can manage image putting and deletions simply set the configuration
parameters ``UPLOAD_PUT_ALLOWED`` and ``UPLOAD_DELETE_ALLOWED`` to
``True``. This parameters are set to ``False`` by default for security
reasons.

Finally the upload constraints (max size, image width and height) will
be controlled by ``UPLOAD_MAX_SIZE``, ``MIN_WIDTH`` and ``MIN_HEIGHT``
parameters.

API Usage
---------

The Thumbor ``/image`` REST end-point supports the commons `HTTP
methods <http://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol>`__ :

* POST : to upload a new image
* GET : to display an image uploaded
* PUT : to replace an image uploaded by another preserving the URI
* DELETE : to remove an image uploaded from storage

By default, ``PUT`` and ``DELETE`` methods are disabled as explained
above. This is done to tighten thumbor's security.

Posting
~~~~~~~

Posting is the only method allowed by default when you activate the
upload module. It allows new images to be sent to Thumbor.

In order to upload a new image, you have two choices:
 * send an HTTP **POST** to the ``/image`` end-point with the image as payload (REST style)
 * send an HTTP **POST** to the ``/image`` end-point with a multi-part form with a file field called media (Form style).

In the REST style mode you may add an optional ``Slug`` header to define
the image filename, which is useful for SEO reasons. Not specifying a
``Slug`` causes the server to use the default filename for the image
(``UPLOAD_DEFAULT_FILENAME`` parameter) .

The HTTP response will return a ``Location`` header pointing on the
uploaded image. The URI presented in ``Location`` header may be used to
update or delete the image uploaded (see below).

For examples, see the `Upload an image via the REST API`_ or `Upload an image via a form`_ sections.

 HTTP status code
^^^^^^^^^^^^^^^^^

The status code returned will be :

-  201 Created (success)
-  415 Unsupported Media Type (image type is not allowed)
-  412 Precondition Failed (image is too small or the file is not an
   image)

Putting
~~~~~~~

Putting is a little more dangerous if you don't have strict control of
who can access the ``/image`` end-point. This is because whatever is
sent using this method gets saved to storage, overwriting the previous
entry.

In order to replace an existing image, all you have to do is send an
HTTP **PUT** request to the ``/image`` end-point with the new image
content as payload. The new image will replace the original image
preserving the URI.

As for the ``POST`` method you may add an optional ``Slug`` header to
define the image filename.

The HTTP response will return a ``Location`` header pointing on the
modified image. The URI presents in ``Location`` header may be used to
update again the image or delete it.

For an example see the `Modifying an image`_ section.

HTTP status code
^^^^^^^^^^^^^^^^

The status code returned will be :

-  204 No Content (success)
-  405 Method Not Allowed (if thumbor's configuration disallows putting
   images)
-  415 Unsupported Media Type (image type is not allowed)
-  412 Precondition Failed (image is too small or file is not an image)

Deleting
~~~~~~~~

Deleting can be very dangerous, thus is disabled by default.

If you do enable it, in order to delete an image, all you have to do is
send an HTTP **DELETE** request to the ``/image`` end-point.

For an example, see the `Deleting an image`_ section.

HTTP status code
^^^^^^^^^^^^^^^^

-  204 No Content (success)
-  404 Not Found (image doesn't exists)
-  405 Method Not Allowed (if thumbor's configuration disallows deleting
   images)

Example
---------

Assuming the thumbor server is located at : ``http://thumbor-server``

Upload an image via the REST API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When using the ``/image`` REST end-point to upload your image via the
REST API :

::

    curl -i -H "Content-Type: image/jpeg" -H "Slug: photo.jpg"
            -XPOST http://thumbor-server/image --data-binary "@tests/fixtures/images/20x20.jpg"

the HTTP **POST** request was send to the server :

::

    POST /image
    Content-Type: image/jpeg
    Content-Length: 822
    Slug : photo.jpg

and the Thumbor server should return:

::

    HTTP/1.1 201 Created
    Content-Length: 0
    Content-Type: text/html; charset=UTF-8
    Location: /image/05b2eda857314e559630c6f3334d818d/photo.jpg
    Server: TornadoServer/2.1.1

The image is created at
``http://thumbor-server/image/05b2eda857314e559630c6f3334d818d/photo.jpg``.
It can be retrieved, modified or deleted via this URI.

The optional ``Slug`` HTTP header specifies the filename to use for the
image uploaded.

Upload an image via a form
~~~~~~~~~~~~~~~~~~~~~~~~~~

When using the ``/image`` REST end-point to upload your images via a
form, the user is free to choose the filename of the image via the
``filename`` field :

::

    curl -i -XPOST http://thumbor-server/image
            -F "media=@tests/fixtures/images/20x20.jpg;type=image/jpeg;filename=croco.jpg"

the HTTP **POST** request was send to the server :

::

    POST /image
    Content-Type: multipart/form-data; boundary=----------------------------11df125d8b12
    Content-Length: 822

and the Thumbor server should return:

::

    HTTP/1.1 201 Created
    Content-Length: 0
    Content-Type: text/html; charset=UTF-8
    Location: /image/05b2eda857314e559630c6f3334d818d/croco.jpg

The image is created at
``http://thumbor-server/image/05b2eda857314e559630c6f3334d818d/croco.jpg``.
It can be retrieve, modify or delete via this URI using the REST API.

Modifying an image
~~~~~~~~~~~~~~~~~~

To replace the previously uploaded image by another we use:

::

    curl -i -H "Content-Type: image/jpeg" -H "Slug: modified_image.jpg"
            -XPUT http://thumbor-server/image/05b2eda857314e559630c6f3334d818d/photo.jpg --data-binary "@tests/fixtures/images/20x20.jpg"

the HTTP **PUT** request was send to the server :

::

    PUT /image/05b2eda857314e559630c6f3334d818d/photo.jpg
    Content-Type: image/jpeg
    Content-Length: 822
    Slug : modified_image.jpg

and the Thumbor server should return:

::

    HTTP/1.1 204 No Content
    Content-Length: 0
    Content-Type: text/html; charset=UTF-8
    Location: /image/05b2eda857314e559630c6f3334d818d/modified_image.jpg
    Server: TornadoServer/2.1.1

Deleting an image
~~~~~~~~~~~~~~~~~

Finally to delete the uploaded image we use:

::

    curl -i -XDELETE http://thumbor-server/image/05b2eda857314e559630c6f3334d818d/modified_image.jpg

the HTTP **DELETE** request was send to the server :

::

    DELETE /image/05b2eda857314e559630c6f3334d818d/modified_image.jpg

and the Thumbor server should return:

::

    HTTP/1.1 204 No Content
    Content-Length: 0
    Content-Type: text/html; charset=UTF-8
    Server: TornadoServer/2.1.1
