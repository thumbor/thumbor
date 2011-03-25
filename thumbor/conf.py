
# the domains that can have theyre images resized
ALLOWED_SOURCES = ['s.glbimg.com', 'www.globo.com', 'ego.globo.com']

# the max width of the resized image
#MAX_WIDTH = 1280

# the max height of the resized image
#MAX_HEIGHT = 800

#QUALITY = 80

LOADER = 'thumbor.loaders.http_loader'

STORAGE = 'thumbor.storages.file_storage'

ENGINE = 'thumbor.engines.pil'

#MAGICKWAND_PATH = []

#FILTERS = ['thumbor.filters.face_filter']

#FACE_FILTER_CASCADE_FILE = 'haarcascade_frontface_alt.xml'
