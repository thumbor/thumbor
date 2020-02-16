Custom Image Loaders
====================

If thumbor image loaders do not meet your needs you can implement a new
image loader.

The structure of the module you should implement can be seen in the http
loader at
`<https://github.com/thumbor/thumbor/blob/master/thumbor/loaders/http_loader.py>`_.

The only required method to implement is the one that receives the
portion of the URI that has the original image path, named **load**.
This method also receives a callback and should call the callback with
the results of reading the image.

Another example can be seen in the filesystem loader at
`<https://github.com/thumbor/thumbor/blob/master/thumbor/loaders/file_loader.py>`_.

You can optionally implement a validate(URI) method that thumbor will
call to make sure that your loader can accept the user required URI.
