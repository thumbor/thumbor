Custom Storages
===============

If the built-in storages do not suit your needs, you can always
implement your own storage and use it in the **STORAGE**
configuration.

All you have to do is create a class called Storage that inherits from
BaseStorage in your module, as can be seen in
`<https://github.com/thumbor/thumbor/blob/master/thumbor/storages/file_storage.py>`_.
