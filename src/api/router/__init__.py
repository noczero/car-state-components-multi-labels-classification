from fastapi import APIRouter

from src.api.router import classifier_endpoint, explainer_endpoint

api_router = APIRouter()

api_router.include_router(classifier_endpoint.router, prefix="/classifier", tags=["classifier"])
api_router.include_router(explainer_endpoint.router, prefix="/explainer", tags=["explainer"])