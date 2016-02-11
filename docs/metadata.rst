Image Metadata
==============

Thumbor uses `Pyexiv2 <http://tilloy.net/dev/pyexiv2/>`_ to read and write image metadata.

If the Pyexif2 or Py3exif2 Python library is available, the PIL engine also stores image metadata
in ``engine.metadata``.



Reading and writing Metadata
----------------------------
This part is copied from the `Pyexiv2 Tutorial <http://tilloy.net/dev/pyexiv2/tutorial.html>`_

Let's retrieve a list of all the available EXIF tags available in the image::

  >>> engine.metadata.exif_keys
  ['Exif.Image.ImageDescription',
   'Exif.Image.XResolution',
   'Exif.Image.YResolution',
   'Exif.Image.ResolutionUnit',
   'Exif.Image.Software',
   'Exif.Image.DateTime',
   'Exif.Image.Artist',
   'Exif.Image.Copyright',
   'Exif.Image.ExifTag',
   'Exif.Photo.Flash',
   'Exif.Photo.PixelXDimension',
   'Exif.Photo.PixelYDimension']

Each of those tags can be accessed with the ``[]`` operator on the metadata,
much like a python dictionary::

  >>> tag = metadata[b'Exif.Image.DateTime']

The value of an :class:`ExifTag` object can be accessed in two different ways:
with the :attr:`raw_value` and with the :attr:`value` attributes::

  >>> tag.raw_value
  '2004-07-13T21:23:44Z'

  >>> tag.value
  datetime.datetime(2004, 7, 13, 21, 23, 44)

The raw value is always a byte string, this is how the value is stored in the
file. The value is lazily computed from the raw value depending on the EXIF type
of the tag, and is represented as a convenient python object to allow easy
manipulation.

Note that querying the value of a tag may raise an :exc:`ExifValueError` if the
format of the raw value is invalid according to the EXIF specification (may
happen if it was written by other software that implements the specification in
a broken manner), or if pyexiv2 doesn't know how to convert it to a convenient
python object.

Accessing the value of a tag as a python object allows easy manipulation and
formatting::

  >>> tag.value.strftime('%A %d %B %Y, %H:%M:%S')
  'Tuesday 13 July 2004, 21:23:44'

Now let's modify the value of the tag and write it back to the file::

  >>> import datetime
  >>> tag.value = datetime.datetime.today()

  >>> engine.metadata.write()

Similarly to reading the value of a tag, one can set either the
:attr:`raw_value` or the :attr:`value` (which will be automatically converted to
a correctly formatted byte string by pyexiv2).

You can also add new tags to the metadata by providing a valid key and value
pair (see exiv2's documentation for a list of valid
`EXIF tags <http://exiv2.org/tags.html>`_)::

  >>> key = 'Exif.Photo.UserComment'
  >>> value = 'This is a useful comment.'
  >>> engine.metadata[key] = pyexiv2.ExifTag(key, value)

As a handy shortcut, you can always assign a value for a given key regardless
of whether it's already present in the metadata.
If a tag was present, its value is overwritten.
If the tag was not present, one is created and its value is set::

  >>> engine.metadata[key] = value

The EXIF data may optionally embed a thumbnail in the JPEG or TIFF format.
The thumbnail can be accessed, set from a JPEG file or buffer, saved to disk and
erased::

  >>> thumb = engine.metadata.exif_thumbnail
  >>> thumb.set_from_file('/tmp/thumbnail.jpg')
  >>> thumb.write_to_file('/tmp/copy')
  >>> thumb.erase()
  >>> engine.metadata.write()



Installation
------------

Pyexiv2 depends on the following libraries:

 * boost.python (http://www.boost.org/libs/python/doc/index.html)
 * exiv2 (http://www.exiv2.org/)


On OSX you can use homebrew to install the dependencies::

    brew install boost --with-python
    brew install boost-python
    brew install exiv2

    pip install git+https://github.com/escaped/pyexiv2.git

If you are updating thumbor and already have an existing virtualenv, then you have to recreate it.
If you have both a System Python and a Homebrew Python with the same version, then make sure
the Virtualenv uses the Homebrew Python binary.

On Linux Pyexiv2 can be installed with apt-get:

    apt-get install python-pyexiv2


pyexiv2.metadata API reference
------------------------------

.. module:: pyexiv2.metadata
.. autoclass:: ImageMetadata
   :members: from_buffer, read, write, dimensions, mime_type,
             exif_keys, iptc_keys, iptc_charset, xmp_keys,
             __getitem__, __setitem__, __delitem__,
             comment, previews, copy, buffer


Currently PyExiv is deprecated in favor of GExiv. However, it is really difficult
to install GExiv with Python on a non-Ubuntu system. Therefore Pyexiv2 is used.
