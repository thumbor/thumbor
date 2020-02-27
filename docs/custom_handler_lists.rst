Custom Handler Lists
====================

Handler Lists are responsible for adding new handlers to thumbor.

Even thumbor's own handlers (other than the default image crop handler) are added using handler lists(healthcheck, blacklist...).

Built-in Handler Lists
----------------------

Thumbor comes with three handler lists built-in:

* ``thumbor.handler_lists.healthcheck``;
* ``thumbor.handler_lists.blacklist``;
* ``thumbor.handler_lists.upload``.

The healthcheck handler list adds a handler at whatever is in the ``HEALTHCHECK_ROUTE`` config.

The blacklist handler list adds a ``/blacklist`` handler that can be used to blacklist images.

The upload handler list adds two handlers for uploading and retrieving uploaded images.

Writing a new Handler List
--------------------------

Creating your own handler list is as simple as creating a new module with a `get_handlers` method:

.. code:: python

   from typing import Any, cast

   from thumbor.handler_lists import HandlerList

   from my.handlers.index import IndexHandler

   def get_handlers(context: Any) -> HandlerList:
       something_enabled = cast(bool, self.context.config.SOMETHING_ENABLED)
       if not something_enabled:
           return []
       return [
           (r"/my-url/?", IndexHandler, {"context": self.context}),
       ]

After your handler list can be imported with python (check with ``python -c 'import <<your handler list module>>'``),
just add it to thumbor's config:

.. code:: python

   from thumbor.handler_lists import BUILTIN_HANDLERS

   # Two things worth noticing here:
   # 1) The handler list order indicates precedence, so whatever matches first will be executed;
   # 2) Please do not forget thumbor's built-ins or you'll kill thumbor functionality.
   HANDLER_LISTS = BUILTIN_HANDLERS + [
       "my.handler_list',
   ]
