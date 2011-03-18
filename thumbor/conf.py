
# the domains that the request for thumbnails will come. They can use the service
#ALLOWED_DOMAINS = ['localhost', ]

# the domains that can have theyre images resized
#ALLOWED_SOURCES = ['s.glbimg.com', 'www.globo.com']

# the max width of the resized image
#MAX_WIDTH = 1280

# the max height of the resized image
#MAX_HEIGHT = 800

#QUALITY = 80

#LOADER = 'thumbor.loaders.http_loader'

STORAGE = 'thumbor.storages.redis_storage'

#ENGINE = 'thumbor.engines.pil'

#MAGICKWAND_PATH = []