# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_get_doctor_output 1'] = '''Using configuration file found at ./tests/invalid-thumbor.conf


Thumbor doctor will analyze your install and verify if everything is working as expected.

Verifying libraries support...

✅ pycurl is installed correctly.
✅ cairosvg is installed correctly.
❎  pyexiv2 is not installed.
If you do not need EXIF metadata, you can safely ignore this.
For more information visit https://python3-exiv2.readthedocs.io/en/latest/.


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

Verifying thumbor filters...

✅ thumbor.filters.brightness
✅ thumbor.filters.colorize
✅ thumbor.filters.contrast
✅ thumbor.filters.rgb
✅ thumbor.filters.round_corner
✅ thumbor.filters.quality
✅ thumbor.filters.noise
✅ thumbor.filters.watermark
✅ thumbor.filters.equalize
✅ thumbor.filters.fill
✅ thumbor.filters.sharpen
✅ thumbor.filters.strip_exif
✅ thumbor.filters.strip_icc
✅ thumbor.filters.frame
✅ thumbor.filters.grayscale
✅ thumbor.filters.rotate
✅ thumbor.filters.format
✅ thumbor.filters.max_bytes
✅ thumbor.filters.convolution
✅ thumbor.filters.blur
✅ thumbor.filters.extract_focal
✅ thumbor.filters.focal
✅ thumbor.filters.no_upscale
✅ thumbor.filters.saturation
✅ thumbor.filters.max_age
✅ thumbor.filters.curve
✅ thumbor.filters.background_color
✅ thumbor.filters.upscale
✅ thumbor.filters.proportion
✅ thumbor.filters.stretch

Verifying extensibility modules found in your thumbor.conf...

❎  thumbor.storages.file_storagee - Storage for source images could not be imported.
❎  thumbor.loaders.http_loaderer - Loader for source images could not be imported.
❎  thumbor.result_storages.file_storagee - ResultStorage could not be imported.
❎  thumbor.storages.file_storager - Uploading to thumbor is enabled and the Upload Storage could not be imported.


😞 Oh no! We found some things that could improve... 😞

⚠️Warnings⚠️
* pyexiv2
    Error Message:
        /lib/x86_64-linux-gnu/libboost_python38.so.1.71.0: undefined symbol: _Py_fopen

    Error Description:
        If you do not need EXIF metadata, you can safely ignore this.
\tFor more information visit https://python3-exiv2.readthedocs.io/en/latest/.

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

* thumbor.storages.file_storager
    Error Message:
        No module named 'thumbor.storages.file_storager'

    Error Description:
        Uploading to thumbor is enabled and the Upload Storage could not be imported.


If you don't know how to fix them, please open an issue with thumbor.
Don't forget to copy this log and add it to the description of your issue.
Open an issue at https://github.com/thumbor/thumbor/issues/new
'''
