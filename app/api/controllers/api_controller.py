"""
api_controller.py
"""
import json
import requests
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
    try:
        url = "https://www4.accuick.com/ChatBot/resumeUpload.jsp"
        
        files=[
            ('filename',(resume_file.filename, resume_file.file, resume_file.content_type))
        ]
        settings.logger.info(resume_file.content_type + ", " + resume_file.filename)
        response = requests.request("POST", url, files=files)
        # response = requests.request("POST", url, data=payload)
        resp = response.json()
        settings.logger.info("Resume Upload API response:" + json.dumps(resp, indent=4))

        # TODO add integration with resume upload api
        # metadata = json.loads(form_data["metadata"]) if "metadata" in form_data else None
        # message = '/input_resume_upload_data{"candidate_id": "1234"}'
        # rasa_payload = RasaWebhook(sender=form_data["sender"], message=message, metadata=metadata)

        past_job_titles = resp.get("jobTitles", [])
        job_title = past_job_titles[0] if len(past_job_titles) > 0 else None
        job_location = resp.get("location", "").strip()

        if job_title is None and job_location == "":
            job_title = "ignore"
        if job_title is not None and job_location == "":
            job_location = "ignore"

        slots = {
            "phone_number": resp.get("phone-number", "").strip(),
            "full_name": resp.get("full-name", "").strip(),
            "email": resp.get("email", "").strip(),
            "job_title": job_title,
            "job_location": job_location,
            # "phone_number": "9998887776",
            # "full_name": "John doe",
            # "email": "abc@gmail.com",
        }

        utils.add_slot_set_events(form_data["sender"], slots)

        # return rasa_webhook(rasa_payload)
        return utils.JsonResponse({"message": resp["message"], "success": True, "candidate_id": resp["candidateId"]}, 200)
    except Exception as e:
        settings.logger.error("Could not upload resume.")
        settings.logger.error(e)
        return utils.JsonResponse({"message": "could not upload resume.", "success": False, "candidate_id": None}, 200)


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