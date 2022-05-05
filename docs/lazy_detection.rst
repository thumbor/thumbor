Lazy Detection
==============

Rationale
---------

Thumbor performs pipeline detection of focal points for a given image.
What this means is that it tries to determine one detection at a time,
only skipping to the next if the current one fails.

We could configure it to run frontal face detection, then if it fails,
try profile face detection and if it fails, best features detection.

As you can imagine, this is a cumbersome process and can take up
precious cpu time from your server(s), eventually leading it to
starvation of CPU. This is why we've implemented what we call Queued
Detection.

Queued Detection
----------------

Configuring thumbor for lazy detecting is as simple as specifying a
detector that supports queued detection.

Thumbor ships with three such detectors, called:

-  ``thumbor.detectors.queued_detector.queued_complete_detector``
-  ``thumbor.detectors.queued_detector.queued_face_detector``
-  ``thumbor.detectors.queued_detector.queued_feature_detector``

These are responsible, respectively, for pipeline detection of face and
feature, only face or only feature.

You can check what additional configuration you need to add to your
configuration file (thumbor.conf) in order to have the bundled detectors
working.

How thumbor deals with queued detection?
----------------------------------------

When an image request arrives with a flag of "smart" detection, a call
is made to the queued detector and it tells thumbor to skip smart
detection and to serve the image with non-smart cropping (much faster).

The call to the queued detector places a message in a Redis Queue that
will later be processed in order to detect focal points in the image.

The next time a request arrive for the same image and with a flag of
"smart" detection, if information on detection is already available (if
the message in the queue has already been processed), thumbor uses that
info to do smart cropping and serves the result.

If the image still hasn't been processed, the same process from before
applies, except thumbor won't place another message in the queue. This
is intended as a way not to flood the queue with requests for the same
image.

Redis Support
-------------

Thumbor supports `Redis single node <https://redis.io/docs/getting-started/>`_.
and `Redis sentinel <https://redis.io/docs/manual/sentinel/>`_.
