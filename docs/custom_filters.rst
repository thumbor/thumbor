Custom Filters
==============

Filters are an easy way to transform images using a pipeline. Creating a new filter is very simple, as we'll see.

The first step is creating a filter class that inherits from ``thumbor.filters.BaseFilter`` and naming it ``Filter``:

.. code:: python

   from thumbor.filters import BaseFilter

   class Filter(BaseFilter):
      pass

The next step is actually implementing the filter. Let's say we want to create
the ``quality(99)`` filter, a filter that takes a ``number`` parameter and
sets the image quality to that parameter.

.. note::
   Yep, this filter already exists and is built-in, but it is simple enough that we can talk on how to do it. Let's get on with it.

.. code:: python

   from thumbor.filters import BaseFilter

   class Filter(BaseFilter):
      @filter_method(BaseFilter.PositiveNumber)
      async def quality(self, value):
         self.context.request.quality = value

Let's analyse it:

- The ``filter_method`` decorator takes as parameters any number of types (more on types below) you want to have as arguments to your filter;
- The filter method should be named according to how you want it to be invoked by thumbor (a.k.a the URL part). In our example, our filter will be invoked with ``quality(99)``;
- The filter method is just an async function that you can do whatever you need with the image.

And that's it, we got our filter. In order to use it, we need to put it in our ``thumbor.conf``:

.. code:: python

   from thumbor.filters import BUILTIN_FILTERS

   FILTERS = BUILTIN_FILTERS + [
      'mylib.filters.quality',
   ]

Available Filter Argument Types
-------------------------------

Each parameter type has a regular expression that matches arguments of the given type, as well as a python type.

For more details on each of the types, check `BaseFilter class in thumbor's codebase <https://github.com/thumbor/thumbor/blob/master/thumbor/filters/__init__.py#L91>`_.

- ``BaseFilter.PositiveNumber``;
- ``BaseFilter.PositiveNonZeroNumber``;
- ``BaseFilter.NegativeNumber``;
- ``BaseFilter.Number``;
- ``DecimalNumber``;
- ``Boolean``;
- ``String``.
