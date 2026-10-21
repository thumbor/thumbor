# NSXBet Thumbor — Thumbor imaging service with video transcoding
# Fork of https://github.com/thumbor/thumbor
#
# Usage: thumbor -c /etc/thumbor/thumbor.conf -p 8888

# --- Security ---
# SECURITY_KEY can be overridden via env (--use-environment) or secret manager.
ALLOW_UNSAFE_URLS = False

# --- Sources (regexes match hostname; video-engine loader uses http_loader) ---
ALLOWED_SOURCES = [
    r'.*\.nsx\.services',
    r'.*\.nsxbet\.com\.br',
    r'.*\.betnacional\.bet\.br',
]

# --- Loader / Storage ---
LOADER = 'thumbor.loaders.http_loader'
STORAGE = 'thumbor.storages.no_storage'
RESULT_STORAGE = 'thumbor.result_storages.no_storage'

# --- Engine ---
ENGINE = 'thumbor_video_engine.engines.video'
# Non-video files fall back to PIL inside the video engine (IMAGING_ENGINE).
ENGINE_THREADPOOL_SIZE = 4

MAX_PIXELS = 8294400  # 4K: 3840x2160 — guard against decompression bombs

# --- Video engine (thumbor-video-engine) ---
AUTO_WEBP = True  # required for FFMPEG_GIF_AUTO_WEBP (Accept header path)
FFMPEG_GIF_AUTO_WEBP = True
FFMPEG_PATH = '/usr/bin/ffmpeg'
FFPROBE_PATH = '/usr/bin/ffprobe'
FFMPEG_GIF_AUTO_H264 = True
FFMPEG_H264_PRESET = 'medium'
FFMPEG_H264_CRF = 23
# MAX_ANIMATED_GIF_PIXELS: gate gif->gif transcodes (0 = disabled). Set to
# bound memory before enabling heavy gif workloads.
MAX_ANIMATED_GIF_PIXELS = 0

# --- Filters ---
# Video-engine format filter REPLACES builtin thumbor.filters.format
# (must not be listed twice). Rest are the builtin filters.
FILTERS = [
    'thumbor_video_engine.filters.format',
    'thumbor.filters.brightness',
    'thumbor.filters.colorize',
    'thumbor.filters.contrast',
    'thumbor.filters.rgb',
    'thumbor.filters.round_corner',
    'thumbor.filters.quality',
    'thumbor.filters.noise',
    'thumbor.filters.watermark',
    'thumbor.filters.equalize',
    'thumbor.filters.fill',
    'thumbor.filters.sharpen',
    'thumbor.filters.strip_exif',
    'thumbor.filters.strip_icc',
    'thumbor.filters.frame',
    'thumbor.filters.grayscale',
    'thumbor.filters.rotate',
    'thumbor.filters.max_bytes',
    'thumbor.filters.convolution',
    'thumbor.filters.blur',
    'thumbor.filters.extract_focal',
    'thumbor.filters.focal',
    'thumbor.filters.no_upscale',
    'thumbor.filters.saturation',
    'thumbor.filters.max_age',
    'thumbor.filters.curve',
    'thumbor.filters.background_color',
    'thumbor.filters.upscale',
    'thumbor.filters.proportion',
    'thumbor.filters.stretch',
]

# --- Metrics ---
# statsd -> statsd_exporter -> Prometheus (see docker/docker-compose.nsx.yaml)
METRICS = 'nsx_metrics'
STATSD_HOST = 'statsd-exporter'
STATSD_PORT = 9125  # statsd_exporter TCP listener (UDP lossy in Docker Desktop)
STATSD_PREFIX = 'thumbor'
