from fastapi import FastAPI

from .health import router as health_router
from .profiles.router import router as profiles_router
from .version import __version__

app = FastAPI(
    title="Profile API",
    version=__version__,
    description="Create, read, update, delete and list person profiles.",
)

app.include_router(health_router)
app.include_router(profiles_router)
