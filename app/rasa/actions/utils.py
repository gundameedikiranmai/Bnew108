import os
import requests
import json
from datetime import datetime
from logging import getLogger
from rasa_sdk.events import SlotSet
import actions.config_values as cfg

logger = getLogger(__name__)

def get_metadata_field(tracker, field):
    """ returns field and slotset event if any"""
    field_slot = tracker.get_slot(field)
    if field_slot:
        # slot was not None
        print("reading {} from slot....".format(field))
        return field_slot, []
    else:
        tracker_field = tracker.get_last_event_for("user").get("metadata", {}).get(field)
        if tracker_field:
            # field was not none
            print("reading {} from tracker".format(field))
            if field == "email":
                tracker_field = tracker_field.lower()
            return tracker_field, [SlotSet(field, tracker_field)]
        else:
            print("reading {} from tracker, output None".format(field))
            return None, []


def accuick_job_apply(user_id, job_id, client_id):
    is_success = False
    workflow_url = ""
    payload = {
        "userId": get_default_slot_value(user_id),
        "accuickJobId": job_id,
        "source": "ChatBot",
        "clientId": client_id
    }

    logger.info("Job Apply API payload: " + str(payload))

    resp = requests.post(cfg.ACCUICK_JOB_APPLY_URL, json=payload)
    try:
        job_apply_resp = resp.json()
        logger.info("Job Apply API response: " + str(job_apply_resp))
        is_success = True
        workflow_url = job_apply_resp.get("workflowURL", "")
    except Exception as e:
        logger.exception(e)
        logger.error("Could not submit job application")
    return is_success, workflow_url


def get_default_slot_value(val, default_val=""):
    if val in cfg.SLOT_IGNORE_VALUES:
        return default_val
    return val


def validate_date(date_str):
    try:
        given_date = datetime.strptime(date_str, cfg.DATE_FORMAT)
        today_date = datetime.now()
        last_valid_date = today_date.replace(year=today_date.year - cfg.DATE_MIN_YEARS_DIFFERENCE)
        return given_date < last_valid_date
    except ValueError:
        return False

def is_default_screening_form_preference_valid(tracker):
    job_screening_questions_last_update_time = tracker.get_slot("job_screening_questions_last_update_time")
    # if job_screening_questions_last_update_time is not None and (datetime.now() - datetime.fromisoformat(job_screening_questions_last_update_time)).days < cfg.SCREENING_FORM_MIN_DAYS_THRESHOLD:
    #     return True
    
    # TODO replace later, temp limit of 5 minutes
    if job_screening_questions_last_update_time is not None and (datetime.now() - datetime.fromisoformat(job_screening_questions_last_update_time)).seconds < 5*60:
        return True
    return False


def is_resume_last_search_available(tracker):
    last_job_search_timestamp = tracker.get_slot("last_job_search_timestamp")
    if last_job_search_timestamp is not None:
        return True
    return False


def sync_sender_data(payload):
    url = os.getenv("API_SERVER_URL")
    resp = requests.post(url + "/api/sync_sender_data/", json=payload)


def get_synced_sender_data(sender_id):
    url = os.getenv("API_SERVER_URL")
    resp = requests.get(url + "/api/get_synced_sender_data/", params={"sender_id": sender_id}).json()
    return resp


def get_user_details(client_id, user_id):
    slots = []
    first_name = None
    try:
        resp = requests.get(cfg.GET_USER_DETAILS_API.format(client_id=client_id, user_id=user_id)).json()
        logger.info(f"get user details user_id={user_id}\n" + json.dumps(resp, indent=4))
        slot_mapping = {
            "resume_upload": user_id,
            "phone_number": resp.get("phoneNo", "").strip(),
            "full_name": resp.get("firstName", "").strip() + resp.get("lastName", "").strip(),
            "first_name": resp.get("firstName", "").strip(),
            "email": resp.get("email", "").strip(),
            "job_title": resp.get("jobTitle", "").strip(),
            "update_contact_details": "ignore",
            # "is_resume_parsing_done": "true"
        }
        for key, value in slot_mapping.items():
            if value is not None and len(value) > 0:
                slots.append( SlotSet(key, value) )
        
        slots += [SlotSet("is_resume_upload", True)]
        
        if len(slot_mapping.get("first_name").strip()) > 0:
            first_name = slot_mapping.get("first_name").strip()

        logger.info(slots)

    except Exception as e:
        logger.exception(e)
        logger.error("Could not fetch user details")
    return slots, first_name


def get_applied_jobs_in_portal(user_id):
    applied_jobs = []
    try:
        if user_id is not None:
            resp = requests.get(cfg.GET_APPLIED_JOBS_URL.format(user_id=user_id)).json()
            applied_jobs = [str(job["jobId"]) for job in resp["Jobs"]]
            logger.info(f"jobs applied in portal={applied_jobs}")
    except Exception as e:
        logger.exception(e)
        logger.error(f"Could not applied job details for user_id={user_id}")
    return applied_jobs

def sync_email_data(payload):
    # returns if email exists
    try:
        resp = requests.post(cfg.CURATELY_EMAIL_SYNC_API, json=payload).json()
        logger.info(f"Email sync response: {resp}")
        return resp.get("Error", False)
    except Exception as e:
        logger.exception(e)
        logger.error(f"Could not sync email data")
    return True