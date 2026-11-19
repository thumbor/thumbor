# Image Metadata

Thumbor reads the EXIF of the source image with
[Pillow](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Exif)
and makes it available in `engine.metadata`, as a `PIL.Image.Exif` object.

The EXIF is read the first time `engine.metadata` is asked for, not when the
image is loaded. `engine.metadata` is `None` when the image has no EXIF, and
also when the EXIF it has is not TIFF data, which thumbor does not read.

## Reading metadata

The tags of the first directory are the items of the object, by their number:

```pycon
>>> dict(engine.metadata)
{296: 2, 34665: 216, 271: 'Canon', 272: 'Canon EOS 5D Mark III', 305: 'Adobe Photoshop Lightroom 4.4 (Macintosh)', 306: '2016:06:24 14:45:44', 282: 300.0, 283: 300.0}
```

`PIL.ExifTags` has the names of the tags and of the other directories:

```pycon
>>> from PIL import ExifTags
>>> engine.metadata[ExifTags.Base.Model]
'Canon EOS 5D Mark III'
>>> details = engine.metadata.get_ifd(ExifTags.IFD.Exif)
>>> details[ExifTags.Base.DateTimeOriginal]
'2016:06:23 13:18:05'
>>> float(details[ExifTags.Base.ExposureTime])
0.01
```

See the
[Pillow documentation](https://pillow.readthedocs.io/en/stable/reference/ExifTags.html)
for the tags and directories it knows.

## Writing metadata

Thumbor writes EXIF to the image it returns when `PRESERVE_EXIF_INFO` is
enabled, and what it writes is `engine.exif`, the EXIF of the source as bytes.
Changing `engine.metadata` does not change `engine.exif`. Code that changes a
tag has to give the engine the bytes of the changed EXIF:

```pycon
>>> engine.metadata[ExifTags.Base.Artist] = "thumbor"
>>> details = engine.metadata.get_ifd(ExifTags.IFD.Exif)
>>> details[ExifTags.Base.DateTimeOriginal] = "2016:06:23 13:18:05"
>>> engine.exif = engine.metadata.tobytes()
```

`engine.metadata` is `None` for an image without EXIF, which takes the bytes of
a new object:

```pycon
>>> from PIL import Image
>>> exif = Image.Exif()
>>> exif[ExifTags.Base.Artist] = "thumbor"
>>> engine.exif = exif.tobytes()
```

With `PRESERVE_EXIF_COPYRIGHT_INFO` and without `PRESERVE_EXIF_INFO`, thumbor
does not write `engine.exif`. It writes the Artist, Copyright and DateTime tags
of the EXIF the source has, or the whole of that EXIF when it is damaged and
the tags cannot be read.

Pillow does not write everything it reads:

- The thumbnail and its directory (`ExifTags.IFD.IFD1`) are not written.
- Before Pillow 11.1, a directory that the EXIF did not have is not written.
- From Pillow 11.1 to 12.3, `tobytes()` raises `struct.error` once
  `get_ifd(ExifTags.IFD.IFD1)` has been called on the object, so take the
  bytes before reading that directory.

## Other metadata

`engine.metadata` has the EXIF of the image and nothing else. With the PIL
engine, the XMP packet of a JPEG, PNG, WebP, TIFF, AVIF or HEIF source is in
the `info` of the image, as the bytes the source has:

```pycon
>>> engine.image.info.get("xmp")
b'<x:xmpmeta xmlns:x="adobe:ns:meta/">...</x:xmpmeta>'
```

Up to thumbor 7.3.0, with pyexiv2 installed, `engine.metadata` was a
`pyexiv2.ImageMetadata`, which held the XMP and the IPTC of the image as
well.

## Upgrading from the piexif dictionary

From thumbor 7.3.1 to 7.8.0 `engine.metadata` was the dictionary that
`piexif.load` returns, filled when the image was loaded, and piexif was
installed with thumbor. Code that imports piexif now has to depend on it
itself, and code that reads or writes `engine.metadata` has to change:

| piexif dictionary          | `PIL.Image.Exif`                              |
| -------------------------- | --------------------------------------------- |
| `metadata["0th"][tag]`     | `metadata[tag]`                               |
| `metadata["Exif"][tag]`    | `metadata.get_ifd(ExifTags.IFD.Exif)[tag]`    |
| `metadata["GPS"][tag]`     | `metadata.get_ifd(ExifTags.IFD.GPSInfo)[tag]` |
| `metadata["Interop"][tag]` | `metadata.get_ifd(ExifTags.IFD.Interop)[tag]` |
| `metadata["1st"][tag]`     | `metadata.get_ifd(ExifTags.IFD.IFD1)[tag]`    |
| `metadata["thumbnail"]`    | nothing: Pillow does not give the thumbnail   |
| `piexif.dump(metadata)`    | `metadata.tobytes()`                          |

The values differ too:

- Text comes as `str` where piexif gave `bytes`.
- A rational comes as a number where piexif gave a pair of integers.
- Values of the `BYTE` type come as `bytes` where piexif gave an integer or a
  tuple of integers: the GPS altitude reference is `b"\x01"`, not `1`, and the
  GPS version is `b"\x02\x02\x00\x00"`, not `(2, 2, 0, 0)`.
- Before Pillow 13, `get_ifd(ExifTags.IFD.Interop)` raises `KeyError` for EXIF
  without that directory, where piexif gave an empty dictionary.
- `piexif.dump` wrote the thumbnail and its directory back, and `tobytes()`
  does not.
