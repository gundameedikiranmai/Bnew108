"""
api_controller.py
"""
import os
import json
import requests
from logging import getLogger
from fastapi import APIRouter, Request
from config.conf import settings
import controllers.utils as utils
from controllers.models import session
from controllers.schema import RasaWebhook
from controllers.rasa_controller import rasa_webhook
from datetime import date, datetime, timedelta

logger = getLogger(__name__)

# intents to ignore
router = APIRouter()

HOST = os.getenv("HOST")
logger.info(f"Using host: {HOST}")

# tr = utils.get_tracker_from_rasa("585c82d2-d7ba-11ee-a528-475e0d709371")
# print(tr.get("slots", {}).get("resume_upload"))

# helper methods
def upload_new_resume(form_data):
    resume_file = form_data["resume"]
    metadata = json.loads(form_data["metadata"])
    try:
        url = f"{HOST}/QADemoCurately/resumeMe"
        
        files=[
            ('resume',(resume_file.filename, resume_file.file, resume_file.content_type))
        ]
        logger.info(resume_file.content_type + ", " + resume_file.filename)
        response = requests.request("POST", url, files=files, data={"clientId": metadata.get("client_id")})
        # response = requests.request("POST", url, data=payload)
        resp = response.json()
        logger.info("Resume Upload API response:" + json.dumps(resp, indent=4))

        # TODO add integration with resume upload api
        # metadata = json.loads(form_data["metadata"]) if "metadata" in form_data else None
        # message = '/input_resume_upload_data{"user_id": "1234"}'
        # rasa_payload = RasaWebhook(sender=form_data["sender"], message=message, metadata=metadata)

        job_title = resp.get("jobTitle", "").strip()
        job_location = resp.get("location", "").strip()

        if job_title is None and job_location == "":
            job_title = "ignore"
        if job_title is not None and job_location == "":
            job_location = "ignore"

        slots = {
            "phone_number": resp.get("phoneNo", "").strip(),
            "full_name": resp.get("firstName", "").strip() + resp.get("lastName", "").strip(),
            "first_name": resp.get("firstName", "").strip(),
            "email": resp.get("email", "").strip(),
            "job_title": job_title,
            "update_contact_details": "ignore",
            "is_resume_parsing_done": "true"
        }

        utils.add_slot_set_events(form_data["sender"], slots)

        # return rasa_webhook(rasa_payload)
        return utils.JsonResponse(resp, 200)
    except Exception as e:
        logger.error("Could not upload resume.")
        logger.exception(e)
        return utils.JsonResponse({"message": "could not upload resume.", "success": False, "user_id": None}, 200)


# helper methods
def reupload_resume(form_data, tracker_slots):   
    resume_file = form_data["resume"]
    metadata = json.loads(form_data["metadata"])
    try:
        url = f"{HOST}/QADemoCurately/reUploadResume"
        
        files=[
            ('resume',(resume_file.filename, resume_file.file, resume_file.content_type))
        ]
        logger.info(resume_file.content_type + ", " + resume_file.filename)
        print(tracker_slots.get("user_id"))
        response = requests.request("POST", url, files=files, data={"clientId": metadata.get("client_id"), "userId": tracker_slots.get("user_id") })
        resp = response.json()
        logger.info("Resume RE-Upload API response:" + json.dumps(resp, indent=4))

        job_title = resp.get("jobTitle", "").strip()
        job_location = resp.get("location", "").strip()

        if job_title is None and job_location == "":
            job_title = "ignore"
        if job_title is not None and job_location == "":
            job_location = "ignore"

        slots = {
            "full_name": resp.get("firstName", "").strip() + " " + resp.get("lastName", "").strip(),
            "first_name": resp.get("firstName", "").strip(),
            "job_title": job_title,
            "is_resume_parsing_done": "true"
        }

        # check if contact details have changed
        if (len(resp.get("email", "").strip())> 0 and not tracker_slots.get("email") == resp.get("email", "").strip()) or \
            (len(resp.get("phone-number", "").strip()) > 0 and not tracker_slots.get("phone_number") == resp.get("phone-number", "").strip()):
            slots["contact_details_temp"] = json.dumps({"email": resp.get("email", "").strip(), "phone_number": resp.get("phone-number", "").strip()})
            slots["update_contact_details"] = "set_to_none"
        else:
            slots["update_contact_details"] = "ignore"

        utils.add_slot_set_events(form_data["sender"], slots)

        # return rasa_webhook(rasa_payload)
        return utils.JsonResponse(resp, 200)
    except Exception as e:
        logger.error("Could not re-upload resume.")
        logger.exception(e)
        return utils.JsonResponse({"message": "could not upload resume.", "success": False, "user_id": None}, 200)


@router.post("/upload_resume")
async def upload_resume(request: Request):
    form_data = await request.form()
    logger.info(form_data)
    logger.info("dict: " + str(dict(form_data)))
    # TODO remove hard code
    tracker = utils.get_tracker_from_rasa(form_data["sender"])
    # tracker = utils.get_tracker_from_rasa("bde2192c-d6d0-11ee-a10e-2be33777c5fe")

    logger.info(f'candidate id: {tracker.get("slots", {}).get("user_id")}')

    if tracker.get("slots", {}).get("user_id") is not None:
        return reupload_resume(form_data=form_data, tracker_slots=tracker.get("slots", {}))
    else:
        return upload_new_resume(form_data)
    


@router.get("/get_responses/")
def get_conversation_responses(sender_id: str):
    """
    """
    logger.info("this is a log " + sender_id)
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


@router.get("/analytics/")
def get_analytics(
        from_date: datetime = datetime.combine(date.today(), datetime.min.time()) - timedelta(days=30),
        to_date : datetime = datetime.combine(date.today(), datetime.min.time()) + timedelta(days=1),
        chatbot_type: str = None
    ):
    """
    """
    logger.info(f"finding analytics from {from_date} to {to_date}")
    logger.info(f"finding analytics from {from_date.timestamp()} to {to_date.timestamp()}")
    data = session.get_conversation_count(from_date, to_date, chatbot_type)
    return data


@router.get("/transcript/")
def get_transcript(
        sender_id: str = None,
        email: str = None
    ):
    """
    """
    data = session.get_transcript(sender_id=sender_id, email=email)
    return data


@router.get("/get_session_list/")
def get_session_list(
        from_date: datetime = datetime.combine(date.today(), datetime.min.time()) - timedelta(days=30),
        to_date : datetime = datetime.combine(date.today(), datetime.min.time()) + timedelta(days=1),
        query_type: str = "total_sessions",
        job_title: str = None
    ):
    """
    """
    logger.info(f"finding analytics from {from_date} to {to_date}")
    logger.info(f"finding analytics from {from_date.timestamp()} to {to_date.timestamp()}")
    extra_params = {"job_title": job_title}
    data = session.get_session_list(from_date, to_date, query_type, extra_params)
    return data


# @router.get("/add_ip/")
# def add_ip(dry_run: bool = True):
#     """
#     """
#     data = session.add_ip(dry_run)
#     return data

@router.post("/sync_sender_data/")
async def sync_sender_data(request: Request):
    """
    """
    json_data = await request.json()
    is_success = session.set_screening_respones(sender_id=json_data["sender_id"], data=json_data["data"])
    logger.info(f"Sync sender data status: {is_success}")
    return is_success


@router.get("/get_synced_sender_data/")
def get_synced_sender_data(
        sender_id: str,
    ):
    logger.info(f"Fetching synced_sender_data for sender_id={sender_id}")
    data = session.get_synced_sender_data(sender_id)
    return data