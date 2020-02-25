Enabling detectors
==================

Out of the box, thumbor does not enable any feature or facial detection.
Enabling it is pretty easy, though.

.. note::
    Starting with release 7.0.0 thumbor depends on opencv-python-headless.
    This means that it should be extremely easy to use the face and feature
    detectors.

For information on all built-in detectors check the :doc:`available_detectors` page.

Configuration
-------------

In order to tell thumbor what detectors it should run in the original
image, you must add them to your ``thumbor.conf`` file in the following
key::

    DETECTORS = [
        'thumbor.detectors.face_detector',
        'thumbor.detectors.feature_detector',
    ]

The above configuration tells thumbor that it should run both the facial
detection and the feature detection. These are mutually exclusive,
meaning that if a face is detected, the feature detector won't be run.

Using it
--------

After restarting thumbor, it should be as easy as adding a ``/smart``
option to your URLs, like::

    http://localhost:8888/unsafe/200x400/smart/https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg

.. note::
    Whenever you are not sure what thumbor is "seeing", use the debug mode::

        http://localhost:8888/unsafe/debug/200x400/smart/https%3A%2F%2Fgithub.com%2Fthumbor%2Fthumbor%2Fraw%2Fmaster%2Fexample.jpg

    Thumbor will draw a square on all focal points it found. That way you can be sure of why an image was cropped the way it was.

Lazy Detection
--------------

Facial detection can be pretty expensive for thumbor, so it is not
advisable to do it synchronously. Please refer to the :doc:`lazy_detection`
page for instructions on using it.

Available Detectors
-------------------

A list of available detectors can be found at :doc:`available_detectors`.
