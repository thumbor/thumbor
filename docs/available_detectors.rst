Available detectors
===================


Face Detector
-------------

``thumbor.detectors.face_detector``

It detects faces, It considers the frontal part of the face for detection.


Feature Detector
----------------

``thumbor.detectors.feature_detector``

Detector used to find relevant focal points in the image. "Features" in this case and in other cases such as machine learning, are pieces of information (in this case, pieces of the image) that are relevant to solving a computational problem. For Thumbor we use this set of focal points to identify faces, for example. We use the first 10 set of points found.

Glasses Detector
----------------

``thumbor.detectors.glasses_detector``

It detects glasses on the faces.


Profile Detector
----------------

``thumbor.detectors.profile_detector``

It detects faces, It considers the side part of the face for detection.


Queued Detector
---------------

``thumbor.detectors.queued_detector``

Detector used to allow face detection process asynchronously.
