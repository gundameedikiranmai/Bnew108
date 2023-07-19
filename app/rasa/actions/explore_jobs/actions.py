import os
import yaml
import json
import requests
import random
from logging import getLogger
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType, SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import actions.utils as utils
from actions.common_actions import AskCustomBaseAction
import actions.config_values as cfg

logger = getLogger(__name__)

def load_faqs():
    faq_file = os.path.join("chatbot_data", "faq", "faq.yml")
    return yaml.load(open(faq_file), Loader=yaml.FullLoader)["faqs"]

faqs = load_faqs()

class ValidateExploreJobsForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_explore_jobs_form"
    
    def fetch_jobs(self, tracker):
        payload = {
            "keyWords":tracker.get_slot("job_title"),
            "location":"",
            "jobType":"",
            "hours":"",
            "payRate":"",
            "next":"0",
            "userId":0
        }
        try:
            job_resp = requests.post(cfg.ACCUICK_SEARCH_JOBS_URL, json=payload)
            logger.info("job_resp status: {}".format(job_resp.status_code))
            if job_resp.status_code == 200:
                jobs = job_resp.json()
                return jobs.get("Match", [])[:cfg.N_JOBS_TO_SHOW]
        except Exception as e:
            logger.error(e)
            logger.error("could not fetch jobs from search api.")
        return None
    
    def validate_is_resume_upload(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `is_resume_upload` value."""
        result_dict = {
            "is_resume_upload": slot_value
        }
        # ignore resume_upload slot if user denied uploading resume.
        if not slot_value:
            result_dict["resume_upload"] = "false"
        return result_dict
    
    def validate_job_location(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `job_location` value."""
        jobs = self.fetch_jobs(tracker)
        # set as default none, update later 
        result_dict = {
            "job_title": None,
            "job_location": None
        }
        if jobs is None:
            dispatcher.utter_message(response="utter_error_explore_jobs")
        elif len(jobs) == 0:
            dispatcher.utter_message(response="utter_explore_jobs_no_jobs_found")
        else:
            result_dict = {
                "search_jobs_list": jobs,
                "job_location": slot_value
            }
            
        return result_dict

    def validate_select_job(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `select_job` value."""
        result_dict = {
            "select_job": slot_value
        }
        # set select_job_title
        jobs = tracker.get_slot("search_jobs_list")
        for job in jobs:
            print("finding job_id", slot_value, job["jobid"], job["jobtitle"])
            if job["jobid"] == slot_value:
                result_dict["select_job_title"] = job["jobtitle"]
                break
        return result_dict


class AskResumeUploadAction(AskCustomBaseAction):
    def __init__(self):
        self.set_params(entity_name="candidate_id", intent_name="input_resume_upload_data", ui_component="resume_upload", action_name="resume_upload")

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        is_cancel_allowed = False
        if tracker.active_loop_name == "explore_jobs_form":
            is_cancel_allowed = True
        kwargs = {
            "responses": ["utter_ask_" + self.action_name],
            "data": {
                "is_cancel_allowed": is_cancel_allowed,
                "cancel_message": "/deny"
            }
        }
        return super().run(dispatcher, tracker, domain, **kwargs)


class AskJobTitleAction(AskCustomBaseAction):
    def __init__(self):
        self.set_params("job_title")

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        kwargs = {
            "responses": ["utter_ask_" + self.entity_name],
            "data": {
                "titles": ["client", "software developer"],
            }
        }
        return super().run(dispatcher, tracker, domain, **kwargs)


class AskJobLocationAction(AskCustomBaseAction):
    def __init__(self):
        self.set_params("job_location")

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        kwargs = {
            "responses": ["utter_ask_" + self.entity_name],
        }
        return super().run(dispatcher, tracker, domain, **kwargs)


class AskSelectJobAction(AskCustomBaseAction):
    def __init__(self):
        self.set_params("select_job")

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        jobs = tracker.get_slot("search_jobs_list")
        # logger.info("matched jobs: " + json.dumps(jobs, indent=4))
        kwargs = {
            "data": {
                "jobs": jobs,
            }
        }
        return super().run(dispatcher, tracker, domain, **kwargs)


class ExploreJobsFormSubmit(Action):

    def name(self) -> Text:
        return "explore_jobs_form_submit"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        """Define what the form has to do after all required slots are filled"""
        result = []
        dispatcher.utter_message(response="utter_explore_jobs_apply_success")
        dispatcher.utter_message(response="utter_screening_start")
        questions_data, slots = get_screening_questions_for_job_id(tracker)
        result += slots
        logger.info("asking questions: {}".format(json.dumps(questions_data, indent=4)))
        result += [
            # set questions to be asked after the selecting a job
            SlotSet("job_screening_questions", questions_data),
            SlotSet("job_screening_questions_count", len(questions_data)),
            # reset explore jobs form
            SlotSet("job_title", None),
            SlotSet("job_location", None),
            # reset job_screening_form
            SlotSet("screening_question", None),
            SlotSet("screening_question_history", None),
            FollowupAction("job_screening_form")
        ]
        return result


######## utils ########
def get_screening_questions_for_job_id(tracker):
    job_id = tracker.get_slot("select_job")
    result = []
    # read from sample file for now.
    # sample_questions_path = os.path.join("chatbot_data", "screening_questions", "sample_questions_after_job_apply.json")
    # questions_data = json.load(open(sample_questions_path, 'r'))["components"]
    
    # use hardcoded job id
    payload = {"action":"get","jobId":"228679","recrId":"1893"}

    resp = requests.post(cfg.ACCUICK_JOBS_FORM_BUILDER_URL, json=payload)
    questions_data = json.loads(resp.json()["json"])["components"]

    questions_data_transformed = []
    for q in questions_data:
        q_transformed = {"input_type": q["inputType"]}
        if q["inputType"] == "attachment":
            # if resume was cancelled, set it to None so that it can be asked later again....
            if tracker.get_slot("resume_upload") == "false":
                result += [SlotSet("resume_upload", None)]
            # resume has a separate slot, don't add in screening questions list
            continue
        if q.get("labelName") is not None:
            q_transformed["text"] = q.get("labelName")
        inputType = q.get("inputType")
        if inputType == "radio":
            q_transformed["buttons"] = [{"payload": val.get("value"), "title": val.get("name")} for val in q.get("PossibleValue", [])]
        elif inputType == "text":
            pass
        questions_data_transformed.append(q_transformed)

    return questions_data_transformed, result