from fastapi import APIRouter
from controllers import rasa_controller
from controllers import api_controller

router = APIRouter()
router.include_router(rasa_controller.router, tags=["webhooks"], prefix="/webhooks")
router.include_router(api_controller.router, tags=["api"], prefix="/api")
