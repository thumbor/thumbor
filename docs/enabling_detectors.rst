Enabling detectors
==================

Out of the box, thumbor does not enable any feature or facial detection.
Enabling it is pretty easy, though.

This documentation assumes you have OpenCV installed. It is a
requirement if you want to use thumbor's :doc:`available_detectors`.

Configuration
-------------

In order to tell thumbor what detectors it should run in the original
image, you must add them to your ``thumbor.conf`` file in the following
key:

::

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
option to your URLs, like:

::

    http://<thumbor>:<port>/unsafe/300x200/smart/my.domain.com/picture.png

Lazy Detection
--------------

Facial detection can be pretty expensive for thumbor, so it is not
advisable to do it synchronously. Please refer to the :doc:`lazy_detection`
page for instructions on using it.

Available Detectors
-------------------

A list of available detectors can be found at :doc:`available_detectors`.
