Custom Routers
==============

Routers are responsible for adding new routes to thumbor. Even thumbor's own routes (other than the default image crop route)
are added via routers (healthcheck, blacklist...).

Built-in Routers
----------------

Thumbor comes with three routers built-in:

* ``thumbor.routers.healthcheck.HealthcheckRouter``;
* ``thumbor.routers.blacklist.BlacklistRouter``;
* ``thumbor.routers.upload.UploadRouter``.

The healthcheck router adds a route at whatever is in the ``HEALTHCHECK_ROUTE`` config.

The blacklist router adds a ``/blacklist`` route that can be used to blacklist images.

The upload router adds two routes for uploading and retrieving uploaded images.

Writing a new Router
--------------------

Creating your own router is as simple as creating a new file with a class that inherits from ``thumbor.routers.base.BaseRouter``:

.. code:: python

   from typing import List, Optional, cast

   from my.handlers.index import IndexHandler
   from thumbor.routers.base import BaseRouter, Route


   class MyRouter(BaseRouter):
       def get_routes(self) -> Optional[List[Route]]:
           something_enabled = cast(bool, self.context.config.SOMETHING_ENABLED)
           if not something_enabled:
               return []

           return [Route(r"/my-route/?", IndexHandler, {"context": self.context})]

After your router can be imported with python (check with ``python -c 'import <<your router module>>'``), just add it to thumbor's config:

.. code:: python

   from thumbor.routers import BUILTIN_ROUTERS

   # You need to put the full name for your class: module_name.class_name
   # Two things worth noticing here:
   # 1) The route order indicates precedence, so whatever matches first will be executed;
   # 2) Please do not forget thumbor's built-ins or you'll kill thumbor functionality.
   ROUTERS = BUILTIN_ROUTERS + [
       "my.router.MyRouter',
   ]
