"""
api_controller.py
"""
import json
from fastapi import APIRouter, Request
from config.conf import settings
import controllers.utils as utils
from controllers.models import session
from controllers.schema import RasaWebhook
from controllers.rasa_controller import rasa_webhook

# intents to ignore
router = APIRouter()

@router.post("/upload_resume")
async def upload_resume(request: Request):
    form_data = await request.form()
    settings.logger.info(form_data)
    settings.logger.info("dict: " + str(dict(form_data)))
    resume_file = form_data["resume"]

    # resume_upload_data = {
    #     "filename": (resume_file.filename, resume_file.file, resume_file.content_type)
    # }
    # TODO add integration with resume upload api
    settings.logger.info(resume_file.content_type + ", " + resume_file.filename)
    metadata = json.loads(form_data["metadata"]) if "metadata" in form_data else None
    # message = '/input_resume_upload_data{"candidate_id": "1234"}'
    # rasa_payload = RasaWebhook(sender=form_data["sender"], message=message, metadata=metadata)

    # return rasa_webhook(rasa_payload)
    return utils.JsonResponse({"message": "uploaded", "success": True, "candidate_id": "1234"}, 200)


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