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


def accuick_job_apply(candidate_id, job_id, client_id):
    is_success = False
    payload = {
        "userId": get_default_slot_value(candidate_id),
        "accuickJobId": job_id,
        "source": "ChatBot",
        "clientId": client_id
    }

    logger.info("Job Apply API payload: " + str(payload))

    resp = requests.post(cfg.ACCUICK_JOB_APPLY_URL, json=payload)
    try:
        logger.info("Job Apply API response: " + str(resp.json()))
        is_success = True
    except Exception as e:
        logger.error(e)
        logger.error("Could not submit job application")
    return is_success


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
    # if last_job_search_timestamp is not None and (datetime.now() - datetime.fromisoformat(last_job_search_timestamp)).days < cfg.RESUME_LAST_SEARCH_MIN_DAYS_THRESHOLD:
    #     return True
    
    # TODO replace later, temp limit of 5 minutes
    if last_job_search_timestamp is not None and (datetime.now() - datetime.fromisoformat(last_job_search_timestamp)).seconds > 5*60:
        return True
    return False


def sync_sender_data(payload):
    url = os.getenv("API_SERVER_URL")
    resp = requests.post(url + "/api/sync_sender_data/", json=payload)


def get_synced_sender_data(sender_id):
    url = os.getenv("API_SERVER_URL")
    resp = requests.get(url + "/api/get_synced_sender_data/", params={"sender_id": sender_id}).json()
    return resp