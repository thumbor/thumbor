# pylint: disable=unused-argument
from __future__ import annotations

import asyncio
from functools import wraps, partial
from typing import TYPE_CHECKING, Any, Optional, Callable

if TYPE_CHECKING:
    from thumbor.handlers import ContextHandler
    from thumbor.handlers.imaging import ImagingHandler
    from thumbor.context import Context
    from thumbor.loaders import Loader, LoaderResult
    from thumbor.storages import BaseStorage
    from thumbor.engines import BaseEngine
    from thumbor.result_storages import ResultStorageResult
    import PIL.Image


BUILTIN_PLUGINS = [
    "thumbor.plugins.auto_webp",
]


_PLUGIN_METHOD_MAP = {}


def func_is_async(func):
    while isinstance(func, partial):
        func = func.func
    if isinstance(func, PluginMethodWrapper):
        return func.is_async
    return asyncio.iscoroutinefunction(func)


class BasePluginType(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        super_new = super().__new__

        plugin_type = attrs.get("plugin_type")
        for base in bases:
            if plugin_type is not None:
                break
            plugin_type = getattr(base, "plugin_type", None)

        if plugin_type is None:
            return super_new(cls, name, bases, attrs, **kwargs)

        if plugin_type not in _PLUGIN_METHOD_MAP:
            _PLUGIN_METHOD_MAP[plugin_type] = {}

        method_map = _PLUGIN_METHOD_MAP[plugin_type]

        for k, val in attrs.items():
            if hasattr(val, "plugin_method_target"):
                method_map[val.plugin_method_target] = k

        return super_new(cls, name, bases, attrs, **kwargs)


class PluginMethodWrapper:
    def __init__(self, is_async, method_name, plugin_type):
        self.is_async = is_async
        self.method_name = method_name
        self.plugin_type = plugin_type

    def __set_name__(self, cls, attr):
        self.attr = attr
        self.cls = cls

    def __get__(self, obj, obj_type=None):
        func = self.async_call if self.is_async else self.sync_call
        wrapped_func = partial(func, obj)
        return plugin_wrap(
            wrapped_func,
            method_name=self.method_name,
            plugin_type=self.plugin_type,
            instance=obj,
        )

    def sync_call(self, instance, *args, **kwargs):
        super_cls = super(self.cls, instance)
        func = getattr(super_cls, self.attr)
        return func(*args, **kwargs)

    async def async_call(self, instance, *args, **kwargs):
        super_cls = super(self.cls, instance)
        func = getattr(super_cls, self.attr)
        return await func(*args, **kwargs)


def plugin_wrap(func, method_name, plugin_type, instance):
    modules = instance.context.modules
    plugins = getattr(modules, f"{plugin_type}_plugins")
    plugin_funcs = reversed(
        [
            getattr(p, method_name)
            for p in plugins
            if getattr(p, method_name, None)
        ]
    )

    next_fn = func
    for plugin_fn in plugin_funcs:
        next_fn = partial(plugin_fn, next_fn, instance)

    if func_is_async(func):

        async def wrapper(*args, **kwargs):
            return await next_fn(*args, **kwargs)

    else:

        def wrapper(*args, **kwargs):
            return next_fn(*args, **kwargs)

    return wraps(func)(wrapper)


def pluggable_class(plugin_type):
    def wrapper(cls):
        method_map = _PLUGIN_METHOD_MAP.get(plugin_type) or {}
        name = f"{cls.__name__}Wrapped"
        attrs = {}
        for target_attr, method_name in method_map.items():
            func = getattr(cls, target_attr, None)
            if func:
                attrs[target_attr] = PluginMethodWrapper(
                    is_async=func_is_async(func),
                    method_name=method_name,
                    plugin_type=plugin_type,
                )
        return type(name, (cls,), attrs)

    return wrapper


def plugin_method(func=None, target=None):
    if func is None:
        return partial(plugin_method, target=target)
    func.plugin_method_target = target or func.__name__
    return func


class BasePlugin(metaclass=BasePluginType):
    def __init__(self, context):
        self.context = context


class BaseImagingHandlerPlugin(BasePlugin):
    plugin_type = "imaging_handler"

    @plugin_method
    async def initialize_request(
        self,
        next_fn: Callable[..., None],
        handler: ImagingHandler,
        **kwargs: dict[str, Any],
    ) -> None:
        return await next_fn(**kwargs)

    @plugin_method
    async def fetch(
        self,
        next_fn: Callable[[Context, BaseStorage, str], Optional[bytes]],
        handler: ImagingHandler,
        context: Context,
        storage: BaseStorage,
        url: str,
    ) -> Optional[bytes]:
        buffer = await next_fn(context, storage, url)
        return buffer

    @plugin_method
    async def load(
        self,
        next_fn: Callable[[Context, Loader, str], LoaderResult],
        handler: ImagingHandler,
        context: Context,
        loader: Loader,
        path: str,
    ) -> LoaderResult:
        loader_result = await next_fn(context, loader, path)
        return loader_result

    @plugin_method
    async def post_transform(
        self, next_fn: Callable[[], None], handler: ContextHandler
    ) -> None:
        return await next_fn()

    @plugin_method
    def define_image_extension(
        self,
        next_fn: Callable[[Context, Optional[str]], str],
        handler: ImagingHandler,
        context: Context,
        image_extension: Optional[str],
    ) -> str:
        return next_fn(context, image_extension)

    @plugin_method
    def execute(
        self,
        next_fn: Callable[[Context, str, int | None], bytes],
        handler: ImagingHandler,
        context: Context,
        image_extension: str,
        quality: int | None,
    ) -> bytes:
        return next_fn(context, image_extension, quality)

    @plugin_method
    def optimize(
        self,
        next_fn: Callable[[Context, str, bytes, int], bytes],
        handler: ImagingHandler,
        context: Context,
        image_extension: str,
        results: bytes,
        quality: int,
    ) -> bytes:
        results = next_fn(context, image_extension, results, quality)
        return results

    @plugin_method(target="_write_results_to_client")
    async def write(
        self,
        next_fn: Callable[[bytes, str], None],
        handler: ImagingHandler,
        buffer: bytes,
        content_type: str,
    ) -> None:
        return await next_fn(buffer, content_type)

    @plugin_method(target="_cleanup")
    def cleanup(
        self, next_fn: Callable[[], None], handler: ImagingHandler
    ) -> None:
        return next_fn()


class BaseResultStoragePlugin(BasePlugin):
    plugin_type = "result_storage"

    @plugin_method
    def normalize_path(
        self, next_fn: Callable[[str], str], instance: Any, path: str
    ) -> str:
        return next_fn(path)

    @plugin_method
    def _normalize_path(
        self, next_fn: Callable[[str], str], instance: Any, path: str
    ) -> str:
        return self.normalize_path(next_fn, instance, path)

    @plugin_method
    def normalize_path_legacy(
        self, next_fn: Callable[[str], str], instance: Any, path: str
    ) -> str:
        return next_fn(path)


class BaseUploadHandlerPlugin(BasePlugin):
    plugin_type = "upload_handler"

    @plugin_method
    def get_engine(
        self,
        next_fn: Callable[[bytes], BaseEngine],
        handler: ContextHandler,
        body: bytes,
    ) -> BaseEngine:
        return next_fn(body)


class BaseResourceHandlerPlugin(BasePlugin):
    plugin_type = "resource_handler"

    @plugin_method
    def get_engine(
        self,
        next_fn: Callable[[bytes], BaseEngine],
        handler: ContextHandler,
        body: bytes,
    ) -> BaseEngine:
        return next_fn(body)


class BaseEnginePlugin(BasePlugin):
    plugin_type = "engine"

    @plugin_method
    def read(
        self,
        next_fn: Callable[[Optional[str], Optional[int]], bytes],
        engine: BaseEngine,
        extension: Optional[str],
        quality: Optional[int],
    ) -> bytes:
        return next_fn(extension, quality)

    @plugin_method
    def load(
        self,
        next_fn: Callable[[bytes, Optional[str]], None],
        engine: BaseEngine,
        results: bytes | ResultStorageResult,
        extension: Optional[str],
    ) -> None:
        return next_fn(results, extension)

    @plugin_method
    def create_image(
        self,
        next_fn: Callable[[bytes], PIL.Image.Image],
        engine: BaseEngine,
        buffer: bytes,
    ) -> PIL.Image.Image:
        return next_fn(buffer)


class BaseTransformerPlugin(BasePlugin):
    plugin_type = "transformer"
