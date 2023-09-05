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


def accuick_job_apply(candidate_id, job_id):
    is_success = False
    payload = {
        "accuickid": get_default_slot_value(candidate_id),
        "jobid": job_id,
        "source": "ChatBot"
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