from fastapi import FastAPI

from app.api.router import router

app = FastAPI(
    title="FastAPI Project",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(router, prefix="/api/v1")
