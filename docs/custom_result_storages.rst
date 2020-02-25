Custom Result Storages
======================

In order to implement your own result storage, you have to implement a
few methods. A reference implementation can be found at the `File
Storage <https://github.com/thumbor/thumbor/blob/master/thumbor/result_storages/file_storage.py>`__.

The required methods are ``put``, ``get``, ``validate_path`` and
``normalize_path``.
