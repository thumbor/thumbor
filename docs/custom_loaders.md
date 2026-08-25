# Custom Image Loaders

If thumbor image loaders do not meet your needs you can implement a new image
loader.

The HTTP loader at `thumbor/loaders/http_loader.py` in the
[thumbor repository](https://github.com/thumbor/thumbor) demonstrates the module
structure you should implement.

The only required method to implement is the one that receives the portion of
the URI that has the original image path, named **load**. This method also
receives a callback and should call the callback with the results of reading the
image.

Another example is the filesystem loader at `thumbor/loaders/file_loader.py` in
the [thumbor repository](https://github.com/thumbor/thumbor).

You can optionally implement a validate(URI) method that thumbor will call to
make sure that your loader can accept the user required URI.
