"""
api_controller.py
"""
from fastapi import APIRouter
from config.conf import settings
import controllers.utils as utils
from controllers.models import session

# intents to ignore
router = APIRouter()


@router.get("/get_responses/")
def get_conversation_responses(sender_id: str):
    """
    """
    settings.logger.info("this is a log " + sender_id)
    tracker_obj = session.get_tracker_object(sender_id)
    if tracker_obj is not None:
        data = {
            "success": True,
            "data": {
                "answers": tracker_obj.get("slots", {}).get("screening_question_history", [])
            },
            "error": None
        }
    else:
        data = {
            "success": False,
            "data": None,
            "error": f"Error: no conversation for sender_id= {sender_id}"
        }
    return utils.JsonResponse(data, 200)