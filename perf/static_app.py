from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

ROUTES = [
    Mount('/', app=StaticFiles(directory='static'), name="static"),
]

APP = Starlette(routes=ROUTES)
