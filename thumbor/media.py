# -*- coding: utf8 -*-
from __future__ import unicode_literals, absolute_import
from thumbor.loaders import LoaderResult
from thumbor.utils import logger, EXTENSION


class Media(object):
    """
    This object holds the image and its metadata.
    """
    def __init__(self, buffer=None, metadata=None, mimetype=None, errors=None):
        """
        Constructor
        :param buffer: The image buffer. (Also buffer for JSON result)
        :type buffer: Binary String
        :param metadata: All metadata for the media file. (Not just EXIF)
        :type metadata: dict
        :param mimetype: Mime-Type of the buffer content
        :type mimetype: String
        :param errors: List of errors that occured when loading or processing media
        :type errors: Array of Strings
        """
        self.buffer = buffer
        self.metadata = metadata or {}
        self.errors = errors or []
        self._mimetype = mimetype
        # store debug and tracing information
        self._info = {
            'creator': 'unknown',
            'changed_by': []
        }
        self.engine = None  # is this really necessary?
        self.normalized = False
        self.successful = False

    @classmethod
    def from_result(self, result):
        """
        Compatibility Factory. Creates a Media instance from a Result.
        This should only be necessary for 3rd party storages.
        :param result: The Result instance
        :type result: Result
        :return: Media instance
        :rtype: Media
        """

        # If this is already a Media instance, pass it on.
        if isinstance(result, Media):
            return result

        elif isinstance(result, LoaderResult):
            # try to get the mimetype from the Result
            mime = getattr(result, 'mime', None)
            media = Media(result.buffer, mimetype=mime)
            media._info['creator'] = '{}.{}'.format(
                result.__module__, result.__class__.__name__)

            if not media.is_valid:
                media.errors.append(result.error)
            return media

        else:
            raise AttributeError('Media.from_result should be called with a '
                                 'Result instance as first argument.')

    @property
    def is_valid(self):
        if self.buffer is None:
            logger.debug('Media objects contains no buffer.')
            return False

        if self.errors:
            logger.debug('Media objects contains errors.')
            return False

        return True

    @property
    def last_modified(self):
        """
        Retrieves last_updated metadata if available
        """
        return self.metadata.get('LastModified', None)

    @property
    def file_extension(self):
        return EXTENSION.get(self.mime, '.jpg')

    @property
    def mime(self):
        if self._mimetype:
            return self._mimetype

        mime = ''

        if not self.buffer:
            return mime
        # magic number detection
        if self.buffer.startswith(b'GIF8'):
            mime = 'image/gif'
        elif self.buffer.startswith(b'\x89PNG\r\n\x1a\n'):
            mime = 'image/png'
        elif self.buffer.startswith(b'\xff\xd8'):
            mime = 'image/jpeg'
        elif self.buffer.startswith(b'WEBP', 8):
            mime = 'image/webp'
        elif self.buffer.startswith(b'\x00\x00\x00\x0c'):
            mime = 'image/jp2'
        elif self.buffer.startswith(b'\x00\x00\x00 ftyp'):
            mime = 'video/mp4'
        elif self.buffer.startswith(b'\x1aE\xdf\xa3'):
            mime = 'video/webm'

        if not mime:
            logger.debug(
                b'[Media] Unknown mime type for header: {header}'.format(
                    header=self.buffer[0:10]
                )
            )
        else:
            self._mimetype = mime

        return mime

    @mime.setter
    def mime(self, value):
        if self._mimetype is not None and value != self._mimetype:
            logger.debug('Changed mimetype from {} to {}'
                         .format(self._mimetype, value))
        self._mimetype = value

    def __len__(self):
        if self.is_valid:
            return len(self.buffer)
        else:
            return 0

    @property
    def is_image(self):
        return self.buffer and self.mime and self.mime.startswith('image/')
