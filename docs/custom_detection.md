# Custom detection

If you need more detection than the pre-packaged detectors are able to give you
(i.e.: you need to detect glasses), you can always implement your own detectors.

If your detector can be found using python's import mechanism, thumbor will be
able to use it. Just add its full name to the detectors {doc}`configuration`.

## Creating a Custom Detector

The face detector in the
[thumbor repository](https://github.com/thumbor/thumbor) demonstrates how easy
it is to implement your own custom detector. Its source lives at
`thumbor/detectors/face_detector/__init__.py`.

All you have to do is create a class that inherits from BaseDetector and
implement a detect method that receives a context dictionary.

In the context dictionary there's a key called "focal_points" to which you
should append any focal points you found in the picture (using the FocalPoint
class).

If your detector does not find any points, simple call the next() method passing
in the context, so further detection can occur.
