# -*- coding: utf8 -*-

from thumbor.loaders import LoaderResult
from thumbor.result_storages import ResultStorageResult
from thumbor.utils import logger, EXTENSION

class Media(object):
    """
    This object holds the image and its meta data.
    """
    def __init__(self, buffer=None, metadata=None, mimetype=None, errors=None):
        self.buffer = buffer
        self.metadata = metadata or {}
        self.errors = errors or []
        self._mimetype = mimetype

    @classmethod
    def from_result(self, result, mimetype=None):
        media = None

        if isinstance(result, Media):
            media = result

        elif isinstance(result, LoaderResult) or isinstance(result, ResultStorageResult):
            media = Media(result.buffer)

            if not media.is_valid:
                media.errors.append(result.error)
        else:
            media = Media(result, mimetype=mimetype)

        return media

    @property
    def is_valid(self):
        if not self.buffer:
            return False

        if self.errors:
            return False

        return True

    @property
    def last_modified(self):
        '''
        Retrieves last_updated metadata if available
        '''
        return self.metadata.get('LastModified', None)

    @property
    def file_extension(self):
        return EXTENSION.get(self.mime, '.jpg')

    @property
    def mime(self):
        if self._mimetype:
            return self._mimetype
        mime = None

        # magic number detection
        if self.buffer.startswith('GIF8'):
            mime = 'image/gif'
        elif self.buffer.startswith('\x89PNG\r\n\x1a\n'):
            mime = 'image/png'
        elif self.buffer.startswith('\xff\xd8'):
            mime = 'image/jpeg'
        elif self.buffer.startswith('WEBP', 8):
            mime = 'image/webp'
        elif self.buffer.startswith('\x00\x00\x00\x0c'):
            mime = 'image/jp2'
        elif self.buffer.startswith('\x00\x00\x00 ftyp'):
            mime = 'video/mp4'
        elif self.buffer.startswith('\x1aE\xdf\xa3'):
            mime = 'video/webm'

        if not mime:
            logger.debug(
                '[Media] Unknown mime type for header: {header}'.format(
                    header=self.buffer[0:10]
                )
            )
        else:
            self._mimetype = mime

        return mime

    def __len__(self):
        if self.is_valid:
            return len(self.buffer)
        else:
            return 0
