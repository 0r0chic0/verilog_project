from fastapi import APIRouter

from app.api.routes import items, login, private, users, utils
from app.api.routes.generate import router as generate_router
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(generate_router)

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
