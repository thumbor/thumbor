Image Metadata
==============

Thumbor uses `piexif <https://github.com/hMatoba/Piexif>`_ to read and write image metadata.

The image metadata is available in ``engine.metadata``.



Reading and writing Metadata
----------------------------

Let's retrieve a list of all the available EXIF tags available in the image::

  >>> engine.metadata
  {
    '0th': {
        271: b'Canon',
        272: b'Canon EOS 5D Mark III',
        282: (300, 1),
        283: (300, 1),
        296: 2,
        305: b'Adobe Photoshop Lightroom 4.4 (Macintosh)',
        306: b'2016:06:24 14:45:44',
        34665: 216
    },
    'Exif': {
        33434: (1, 100),
        33437: (56, 10),
        34850: 1,
        34855: 640,
        34864: 2,
        34866: 640,
        36864: b'0230',
        36867: b'2016:06:23 13:18:05',
        36868: b'2016:06:23 13:18:05',
        37377: (6643856, 1000000),
        37378: (4970854, 1000000),
        37380: (0, 1),
        37381: (3, 1),
        37383: 5,
        37385: 16,
        37386: (123, 1),
        37521: b'91',
        37522: b'91',
        41486: (5242880, 32768),
        41487: (5242880, 32768),
        41488: 4,
        41985: 0,
        41986: 1,
        41987: 1,
        41990: 0,
        42033: b'042024004240',
        42034: ((70, 1), (200, 1), (0, 0), (0, 0)),
        42036: b'EF70-200mm f/2.8L IS II USM',
        42037: b'0000c139be'},
    'GPS': {},
    'Interop': {},
    '1st': {},
    'thumbnail': None
  }

The reference to the values can be found here `Exif values <https://github.com/hMatoba/Piexif/blob/master/piexif/_exif.py>`

  >>> tag = metadata["Exif"][piexif.ExifIFD.DateTimeOriginal]
  "2016:06:23 13:18:05"


piexif API reference
------------------------------

.. module:: piexif
.. autoclass:: dict
   :members: __getitem__, __setitem__, __delitem__
