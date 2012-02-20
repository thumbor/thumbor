#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

import mimetypes
from cStringIO import StringIO 
from os.path import abspath, join, dirname, exists
from datetime import datetime

from pyvows import Vows, expect
from tornado_pyvows.context import TornadoHTTPContext

from thumbor.app import ThumborServiceApp
from thumbor.config import Config
from thumbor.importer import Importer
from thumbor.context import Context

storage_path = '/tmp/thumbor-vows/storage'
crocodile_file_path = abspath(join(dirname(__file__), 'crocodile.jpg'))

def get_content_type(filename): 
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream' 

"adapted from: http://code.activestate.com/recipes/146306/" 
def encode_multipart_formdata(fields, files): 
    """ 
    fields is a sequence of (name, value) elements for regular form 
fields. 
    files is a sequence of (name, filename, value) elements for data 
to be uploaded as files 
    Return (content_type, body) ready for httplib.HTTP instance 
    """ 
    BOUNDARY = '-------tHISiStheMulTIFoRMbOUNDaRY' 
    CRLF = '\r\n' 
    L = [] 
    for (key, value) in fields: 
        L.append('--' + BOUNDARY) 
        L.append('Content-Disposition: form-data; name="%s"' % key) 
        L.append('') 
        L.append(value) 

    for (key, filename, value) in files: 
        L.append('--' + BOUNDARY) 
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename)) 
        L.append('Content-Type: %s' % get_content_type(filename)) 
        L.append('') 
        L.append(value) 
    L.append('--' + BOUNDARY + '--') 
    L.append('') 
    b = StringIO() 
    for l in L: 
        b.write(l) 
        b.write(CRLF) 
    body = b.getvalue() 
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY 
    return content_type, body 

@Vows.batch
class Upload(TornadoHTTPContext):
    def get_app(self):
        cfg = Config()
        cfg.ENABLE_ORIGINAL_PHOTO_UPLOAD = True
        cfg.ORIGINAL_PHOTO_STORAGE = 'thumbor.storages.file_storage'
        cfg.FILE_STORAGE_ROOT_PATH = storage_path

        ctx = Context(None, cfg, Importer(cfg))
        application = ThumborServiceApp(ctx)
        return application

    class WhenPutting(TornadoHTTPContext):
        def __put(self, path, data={}, files=[]):
            multipart_data = encode_multipart_formdata(data, files)
            return self.fetch(path,
                method="PUT",
                body=multipart_data[1],
                headers={
                    'Content-Type': multipart_data[0]
                },
                allow_nonstandard_methods=True)

        def topic(self):
            with open(crocodile_file_path, 'r') as croc:
                image = ('image', u'crocodile.jpg', croc.read()) 
            response = self.__put('/upload', {}, [image])
            return (response.code, response.body)

        class StatusCode(TornadoHTTPContext):
            def topic(self, response):
                return response[0]

            def should_not_be_an_error(self, topic):
                expect(topic).to_equal(200)

        class Body(TornadoHTTPContext):
            def topic(self, response):
                return response[1]

            def should_be_in_right_path(self, topic):
                path = join(storage_path, datetime.now().strftime('%Y/%M/%d'), 'crocodile.jpg')
                expect(topic).to_equal(path)
                expect(exists(path)).to_be_true()

