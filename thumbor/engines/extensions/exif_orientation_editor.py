import struct
from io import BytesIO

PREFIXES = [
    b"MM\x00\x2a",  # Valid TIFF header with big-endian byte order
    b"II\x2a\x00",  # Valid TIFF header with little-endian byte order
    b"MM\x2a\x00",  # Invalid TIFF header, assume big-endian
    b"II\x00\x2a",  # Invalid TIFF header, assume little-endian
]

EXIF_HEADER = b"Exif\x00\x00"


class ExifOrientationEditor:
    _endian = "<"
    _offset = None

    def __init__(self, data):
        if data[:6] != EXIF_HEADER:
            raise SyntaxError(f"not a TIFF file (header {data[:4]} not valid)")

        # Skip 6 bytes of exif header to simplify seeks in ImageFileDirectory
        self.exif_buffer = BytesIO(data[6:])

        header = self._read_header()
        self._find_orientation_offset(header)

    def _read_header(self):
        header = self.exif_buffer.read(8)

        if header[:4] not in PREFIXES:
            raise SyntaxError(f"not a TIFF file (header {header} not valid)")
        prefix = header[:2]
        if prefix == b"MM":
            self._endian = ">"
        elif prefix == b"II":
            self._endian = "<"
        else:
            raise SyntaxError("not a TIFF IFD")

        return header

    def _find_orientation_offset(self, header):
        (ifd_offset,) = self._unpack("L", header[4:])
        self.exif_buffer.seek(ifd_offset)

        # Read tag directory
        for _ in range(self._unpack("H", self.exif_buffer.read(2))[0]):
            # Each tag is 12 bytes. HHL4s = tag, type, count, data
            # Read tag and ignore the rest
            (tag,) = self._unpack("H10x", self.exif_buffer.read(12))
            if tag == 0x0112:  # Orientation tag
                self._offset = (
                    self.exif_buffer.tell() - 4
                )  # Back 4 bytes to the start of data
                break

    def _unpack(self, fmt, data):
        return struct.unpack(self._endian + fmt, data)

    def get_orientation(self):
        if self._offset is None:
            return None

        self.exif_buffer.seek(self._offset)
        return self._unpack("H", self.exif_buffer.read(2))[0]

    def set_orientation(self, value):
        if self._offset is None:
            return

        self.exif_buffer.seek(self._offset)
        self.exif_buffer.write(struct.pack(self._endian + "H", value))

    def tobytes(self):
        self.exif_buffer.seek(0)
        return EXIF_HEADER + self.exif_buffer.read()
