Custom detection
================

If you need more detection than the pre-packaged detectors are able to
give you (i.e.: you need to detect glasses), you can always implement
your own detectors.

If your detector can be found using python's import mechanism, thumbor
will be able to use it. Just add its full name to the detectors
:doc:`configuration`.

Creating a Custom Detector
--------------------------

As you can see here `<https://github.com/thumbor/thumbor/blob/master/thumbor/detectors/face_detector/__init__.py>`_
it is pretty easy to implement your own custom detector.

All you have to do is create a class that inherits from BaseDetector and
implement a detect method that receives a context dictionary.

In the context dictionary there's a key called "focal\_points" to which
you should append any focal points you found in the picture (using the
FocalPoint class).

If your detector does not find any points, simple call the next() method
passing in the context, so further detection can occur.
