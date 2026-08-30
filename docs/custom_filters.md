# Custom Filters

Filters transform images as part of Thumbor's processing pipeline. A filter
module must expose a class named `Filter` that inherits from
`thumbor.filters.BaseFilter`. Filter methods are asynchronous and must be
decorated with `filter_method`.

The example below implements `quality(99)`, a filter that takes a positive
number and sets the image quality to that value:

```{note}
Yep, this filter already exists and is built-in, but it is simple enough that
we can talk about how to do it. Let's get on with it.
```

```python
from thumbor.filters import BaseFilter, filter_method


class Filter(BaseFilter):
    @filter_method(BaseFilter.PositiveNumber)
    async def quality(self, value):
        self.context.request.quality = value
```

Let's analyse it:

- The `filter_method` decorator takes as parameters any number of types (more on
  types below) you want to have as arguments to your filter;
- The filter method should be named according to how you want it to be invoked
  by thumbor (a.k.a the URL part). In our example, our filter will be invoked
  with `quality(99)`;
- The filter method is just an async function that you can do whatever you need
  with the image.

The `Filter` instance receives the current request context as `self.context`.
The current image engine is available as `self.engine`.

When a metrics backend is enabled, each filter execution emits a
`filter.<filter_name>.time` timing. Successful executions also emit
`filter.<filter_name>.count`, while failed executions emit
`filter.<filter_name>.error`. The `<filter_name>` portion comes from the
decorated method name, so it should stay stable if you rely on dashboards or
alerts.

And that's it, we got our filter. In order to use it, we need to put it in our
`thumbor.conf`:

```python
from thumbor.filters import BUILTIN_FILTERS

FILTERS = BUILTIN_FILTERS + [
    "mylib.filters.quality",
]
```

Each entry in `FILTERS` is the full name of a module, not the full name of the
class. Thumbor imports `Filter` from each configured module. List order and
duplicate entries are preserved.

## Available Filter Argument Types

Each parameter type has a regular expression that matches arguments of the given
type, as well as a python type.

For more details on each type, see `thumbor/filters/__init__.py` in the
[thumbor repository](https://github.com/thumbor/thumbor).

- `BaseFilter.PositiveNumber`;
- `BaseFilter.PositiveNonZeroNumber`;
- `BaseFilter.NegativeNumber`;
- `BaseFilter.Number`;
- `BaseFilter.DecimalNumber`;
- `BaseFilter.Boolean`;
- `BaseFilter.String`.
