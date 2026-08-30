# Custom Image Optimizers

An optimizer receives the bytes produced by the engine and may return an
optimized replacement. Add optimizer modules to `OPTIMIZERS` in execution
order:

```python
OPTIMIZERS = [
    "my_package.optimizer",
]
```

Each module must expose a class named `Optimizer`. Subclass
`thumbor.optimizers.BaseOptimizer`:

```python
from thumbor.optimizers import BaseOptimizer


class Optimizer(BaseOptimizer):
    def should_run(self, image_extension, image_buffer):
        return image_extension in {".jpg", ".jpeg"}

    def optimize(self, image_buffer, input_file, output_file):
        # Write the optimized bytes to output_file.
        ...
```

The base `run_optimizer()` implementation checks `should_run()`, creates input
and output temporary files, calls `optimize()` and returns the bytes written to
the output file. Override `run_optimizer(image_extension, buffer)` instead when
the optimizer works in memory or needs a different process lifecycle.

Return the original buffer when optimization is skipped or fails safely. A
non-`None` return value becomes the input to the next configured optimizer, so
the order in `OPTIMIZERS` is significant. Thumbor instantiates each optimizer
with the request context, available as `self.context`.

Optimizers run synchronously while the response is being produced. Bound
external-process execution time and avoid leaving child processes or temporary
files behind. See `thumbor.optimizers.jpegtran.Optimizer` for an in-memory
`run_optimizer()` implementation.
