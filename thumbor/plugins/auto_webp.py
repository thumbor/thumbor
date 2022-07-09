from thumbor.plugins import BaseImagingHandlerPlugin
from thumbor.utils import is_animated_gif, logger
from thumbor.config import Config


Config.define(
    "AUTO_WEBP",
    False,
    "Specifies whether WebP format should be used automatically if the request accepts it "
    "(via Accept header)",
    "Imaging",
)


class ImagingHandlerPlugin(BaseImagingHandlerPlugin):
    def supports_auto_webp(self, context):
        return (
            context.config.AUTO_WEBP
            and not context.request.engine.is_multiple()
            and context.request.engine.can_convert_to_webp()
        )

    def is_webp(self, context):
        return (
            self.supports_auto_webp(context)
            and "webp" in context.request.accept_formats
        )

    async def initialize_request(self, next_fn, handler, **kwargs):
        await next_fn(**kwargs)
        if self.context.config.AUTO_WEBP:
            if "webp" not in self.context.request.accept_formats:
                if "image/webp" in handler.request.headers.get("Accept", ""):
                    self.context.request.accept_formats.append("webp")

    def define_image_extension(
        self, next_fn, handler, context, image_extension
    ):
        if image_extension is None and self.is_webp(context):
            image_extension = ".webp"
            logger.debug(
                "Image format set by AUTO_WEBP as %s.", image_extension
            )
        return next_fn(context, image_extension)

    async def write(self, next_fn, handler, buffer, content_type):
        context = self.context
        should_vary = (
            # auto-convert configured?
            context.config.AUTO_WEBP
            # we have image (not video)
            and content_type.startswith("image/")
            # our image is not animated gif
            and not is_animated_gif(buffer)
        )
        if should_vary and "webp" not in context.request.vary_formats:
            context.request.vary_formats.append("webp")
        return await next_fn(buffer, content_type)
