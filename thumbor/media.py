# -*- coding: utf8 -*-

from thumbor.loaders import LoaderResult
from thumbor.result_storages import ResultStorageResult

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
    def content_type(self):
        return self.mime

    @property
    def last_modified(self):
        '''
        Retrieves last_updated metadata if available
        '''
        return self.metadata.get('LastModified', None)

    @property
    def mime(self):
        '''
        Retrieves mime metadata if available
        '''
        return self.metadata.get('ContentType')

    def __len__(self):
        return len(self.buffer)
