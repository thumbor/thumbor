# -*- coding: utf8 -*-

from thumbor.engines import BaseEngine

class Media(object):
    def __init__(self, buffer=None, is_valid=True, metadata={}, errors=[]):
        self.buffer = buffer
        self.metadata = metadata
        self.errors = errors
        self.is_valid = True

    @property
    def content_type(self):
        return self.metadata.get('ContentType', None)

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
        return self.metadata['ContentType'] if 'ContentType' in self.metadata else BaseEngine.get_mimetype(self.buffer)

    def __len__(self):
        return self.metadata['ContentLength'] if 'ContentLength' in self.metadata else len(self.buffer)
