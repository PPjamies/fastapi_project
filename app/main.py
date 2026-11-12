from fastapi import FastAPI

from app.api.router import router

__version__ = "2.0.0"

app = FastAPI(
    title="fastapi_project",
    version=__version__
)

app.include_router(router, prefix="/api/v1")
