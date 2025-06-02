from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from config import settings
from src.api.router import api_router
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_VERSION_PREFIX}/openapi.json",
    docs_url="/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600
)

app.include_router(api_router, prefix=f"/api{settings.API_VERSION_PREFIX}")
