# -*- coding: utf8 -*-

from thumbor.loaders import LoaderResult
from thumbor.result_storages import ResultStorageResult
from thumbor.utils import logger, EXTENSION

class Media(object):
    def __init__(self, buffer=None, is_valid=True, metadata={}, errors=[]):
        self.buffer = buffer
        self.metadata = metadata
        self.errors = errors
        self.is_valid = True

    @classmethod
    def from_result(self, result):

        media = None

        if isinstance(result, Media):
            media = result

        elif isinstance(result, LoaderResult):
            media = Media(result.buffer, result.successful)

            if not media.is_valid:
                media.errors.push(result.error)

        elif isinstance(result, ResultStorageResult):
            media = Media(result.buffer, result.successful)

            if not media.is_valid:
                media.errors.push(result.error)
        else:
            media = Media(result)

        if not media.buffer:
            media.is_valid = False

        return media

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

        return mime

    def __len__(self):
        return len(self.buffer)
