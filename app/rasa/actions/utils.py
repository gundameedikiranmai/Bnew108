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
        # today_date = datetime.now()
        # last_valid_date = today_date.replace(year=today_date.year - cfg.DATE_MIN_YEARS_DIFFERENCE)
        # return given_date < last_valid_date
        return True
    except ValueError:
        return False

def validate_ssn(ssn_str):
    try:
        is_length = len(ssn_str) in [9, 10]
        if is_length is False:
            return is_length
        int_ssn = int(ssn_str)
        return True
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

def reupload_resume_update_contact_details(user_id, email):
    try:
        payload = {
            "userId": user_id,
            "email": email
        }
        print(cfg.REUPLOAD_RESUME_UPDATE_CONTACT_DETAILS, payload)
        resp = requests.post(cfg.REUPLOAD_RESUME_UPDATE_CONTACT_DETAILS, json=payload).json()
        logger.info(f"Email sync response: {resp}")
        return resp.get("Success", False), resp.get("Message", "")
    except Exception as e:
        logger.exception(e)
        logger.error(f"Could not update contact details")
    return False, "Backend server is unreachable"


########### explore jobs utils ###############
def get_screening_questions_for_job_id(tracker, user_id=None):
    job_id = tracker.get_slot("select_job")
    client_id = tracker.get_slot("client_id")
    if user_id is None:
        user_id = tracker.get_slot("user_id")
    questions_data_transformed = []
    questions_data_transformed1 = []
    result = []
    result1 = []
    if user_id is not None:
        questions_data_transformed, result = parse_custom_json(tracker, job_id, client_id, user_id)
    else:
        # resume was not uploaded
        result += [SlotSet("resume_upload", None)]
    
    logger.info("job specific questions obtained.")
    if is_default_screening_form_preference_valid(tracker):
        return questions_data_transformed, result + [SlotSet("input_edit_preferences", "ignore"), SlotSet("view_edit_preferences", "ignore")]
    
    #
    if user_id is not None:
        logger.info("getting user preferences.")
        questions_data_transformed1, result1 = parse_user_preference_json(user_id)
        result += [SlotSet("is_default_screening_questions", True)]
    #
    result += result1
    questions_data_transformed += questions_data_transformed1

    synced_data = get_synced_sender_data(tracker.sender_id)
    if synced_data.get("data", {}).get("screening_question_history") is not None:
        # this user has already provided preferences that need to be updated.
        result += [SlotSet("input_edit_preferences", None), SlotSet("view_edit_preferences", None)]
    else:
        # this user is entering preferences for first time.
        result += [SlotSet("input_edit_preferences", "ignore"), SlotSet("view_edit_preferences", "ignore")]
    
    return questions_data_transformed, result


def parse_user_preference_json(user_id):
    questions_data_transformed = []
    try:
        resp_json = requests.get(cfg.ACCUICK_CHATBOT_USER_PREFERENCE_GET_URL + user_id).json()
        for q in resp_json.get("json", []):
            q_transformed = {"text": q["Label"], "selection": q.get("selection"), "data_key": q["datakey"], "data_key_label": q.get("datakeyLabel"), "is_review_allowed": True}
            if q.get("selection") == "multiple":
                # add multi-select
                options = [{"key": o["Name"], "value": str(o["LookupId"])} for o in q["Options"]]
                q_transformed.update({"input_type": "multi-select", "options": options, "anyRadioButton": q.get("anyRadioButton")})
            elif q.get("selection") == "single":
                q_transformed["buttons"] = [{"payload": str(val.get("LookupId")), "title": val.get("Name")} for val in q.get("Options", [])]
            else:
                continue
            questions_data_transformed.append(q_transformed)
    except Exception as e:
        logger.exception(e)
    return questions_data_transformed, []

def parse_custom_json(tracker, job_id, client_id, user_id):
    questions_data_transformed = []
    result = []
    try:
        url = cfg.GET_CUSTOM_JOB_FORM.format(job_id=job_id, client_id=client_id, user_id=user_id)
        print(url)
        resp_json = requests.get(url).json()
        # form = json.loads(resp_json["Job"][0]["json"])
        user_details = resp_json["Job"][0]["userDetails"]
        form = resp_json["Job"][0]["json"]
        for q in form:
            # first check hardcoded id's
            if q["id"] in list(cfg.FIXED_FORM_BUILDER_PROFILE_IDS.keys()):
                field_name = cfg.FIXED_FORM_BUILDER_PROFILE_IDS[q["id"]]
                user_details_data = user_details.get(field_name)
                logger.info(f"-------USER Details, field_name={field_name}, data={user_details_data}")
                if user_details_data is not None and len(user_details_data) > 0:
                    if field_name == "email" and tracker.get_slot("email") is None:
                        logger.info(f"setting EMAIL slot")
                        result += [SlotSet("email", user_details_data)]
                    elif field_name == "phoneNo" and tracker.get_slot("phone_number") is None:
                        logger.info(f"setting PHONE NUMBER slot")
                        result += [SlotSet("phone_number", user_details_data)]
                    if field_name == "firstName" and tracker.get_slot("first_name") is None:
                        logger.info(f"setting FIRST NAME slot")
                        result += [SlotSet("first_name", user_details_data)]
                    if field_name == "lastName" and tracker.get_slot("full_name") is None:
                        first_name = user_details.get("firstName")
                        if first_name is not None and len(first_name) > 0:
                            logger.info(f"setting FULL NAME slot")
                            result += [SlotSet("full_name", f"{first_name} {user_details_data}")]
                    # we already know the value for this question.
                    continue
            
            if q["inputType"] in ["attachment", "fileupload"]:
            # if resume was cancelled, set it to None so that it can be asked later again....
                if tracker.get_slot("resume_upload") == "false":
                    result += [SlotSet("resume_upload", None)]
                # resume has a separate slot, don't add in screening questions list
                continue

            # TODO text put here as adhoc for full_name
            elif q["fieldType"] in ["email", "phone"]:
                # ignore these input types as they are mandatory.
                continue

            q_transformed = {"id": q.get("id"), "input_type": q["inputType"], "data_key": q.get("datakey", ""), "is_review_allowed": False}
            if q.get("labelName") is None or len(q.get("labelName").strip()) == 0:
                continue
            q_transformed["text"] = q.get("labelName")
            inputType = q.get("inputType")
            if inputType in ["checkbox", "radio"]:
                q_transformed["buttons"] = [{"payload": "Yes", "title": "Yes"}, {"payload": "No", "title": "No"}]
            elif inputType == "dropdown":
                q_transformed["buttons"] = [{"payload": val, "title": val} for val in q.get("options", [])]
            # elif inputType == "date":
            #     q_transformed["custom"] = {"ui_component": "datepicker", "placeholder_text": "Please select a date"}
            # else:
            #     q_transformed["buttons"] = [{"payload": val.get("value"), "title": val.get("name")} for val in q.get("PossibleValue", [])]
            elif inputType in ["ssn"]:
                q_transformed["custom"] = {"ui_component": q.get("fieldType"), "placeholder_text": q.get("placeholderName")}
            elif inputType == "text":
                if q.get("fieldType") in ["address", "ssn"]:
                    q_transformed["custom"] = {"ui_component": q.get("fieldType"), "placeholder_text": q.get("placeholderName")}
                    q_transformed["input_type"] = q.get("fieldType")
            questions_data_transformed.append(q_transformed)
    except Exception as e:
        logger.exception(e)
        logger.error("Could not fetch user details")
    return questions_data_transformed, result