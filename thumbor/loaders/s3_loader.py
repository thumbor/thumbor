# coding: utf-8

from boto.s3.connection import S3Connection
from boto.s3.bucket import Bucket
from boto.s3.key import Key

connection = None

def _get_bucket(url):
    #first item in URL
    arr = url.lstrip('/').split('/',1)
    return arr[0],arr[1]

def _validate_bucket(context,bucket):
    if not context.config.S3_ALLOWED_BUCKETS:
        return True

    for allowed in context.config.S3_ALLOWED_BUCKETS:
        #s3 is case sensitive
        if allowed == bucket:
            return True

    return False

def load(context, url, callback):
    
    if context.config.S3_LOADER_BUCKET:
        bucket = context.config.S3_LOADER_BUCKET
    else:
        bucket,url = _get_bucket(url)
        if not _validate_bucket(context,bucket):
            return callback(None)

    conn = connection
    if conn is None:
        #Store connection not bucket
        conn = S3Connection(
            context.config.AWS_ACCESS_KEY,
            context.config.AWS_SECRET_KEY,
            suppress_consec_slashes=context.config.S3_LOADER_SUPPRESS_SLASHES
        )

    bucketLoader = Bucket(
        connection=conn,
        name=bucket
    )

    if context.config.S3_LOADER_SUPPRESS_SLASHES:
        file_key = bucketLoader.get_key(url)
    else:
        """
            BUG IN BOTO
            When the first character of a key name is a / boto will generate 
            invalid signing keys with suppress_consec_slashes=False
        """
        if url[0] == "/":
            file_key = bucketLoader.get_key(url[1:])
        else:
            file_key = bucketLoader.get_key(url)

    if not file_key:
        return callback(None)

    return callback(file_key.read())