# Custom Storages

If the built-in storages do not suit your needs, you can always implement your
own storage and use it in the **STORAGE** configuration.

Create a class called Storage that inherits from BaseStorage in your module. See
`thumbor/storages/file_storage.py` in the
[thumbor repository](https://github.com/thumbor/thumbor) for an example.
