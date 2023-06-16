"""
api_controller.py
"""
import os
import re
import copy
import json
import requests
from fastapi import APIRouter, Request
from config.conf import settings
import controllers.utils as utils
from controllers.models import session
from controllers.schema import RasaWebhook

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