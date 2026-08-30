# content of conftest.py

# pylint: disable=unused-import

import pytest

import tests.base  # NOQA


@pytest.fixture
def doctor_output():
    return """Using configuration file found at ./tests/invalid-thumbor.conf

Thumbor doctor will analyze your install and verify if everything is working as expected.

Verifying libraries support...

✅ pycurl is installed correctly.
✅ cairosvg is installed correctly.

Verifying thumbor compiled extensions...

✅ _alpha
✅ _bounding_box
✅ _brightness
✅ _colorize
✅ _composite
✅ _contrast
✅ _convolution
✅ _curve
✅ _equalize
✅ _fill
✅ _nine_patch
✅ _noise
✅ _rgb
✅ _round_corner
✅ _saturation
✅ _sharpen

Verifying extensibility modules found in your thumbor.conf...

❎ thumbor.storages.file_storagee - Storage for source images could not be imported.
❎ thumbor.loaders.http_loaderer - Loader for source images could not be imported.
❎ thumbor.result_storages.file_storagee - ResultStorage could not be imported.
❎ thumbor.engines.pillage - Engine for transforming images could not be imported.
❎ thumbor.storages.file_storager - Uploading to thumbor is enabled and the Upload Storage could not be imported.
✅ thumbor.detectors.face_detector
❎ thumbor.detectors.face_detectorer - Detector could not be imported.
❎ thumbor.detectors.other_invalid - Detector could not be imported.
❎ invalid-filter - Filter could not be imported.
✅ thumbor.filters.redeye
❎ thumbor.optimizers.gifver - Optimizer could not be imported.
❎ thumbor.optimizers.jpegtraner - Optimizer could not be imported.
❎ thumbor.error_handlers.sentryer - Custom error handling is enabled and the error handler module could not be imported.
❎ my.invalid.handler - Custom http handler could not be imported.
✅ thumbor.handler_lists.blacklist
✅ thumbor.handler_lists.healthcheck
✅ thumbor.handler_lists.upload

Verifying security...

❎ Using default security key.
❎ Allowing unsafe URLs.

😞 Oh no! We found some things that could improve... 😞

⚠️Warnings⚠️
* Security
    Error Message:
        Using default security key configuration in thumbor.conf.

    Error Description:
        You should specify a unique security key for thumbor or use a command line param to specify a security key.
\tFor more information visit https://thumbor.readthedocs.io/en/latest/running.html

⛔Errors⛔
* thumbor.storages.file_storagee
    Error Message:
        No module named 'thumbor.storages.file_storagee'

    Error Description:
        Storage for source images could not be imported.

* thumbor.loaders.http_loaderer
    Error Message:
        No module named 'thumbor.loaders.http_loaderer'

    Error Description:
        Loader for source images could not be imported.

* thumbor.result_storages.file_storagee
    Error Message:
        No module named 'thumbor.result_storages.file_storagee'

    Error Description:
        ResultStorage could not be imported.

* thumbor.engines.pillage
    Error Message:
        No module named 'thumbor.engines.pillage'

    Error Description:
        Engine for transforming images could not be imported.

* thumbor.storages.file_storager
    Error Message:
        No module named 'thumbor.storages.file_storager'

    Error Description:
        Uploading to thumbor is enabled and the Upload Storage could not be imported.

* thumbor.detectors.face_detectorer
    Error Message:
        No module named 'thumbor.detectors.face_detectorer'

    Error Description:
        Detector could not be imported.

* thumbor.detectors.other_invalid
    Error Message:
        No module named 'thumbor.detectors.other_invalid'

    Error Description:
        Detector could not be imported.

* invalid-filter
    Error Message:
        No module named 'invalid-filter'

    Error Description:
        Filter could not be imported.

* thumbor.optimizers.gifver
    Error Message:
        No module named 'thumbor.optimizers.gifver'

    Error Description:
        Optimizer could not be imported.

* thumbor.optimizers.jpegtraner
    Error Message:
        No module named 'thumbor.optimizers.jpegtraner'

    Error Description:
        Optimizer could not be imported.

* thumbor.error_handlers.sentryer
    Error Message:
        No module named 'thumbor.error_handlers.sentryer'

    Error Description:
        Custom error handling is enabled and the error handler module could not be imported.

* my.invalid.handler
    Error Message:
        No module named 'my'

    Error Description:
        Custom http handler could not be imported.

* Security
    Error Message:
        Unsafe URLs are enabled.

    Error Description:
        It is STRONGLY recommended that you turn off ALLOW_UNSAFE_URL flag in production environments as this can lead to DDoS attacks against thumbor.
\tFor more information visit https://thumbor.readthedocs.io/en/latest/security.html

❓Need Help❓

If you don't know how to fix the above problems, please open an issue with thumbor.
Don't forget to copy this log and add it to the description.
Open an issue at https://github.com/thumbor/thumbor/issues/new
"""


@pytest.fixture
def doctor_output_no_config():
    return """
Thumbor doctor will analyze your install and verify if everything is working as expected.

Verifying libraries support...

✅ pycurl is installed correctly.
✅ cairosvg is installed correctly.

Verifying thumbor compiled extensions...

✅ _alpha
✅ _bounding_box
✅ _brightness
✅ _colorize
✅ _composite
✅ _contrast
✅ _convolution
✅ _curve
✅ _equalize
✅ _fill
✅ _nine_patch
✅ _noise
✅ _rgb
✅ _round_corner
✅ _saturation
✅ _sharpen

Verifying extension programs...

✅ jpegtran is installed correctly.
✅ ffmpeg is installed correctly.
✅ gifsicle is installed correctly.
Verifying security...


🎉 Congratulations! No errors found! 🎉
"""
