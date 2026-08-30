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

A detector module must expose a class named `Detector` that inherits from
`thumbor.detectors.BaseDetector`. Thumbor constructs it with the current
request context, its position in the configured detector list, and the complete
detector list.

Implement an asynchronous `detect(self)` method. Focal points found by the
detector should be appended to `self.context.request.focal_points`. If the
detector finds no points, call `await self.next()` so the next configured
detector can run.

```python
from thumbor.detectors import BaseDetector
from thumbor.point import FocalPoint


class Detector(BaseDetector):
    async def detect(self):
        # Replace this with the detector's own image-analysis result.
        detected_rectangles = []

        if not detected_rectangles:
            await self.next()
            return

        for left, top, width, height in detected_rectangles:
            self.context.request.focal_points.append(
                FocalPoint.from_square(
                    left,
                    top,
                    width,
                    height,
                    origin="my-detector",
                )
            )
```

Add the module, not the class name, to `DETECTORS`:

```python
DETECTORS = [
    "mylib.detectors.my_detector",
]
```

Detector order is significant. `await self.next()` constructs and invokes the
next detector in this list.
