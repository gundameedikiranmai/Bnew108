import os
import copy
import json
import re
import requests
from logging import getLogger
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import yaml
import actions.utils as utils
from actions.common_actions import AskUtteranceWithPlaceholderAction, add_date_utterance
import actions.config_values as cfg
from datetime import datetime

logger = getLogger(__name__)

class ValidateJobScreeningForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_job_screening_form"
    
    def validate_email(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `email` value."""
        logger.info(f"validating input {slot_value}")
        if slot_value is not None and cfg.email_pattern.match(slot_value):
            print("valid email from slot:", slot_value.lower())
            return {"email": slot_value.lower()}
        else:
            dispatcher.utter_message(response="utter_email_invalid")
            return {"email": None}


    def validate_phone_number(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `phone_number` value."""
        logger.info(f"validating input {slot_value}")

        if cfg.phone_pattern.match(slot_value):
            phone = re.sub("[^0-9]", "", slot_value)
            if len(phone) == 10:
                return {"phone_number": phone}

        # else case
        dispatcher.utter_message(response="utter_phone_number_error")
        return {"phone_number": None}

    def validate_input_edit_preferences(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `input_edit_preferences` value."""
        logger.info(f"validating input {slot_value}")
        result_dict = {"input_edit_preferences": slot_value}

        if slot_value is True:
            dispatcher.utter_message(response="utter_edit_preferences")
        elif slot_value is False:
            synced_data = utils.get_synced_sender_data(tracker.sender_id)
            # set the slots from synced data
            result_dict.update(synced_data["data"])
            result_dict["screening_question"] = "ignore"

        return result_dict


    def validate_screening_question(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `screening_question` value."""
        logger.info(f"validating input {slot_value}")
        if slot_value in [None, "ignore"]:
            return {"screening_question": slot_value}
        
        job_screening_questions = tracker.get_slot("job_screening_questions")
        job_screening_questions_count = tracker.get_slot("job_screening_questions_count")
        
        
        history = tracker.get_slot("screening_question_history")
        if history is None:
            history = []
        n_history = len(history)

        input_type = job_screening_questions[n_history].get("input_type")

        # check for back message
        if n_history > 0 and slot_value.upper() == cfg.SCREENING_FORM_BACK_KEYWORD:
            dispatcher.utter_message(response="utter_screening_go_back")
            return {"screening_question": None, "screening_question_history": history[:-1]}
        elif input_type == "date" and not utils.validate_date(slot_value):
            dispatcher.utter_message(response="utter_date_error")
            return {"screening_question": None}
        
        result_dict = {
            "screening_question_history": history + [slot_value]
        }
        if n_history + 1 < job_screening_questions_count:
            result_dict["screening_question"] = None
        else:
            result_dict["screening_question"] = slot_value
            dispatcher.utter_message(json_message={"screening_start": False})
            print(history)
        return result_dict


class AskEmailAction(AskUtteranceWithPlaceholderAction):
    def __init__(self):
        self.set_params("email", cfg.PLACEHOLDER_EMAIL)

class AskEmailAction(AskUtteranceWithPlaceholderAction):
    def __init__(self):
        self.set_params("phone_number", cfg.PLACEHOLDER_PHONE_NUMBER)

class AskEmailAction(AskUtteranceWithPlaceholderAction):
    def __init__(self):
        self.set_params("full_name", cfg.PLACEHOLDER_FULL_NAME)


class AskScreeningQuestionAction(Action):
    def name(self) -> Text:
        return "action_ask_screening_question"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        # either load from slot or look for job id value from metadata.
        result = []
        questions_data = tracker.get_slot("job_screening_questions")
        input_type = None
        job_screening_questions_count = tracker.get_slot("job_screening_questions_count")
        
        history = tracker.get_slot("screening_question_history")
        if history is None:
            history = []
        n_history = len(history)
        
        if n_history == 0:
            dispatcher.utter_message(json_message={"screening_start": True})
        if n_history < job_screening_questions_count:
            # if n_history > 0 and questions[n_history - 1].get("validations") is not None:
            #     validation_info = questions[n_history - 1].get("validations")
            #     if history[n_history - 1] == validation_info["correct_answer"]:
            # logger.info(f"displaying question: {questions[n_history]}")
            logger.info(f"rendering: {questions_data[n_history]}")
            input_type = questions_data[n_history].get("input_type")
            
            # if a question has some metadata, send all of it as a json message to avoid sending multiple messages.
            if questions_data[n_history].get("metadata"):
                dispatcher.utter_message(json_message=questions_data[n_history])
            else:
                dispatcher.utter_message(**questions_data[n_history])
            # if "buttons" not in questions_data:
                # if there are no buttons
            # dispatcher.utter_message(text=questions_data[n_history].get("text"), buttons=questions_data[n_history].get("buttons"), json_message=questions_data[n_history].get("custom"))
            if input_type == "date":
                add_date_utterance(dispatcher)
            
            if n_history == 1 and (questions_data[n_history].get("buttons") is None or len(questions_data[n_history].get("buttons")) == 0):
                # show back prompt on second question
                dispatcher.utter_message(response="utter_screening_show_back_prompt")
        else:
            dispatcher.utter_message(text="Error.... all questions have been answered...")
        return result


class JobScreeningFormSubmit(Action):

    def name(self) -> Text:
        return "job_screening_form_submit"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        """Define what the form has to do after all required slots are filled"""   
        dispatcher.utter_message(response="utter_submit")
        # dispatcher.utter_message(text="Your responses are:" + ", ".join(tracker.get_slot("screening_question_history")))
        selected_job = tracker.get_slot("select_job")
        result = job_screening_submit_integration(tracker, selected_job, dispatcher)
        return result


############# utils #################

def sync_screening_responses(tracker):
    payload = {
        "email": tracker.get_slot("email"),
        "candidateId": tracker.get_slot("resume_upload"),
        "fullName": tracker.get_slot("full_name"),
        "phoneNumber": tracker.get_slot("phone_number"),
        "jobId": tracker.get_slot("select_job"),
        "candidateResponses": [],
        "clientId": tracker.get_slot("client_id")
    }
    if tracker.get_slot("job_screening_questions") is not None and tracker.get_slot("screening_question_history") is not None:
        payload["candidateResponses"] = [{"id": q["id"], "label": q["text"], "answer": a} for q, a in zip(tracker.get_slot("job_screening_questions"), tracker.get_slot("screening_question_history")) ]
    
    logger.info("Sending sync response: " + str(payload))
    response = requests.post(cfg.ACCUICK_CHATBOT_RESPONSE_SUBMIT_URL, json=payload)
    logger.info("received status code from sync response: " + str(response.status_code))
    #  no need to check for response body as it is empty, only printing the status code
    # try:
    #     print(response.status_code, response.text)
    #     resp = response.json()
    #     print(json.dumps(resp, indent=4))
    # except Exception as e:
    #     logger.error("Could not submit screening responses to webhook")
    #     logger.error(e)


def job_screening_submit_integration(tracker, selected_job, dispatcher, utter_menu=True):
    sync_screening_responses(tracker)
    is_success = utils.accuick_job_apply(tracker.get_slot("resume_upload"), selected_job, tracker.get_slot("client_id"))
    applied_jobs = tracker.get_slot("applied_jobs")
    if is_success:
        applied_jobs += [selected_job]
    
    result = [
        SlotSet("job_screening_questions", None),
        SlotSet("job_screening_questions_count", None),
        SlotSet("select_job", None),
        SlotSet("applied_jobs", applied_jobs),
        SlotSet("job_screening_questions_last_update_time", str(datetime.now())),
    ]
    if tracker.get_slot("is_default_screening_questions") is True:
        logger.info("saving default screening questions responses in DB.")
        sync_sender_data_payload = {
            "sender_id": tracker.sender_id,
            "data": {
                "job_screening_questions": tracker.get_slot("job_screening_questions"),
                "job_screening_questions_count": tracker.get_slot("job_screening_questions_count"),
                "screening_question_history": tracker.get_slot("screening_question_history"),
                "job_screening_questions_last_update_time": str(datetime.now())
            }
        }
        utils.sync_sender_data(sync_sender_data_payload)
        result += [SlotSet("is_default_screening_questions", False)]
    
    if utter_menu:
        dispatcher.utter_message(response="utter_greet", greet="after_apply")
    return result