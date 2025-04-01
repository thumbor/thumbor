gifv
==========

The gifv optimizer is able to convert gifs to mp4 or webm videos, often resulting in dramatically smaller sized files.

**Gifv is categorized as experimental and should be used with caution.** It uses ffmpeg to convert gifs to videos and so it's sensitive to changes with ffmpeg. It's recommended to lock your ffmpeg version with a fixed version (chef, docker, etc) and if updating make sure to check that the update doesn't break gifv. **FFmpeg version 3.2.4 is the current recommended version.** Later version, such as 3.3 will break the proper conversion of gif delays to frame durations in videos ... meaning videos will not be the same length as equivelant gifs.

To enable gifv, ensure ffmpeg is in PATH and enable the optimizer in your config:

.. code-block:: python

  OPTIMIZERS = [
    'thumbor.optimizers.gifv',
  ]

Once activated, you must add the ``gifv()`` option to your filters list. An example request might look like this:

.. code-block:: text

  http://localhost:8888/unsafe/filters:gifv()/http://localhost/livingroom.gif

The above example will default to using the mp4 video container with h264 video. You can also be explicit:

.. code-block:: text

  http://localhost:8888/unsafe/filters:gifv(mp4)/http://localhost/livingroom.gif

or use explicitly specify webm

.. code-block:: text

  http://localhost:8888/unsafe/filters:gifv(webm)/http://localhost/livingroom.gif


Because videos (in mp4 or webm format) cannot contain alpha transparency a background color will be automatically added. The default color is white. You can also specify a background color:

.. code-block:: text

  http://localhost:8888/unsafe/filters:gifv():background_color(ff00ff)/http://localhost/livingroom.gif

.. code-block:: text

  http://localhost:8888/unsafe/filters:gifv():background_color(f0f)/http://localhost/livingroom.gif


.. code-block:: text

  http://localhost:8888/unsafe/filters:gifv():background_color(magenta)/http://localhost/livingroom.gif


The color must be specified in 6 character hex, 3 character hex or color name. But 6 or 3 character hex are the preferred formats. Including a ``#`` symbol in your color will break the url if not url encoded and thumbor will error on the request. The recommendation is to not use them at all which also makes urls shorter. But if you must a leading `%23` will probably work.
