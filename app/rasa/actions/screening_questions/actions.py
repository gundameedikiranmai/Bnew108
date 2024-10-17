import os
import copy
import json
import re
import requests
from logging import getLogger
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType, SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import yaml
import actions.utils as utils
from actions.common_actions import AskUtteranceWithPlaceholderAction, add_date_utterance, add_multiselect_utterance
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
            payload = {
                "userId": tracker.get_slot("user_id"),
                "clientId": tracker.get_slot("client_id"),
                "email": slot_value.lower()
            }
            if slot_value in tracker.latest_message.get("text"):
                # the email has been entered by user.
                is_email_exist = utils.sync_email_data(payload)
                if is_email_exist:
                    dispatcher.utter_message(response="utter_email_already_exist")
                    return {"email": None}
            # email does not exist, accept it and move forward
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
    
    def validate_full_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `full_name` value."""
        logger.info(f"validating input {slot_value}")
        result_dict = {"full_name": slot_value}
        if tracker.get_slot("first_name") is None:
            result_dict["first_name"] = slot_value
        
        return result_dict


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

        if slot_value == "true":
            dispatcher.utter_message(response="utter_edit_preferences")
        elif slot_value == "false":
            synced_data = utils.get_synced_sender_data(tracker.sender_id)
            # set the slots from synced data
            for slot in cfg.USER_PREFERENCES_RELEVANT_SLOTS:
                result_dict[slot] = synced_data.get("data", {}).get(slot)
            result_dict["screening_question"] = "ignore"
            result_dict["view_edit_preferences"] = "ignore"

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

class AskPhoneNumberAction(AskUtteranceWithPlaceholderAction):
    def __init__(self):
        self.set_params("phone_number", cfg.PLACEHOLDER_PHONE_NUMBER)

class AskFullNameAction(AskUtteranceWithPlaceholderAction):
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
            logger.debug(f"rendering: {questions_data[n_history]}")
            if n_history == 1:
                # and (questions_data[n_history].get("buttons") is None or len(questions_data[n_history].get("buttons")) == 0):
                # show back prompt on second question
                dispatcher.utter_message(response="utter_screening_show_back_prompt")
            utter_screening_question(dispatcher, tracker, questions_data, n_history, go_back=True)
        else:
            dispatcher.utter_message(text="Error.... all questions have been answered...")
        return result


class ViewEditPreferencesAction(Action):
    def name(self) -> Text:
        return "action_ask_view_edit_preferences"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        # either load from slot or look for job id value from metadata.
        result = []
        questions_data = tracker.get_slot("job_screening_questions")
        # job_screening_questions_count = tracker.get_slot("job_screening_questions_count")
        screening_question_history = tracker.get_slot("screening_question_history")
        dispatcher.utter_message(template="utter_ask_view_edit_preferences_text")
        screening_response_txt = ""
        for q, a in zip(questions_data, screening_question_history):
            data_key_label = q.get("data_key_label") if q.get("data_key_label") is not None else q['data_key']
            answer_label = get_label_from_lookupid(q, a)
            screening_response_txt += f"{data_key_label}: {answer_label}\n"
        
        dispatcher.utter_message(text=screening_response_txt.strip())
        dispatcher.utter_message(template="utter_ask_view_edit_preferences_buttons")


class JobScreeningFormSubmit(Action):

    def name(self) -> Text:
        return "job_screening_form_submit"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        """Define what the form has to do after all required slots are filled"""   
        view_edit_preferences = tracker.get_slot("view_edit_preferences")
        selected_job = tracker.get_slot("select_job")
        if view_edit_preferences == "ignore":
            result = job_screening_submit_integration(tracker, selected_job, dispatcher, greet_type="after_apply")
        elif view_edit_preferences == "confirm":
            result = job_screening_submit_integration(tracker, selected_job, dispatcher, greet_type="after_apply_review_screening_questions")
        elif view_edit_preferences == "edit_details":
            dispatcher.utter_message(response="utter_screening_review_start")
            result = [FollowupAction("review_screening_questions_form")]
        elif view_edit_preferences == "review_form_completed":
            result = job_screening_submit_integration(tracker, selected_job, dispatcher, greet_type="after_apply_review_screening_questions_form_submit")
            # reset form slots
            result += [
                SlotSet("screening_question_options", None),
                SlotSet("screening_question_display_q", None),
                SlotSet("screening_review_context", None),
            ]
        return result


############# utils #################
    
def utter_screening_question(dispatcher, tracker, questions_data, n_history, go_back=False):
    input_edit_preferences = tracker.get_slot("input_edit_preferences")
    input_type = questions_data[n_history].get("input_type")            
    # if a question has some metadata, send all of it as a json message to avoid sending multiple messages.
    qdata = copy.copy(questions_data[n_history])
    if input_edit_preferences == "true":
        if n_history == 0:
            selected_var = ""
        elif n_history == len(questions_data) - 1:
            selected_var = "Lastly, "
        else:
            variations = ["Understood. ", "Got it. "]
            selected_var = variations[n_history % len(variations)]
        qdata["text"] = selected_var + qdata["text"]
    
    # add a back button for 2nd questions onward
    if go_back and n_history > 0 and len(qdata.get("buttons", [])) > 0:
        qdata["buttons"].append({"payload": "back", "title": "back"})
    
    if questions_data[n_history].get("metadata"):
        dispatcher.utter_message(json_message=qdata)
    else:
        # print("-------------------------", questions_data)
        dispatcher.utter_message(**qdata)
    if input_type == "date":
        add_date_utterance(dispatcher)
    elif input_type == "multi-select":
        add_multiselect_utterance(dispatcher, qdata["options"], qdata["anyRadioButton"], is_back_button_enabled = go_back and n_history > 0)


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
        payload["candidateResponses"] = [{"id": q.get("id", 0), "label": q["text"], "answer": a} for q, a in zip(tracker.get_slot("job_screening_questions"), tracker.get_slot("screening_question_history")) ]
    
    logger.info("Sending sync response: " + str(payload))
    response = requests.post(cfg.ACCUICK_CHATBOT_RESPONSE_SUBMIT_URL, json=payload)
    logger.info("received status code from sync response: " + str(response.status_code))

    try:
        submit_user_preferences(tracker)
    except Exception as e:
        logger.error("Could not submit user preferences")
        logger.exception(e)
    
    #  no need to check for response body as it is empty, only printing the status code
    # try:
    #     print(response.status_code, response.text)
    #     resp = response.json()
    #     print(json.dumps(resp, indent=4))
    # except Exception as e:
    #     logger.error("Could not submit screening responses to webhook")
    #     logger.error(e)


def job_screening_submit_integration(tracker, selected_job, dispatcher, greet_type):
    sync_screening_responses(tracker)
    is_success, workflow_url = utils.accuick_job_apply(tracker.get_slot("resume_upload"), selected_job, tracker.get_slot("client_id"))
    applied_jobs = tracker.get_slot("applied_jobs")
    if is_success:
        applied_jobs += [selected_job]
    
    current_timestamp = str(datetime.now())
    result = [
        SlotSet("job_screening_questions", None),
        SlotSet("job_screening_questions_count", None),
        SlotSet("select_job", None),
        SlotSet("applied_jobs", applied_jobs),
        SlotSet("last_job_search_timestamp", current_timestamp),
        SlotSet("resume_last_search", None)
    ]
    
    data = {}
    for slot in cfg.RESUME_LAST_SEARCH_RELEVANT_SLOTS:
        data[slot] = tracker.get_slot(slot)
    
    if tracker.get_slot("is_default_screening_questions") is True:
        logger.info("saving default screening questions responses in DB.")
        for slot in cfg.USER_PREFERENCES_RELEVANT_SLOTS:
            data[slot] = tracker.get_slot(slot)
        result += [
            SlotSet("is_default_screening_questions", False),
            SlotSet("job_screening_questions_last_update_time", current_timestamp),
        ]
    
    # sync sender data
    sync_sender_data_payload = {
        "sender_id": tracker.sender_id,
        "data": {
            **data,
            "job_screening_questions_last_update_time": current_timestamp,
        }
    }
    utils.sync_sender_data(sync_sender_data_payload)
        
    if workflow_url is not None and len(workflow_url.strip()) > 0:
        logger.info(f"Workflow exists: {workflow_url}")
        dispatcher.utter_message(
            response="utter_greet", 
            greet="after_apply_workflow_url_displayed"
        )
        utt = {
            "ui_component": "workflow",
            "workflow_url": workflow_url
        }
        logger.info(f"Sending workflow message: {utt}")
        dispatcher.utter_message(json_message=utt)        
    else:
        logger.info("No workflow found")
        dispatcher.utter_message(response="utter_greet", greet=greet_type)
    
    return result

def submit_user_preferences(tracker):
    user_id = tracker.get_slot("user_id")
    if user_id is None:
        logger.error("Could not submit user preferences because user_id is null")
        return
    get_response = requests.get(cfg.ACCUICK_CHATBOT_USER_PREFERENCE_GET_URL + user_id).json()
    is_edit = False
    # print(get_response)
    for item in get_response["json"]:
        for i, q in enumerate(tracker.get_slot("job_screening_questions")):
            if item["datakey"] == q["data_key"]:
                user_response = tracker.get_slot("screening_question_history")[i]
                if tracker.get_slot("is_default_screening_questions") is True:
                    item["Value"] = user_response
                    is_edit = True
                else:
                    for choice in item["Options"]:
                        if choice["Name"].lower() == user_response.lower():
                            # print(choice["LookupId"])
                            item["Value"] = choice["LookupId"]
                            is_edit = True
                            break
                    break
    
    if is_edit:
        get_response["userId"] = user_id
        logger.info("Sending set user preference payload: " + str(get_response))
        response = requests.post(cfg.ACCUICK_CHATBOT_USER_PREFERENCE_POST_URL, json=get_response)
        logger.info("Set user preference API response: " + str(response.json()))
    else:
        logger.info("No edit required for set user preference")


def get_label_from_lookupid(question, answer):
    if len(question.get("buttons", [])) > 0:
        for button in question.get("buttons"):
            if answer == button["payload"]:
                return button["title"]
    elif len(question.get("options", [])) > 0:
        options = question.get("options")
        if question.get("anyRadioButton") is not None:
            options.append({"key": question.get("anyRadioButton").get("Name"), "value": str(question.get("anyRadioButton").get("LookupId"))})
        choice_keys = []
        for choice in answer.split(","):
            choice = choice.strip()
            for option in options:
                # print(option, choice)
                if choice == option["value"]:
                    choice_keys.append(option["key"])
                    break
        return ", ".join(choice_keys)
    else:
        return answer