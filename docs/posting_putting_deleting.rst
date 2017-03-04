Posting, Putting and Deleting
==============================

thumbor original photo uploading end-point supports three different
`http
verbs <http://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol>`__:
put, post and delete.

By default, put and delete are disabled. This is done to tighten
thumbor's security. If you wish to enable them, please refer to the
:doc:`how_to_upload_images` page.

Posting
-------

Posting is the only allowed by default method. It allows new images to
be sent to thumbor. If the same image is sent again, thumbor will raise
an exception.

This is done so users can't overwrite images with other images, possibly
defacing your website.

In order to post a new image, all you have to do is send a multi-part
form with a file field called media and action of
``http://{thumbor-server}/image`` and method of ``POST``.

HTTP status code
~~~~~~~~~~~~~~~~

-  201 Created (success)
-  409 Conflict (image already exists)
-  412 Precondition Failed (image is too small or the file is not an
   image)

Putting
-------

Putting is a little more dangerous if you don't have strict control of
who can access the ``/image`` route. This is because whatever is sent
using this method gets saved to storage, overwriting the previous entry.

In order to put a new image, all you have to do is send a multi-part
form with a file field called ``media`` and action of
``http://{thumbor-server}/image`` and method of ``PUT``.

HTTP status code
~~~~~~~~~~~~~~~~

-  201 Created (success)
-  405 Method Not Allowed (if thumbor's configuration disallows putting
   images)
-  412 Precondition Failed (image is too small or file is not an image)

Deleting
--------

Deleting can be very dangerous, thus is disabled by default.

If you do enable it, in order to delete an image, all you have to do is
send a request to ``http://{thumbor-server}/image`` with a method of
``DELETE`` and a field called ``file_path`` with the same path that was
used when uploading the image.

HTTP status code
~~~~~~~~~~~~~~~~

-  200 OK (success)
-  405 Method Not Allowed (if thumbor's configuration disallows deleting
   images)
