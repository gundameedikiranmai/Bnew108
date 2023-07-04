import os
import yaml
import json
import requests
import random
from logging import getLogger
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import actions.utils as utils

logger = getLogger(__name__)

def load_faqs():
    faq_file = os.path.join("chatbot_data", "faq", "faq.yml")
    return yaml.load(open(faq_file), Loader=yaml.FullLoader)["faqs"]

faqs = load_faqs()

class ValidateExploreJobsForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_explore_jobs_form"
    
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
            result_dict["resume_upload"] = "ignore"
        return result_dict
    
    # def validate_job_title(
    #     self,
    #     slot_value: Any,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: DomainDict,
    # ) -> Dict[Text, Any]:
    #     """Validate `job_title` value."""
    #     result_dict = {
    #         "job_title": None,
    #         "faq_suggestion_context": slot_value
    #     }
    #     question_data = faqs[slot_value]
    #     dispatcher.utter_message(text=question_data["answer"])
    #     dispatcher.utter_message(response="utter_suggest_more_questions")
    #     return result_dict


class AskJobTitleAction(Action):
    def name(self) -> Text:
        return "action_ask_job_title"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        result = []
        dispatcher.utter_message(response="utter_ask_job_title")
        utt = {
            "ui_component": "job_title",
            "titles": ["client", "software developer"],
            "intent": "input_job_title",
            "entity": "job_title"
        }
        dispatcher.utter_message(json_message=utt)
        return result

class AskJobLocationAction(Action):
    def name(self) -> Text:
        return "action_ask_job_location"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        result = []
        dispatcher.utter_message(response="utter_ask_job_location")
        utt = {
            "ui_component": "job_location",
            "intent": "input_job_location",
            "entity": "job_location"
        }
        dispatcher.utter_message(json_message=utt)
        return result

class AskSelectJobAction(Action):
    n_jobs_to_show = 5

    def name(self) -> Text:
        return "action_ask_select_job"

    def fetch_jobs(self, job_title):
        url = "https://sequence.accuick.com/Sequence/searchjobs"
        payload = {
            "keyWords":job_title,
            "location":"",
            "jobType":"",
            "hours":"",
            "payRate":"",
            "next":"0",
            "userId":0
        }
        job_resp = requests.post(url, json=payload)
        logger.info(f"job_resp: {job_resp.text}, status: {job_resp.status_code}")
        if job_resp.status_code == 200:
            jobs = job_resp.json()
            return jobs.get("Match", [])[:self.n_jobs_to_show]
        return []


    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        result = []
        jobs = self.fetch_jobs(tracker.get_slot("job_title"))
        logger.info("matched jobs: " + json.dumps(jobs, indent=4))
        utt = {
            "ui_component": "select_job",
            "jobs": jobs,
            "intent": "input_select_job",
            "entity": "select_job"
        }
        dispatcher.utter_message(json_message=utt)
        return result


class ExploreJobsFormSubmit(Action):

    def name(self) -> Text:
        return "explore_jobs_form_submit"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        """Define what the form has to do after all required slots are filled"""
        result = []
        dispatcher.utter_message(text="thanks for applying " + str(tracker.get_slot("select_job")))
        dispatcher.utter_message(response="utter_greet")
        return result