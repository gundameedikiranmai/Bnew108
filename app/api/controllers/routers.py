from fastapi import APIRouter
from controllers import rasa_controller

router = APIRouter()
router.include_router(rasa_controller.router, tags=["webhooks"], prefix="/webhooks")
