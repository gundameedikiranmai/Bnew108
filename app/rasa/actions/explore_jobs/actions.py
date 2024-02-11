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
from actions.screening_questions.actions import job_screening_submit_integration
import actions.config_values as cfg
from datetime import datetime

logger = getLogger(__name__)

class ActionStartExploreJobs(Action):

    def name(self) -> Text:
        return "action_start_explore_jobs"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        result = []
        # set slot values 
        chatbot_type, chatbot_type_slot = utils.get_metadata_field(tracker, "chatbot_type")
        job_location, job_location_slot = utils.get_metadata_field(tracker, "job_location")
        
        if chatbot_type == "1":
            dispatcher.utter_message(response="utter_start_explore_jobs")
        elif chatbot_type == "2":
            result += [
                SlotSet("is_resume_upload", False),
                SlotSet("resume_upload", "ignore"),
                SlotSet("job_title", "ignore"),
            ]
            dispatcher.utter_message(response="utter_start_explore_jobs_without_asking", slots={"job_location": job_location})
        
        return result + chatbot_type_slot + job_location_slot

class ValidateExploreJobsForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_explore_jobs_form"
    
    # async def required_slots(
    #     self,
    #     domain_slots: List[Text],
    #     dispatcher: "CollectingDispatcher",
    #     tracker: "Tracker",
    #     domain: "DomainDict",
    # ) -> List[Text]:
    #     chatbot_type, _ = utils.get_metadata_field(tracker, "chatbot_type")
    #     if chatbot_type == "1":
    #         return cfg.EXPLORE_JOBS_MATCHING_CRITERIA_SLOTS + domain_slots
    #     return domain_slots
    
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

    def validate_resume_upload(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `resume_upload` value."""
        result_dict = {
            "resume_upload": slot_value
        }
        # resume upload cancel
        if slot_value == "false":
            dispatcher.utter_message(response="utter_resume_upload_cancel")
            result_dict["resume_upload"] = None
            result_dict["is_resume_upload"] = None
        if tracker.get_slot("first_name") is not None:
            dispatcher.utter_message(response="utter_nice_to_meet_you")
        return result_dict

    def validate_refine_job_search_field(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `refine_job_search_field` value."""
        result_dict = {
            "refine_job_search_field": slot_value
        }
        if slot_value not in cfg.SLOT_IGNORE_VALUES:
            result_dict[slot_value] = None
            # deselect job also
            result_dict["select_job"] = None
            result_dict["previous_job_title"] = tracker.get_slot("job_title")
            
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
        if not slot_value == "restart":
            result_dict["refine_job_search_field"] = "ignore"
            
            # set select_job_title
            jobs = tracker.get_slot("search_jobs_list")
            for job in jobs:
                if job["requisitionId_"] == slot_value:
                    result_dict["select_job_title"] = job["title_"]
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
                "placeholder_text": "Upload your resume",
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
        result = []
        titles = []
        responses = []
        if tracker.get_slot("refine_job_search_field") == "job_title":
            result += [SlotSet("refine_job_search_field", None)]
            logger.info("refined - job title: " + str(tracker.get_slot("previous_job_title")))
            if tracker.get_slot("previous_job_title") not in cfg.SLOT_IGNORE_VALUES:
                titles += [tracker.get_slot("previous_job_title")]
        else:
            responses += ["utter_perfect"]
        kwargs = {
            "responses": responses + ["utter_ask_" + self.entity_name],
            "data": {
                "titles": titles,
                "placeholder_text": "Start typing to select job title",
            }
        }
        return result + super().run(dispatcher, tracker, domain, **kwargs)


class AskJobLocationAction(AskCustomBaseAction):
    def __init__(self):
        self.set_params("job_location")

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        responses = []
        result = []
        if not tracker.get_slot("refine_job_search_field") == "job_location":
            responses += ["utter_thank_you"]
        else:
            result += [SlotSet("refine_job_search_field", None)]
        kwargs = {
            "responses": responses + ["utter_ask_" + self.entity_name],
            "data": {
                "placeholder_text": "Reply to choose locations..",
            }
        }
        return result + super().run(dispatcher, tracker, domain, **kwargs)


class AskSelectJobAction(AskCustomBaseAction):
    def __init__(self):
        self.set_params("select_job")
    
    def fetch_jobs(self, tracker):
        # payload = {
        #     "keyword": utils.get_default_slot_value(tracker.get_slot("job_title")),
        #     "location": utils.get_default_slot_value(tracker.get_slot("job_location")),
        # }
        payload = {
            "jobquery": [
                {
                    "query": utils.get_default_slot_value(tracker.get_slot("job_title")),
                    "clientId": tracker.get_slot("client_id"),
                    "jobType": "All Job Types",
                    "datePosted": "0",
                    "locationFilters": [
                        {"address": utils.get_default_slot_value(tracker.get_slot("job_location")), "regionCode": "", "distanceInMiles": 0}
                    ],
                }
            ],
            "searchMode": "JOB_SEARCH",
            "disableKeywordMatch": False,
            "enableBroadening": True,
            "keywordMatchMode": "KEYWORD_MATCH_ALL",
            "offset": 0,
        }
        try:
            logger.info("job search params: " + str(payload))
            job_resp = requests.post(cfg.ACCUICK_SEARCH_JOBS_URL, json=payload)
            logger.info("job_resp status: {}".format(job_resp.status_code))
            if job_resp.status_code == 200:
                jobs = job_resp.json().get("jobList", [])
                logger.info(f"total job count: {len(jobs)}")
                applied_jobs = tracker.get_slot("applied_jobs")
                jobs_filtered = [j["job_"] for j in jobs if j["job_"]["requisitionId_"] not in applied_jobs]
                logger.info(f"filtered job count: {len(jobs_filtered)}")
                jobs_to_show = jobs_filtered[:cfg.N_JOBS_TO_SHOW]
                log_subset =  [{key: value for key, value in j.items() if key in ["requisitionId_", "title_"]} for j in jobs_to_show[:3]]
                logger.info("found jobs: " + json.dumps(log_subset, indent=4))
                return jobs_to_show
        except Exception as e:
            logger.error(e)
            logger.error("could not fetch jobs from search api.")
        return None

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        result = []
        jobs = self.fetch_jobs(tracker)
        
        if jobs is None:
            dispatcher.utter_message(response="utter_error_explore_jobs")
        elif len(jobs) == 0:
            dispatcher.utter_message(response="utter_explore_jobs_no_jobs_found")
        else:
            dispatcher.utter_message(response="utter_explore_jobs_jobs_found")
            result += [SlotSet("search_jobs_list", jobs)]
        
        # jobs = tracker.get_slot("search_jobs_list")
        # logger.info("matched jobs: " + json.dumps(jobs, indent=4))
        kwargs = {
            "data": {
                "jobs": jobs,
                "refine_job_search_message": "/refine_job_search"
            }
        }
        return result + super().run(dispatcher, tracker, domain, **kwargs)


class ExploreJobsFormSubmit(Action):

    def name(self) -> Text:
        return "explore_jobs_form_submit"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        """Define what the form has to do after all required slots are filled"""
        result = []
        
        questions_data, slots = get_screening_questions_for_job_id(tracker)
        result += slots
        logger.info("asking questions: {}".format(json.dumps(questions_data, indent=4)))
        dispatcher.utter_message(json_message={"screening_start": True})
        result += [
            # reset explore jobs form
            SlotSet("refine_job_search_field", None),
            # reset job_screening_form
            SlotSet("screening_question", None),
            SlotSet("screening_question_history", None),
        ]
        if len(questions_data) > 0:
            result += [
                # set questions to be asked after the selecting a job
                SlotSet("job_screening_questions", questions_data),
                SlotSet("job_screening_questions_count", len(questions_data)),
                FollowupAction("job_screening_form")
            ]
            dispatcher.utter_message(response="utter_explore_jobs_apply_success")
            dispatcher.utter_message(response="utter_screening_start")
        else:
            # check if any mandatory question has to be asked.
            is_ask_mandatory_question = False
            for s in cfg.SCREENING_FORM_MANDATORY_QUESTIONS:
                if tracker.get_slot(s) is None:
                    is_ask_mandatory_question = True
                    break
            if is_ask_mandatory_question:
                # there is no screening question but one or more of the mandatory questions have been left unanswered.
                result += [
                    SlotSet("screening_question", "ignore"),
                    FollowupAction("job_screening_form")
                ]
                dispatcher.utter_message(response="utter_explore_jobs_apply_success")
                dispatcher.utter_message(response="utter_screening_start")
            else:
                # no screening question has to be asked.
                dispatcher.utter_message(response="utter_greet", greet="after_apply_no_screening_questions")
                result += job_screening_submit_integration(tracker, tracker.get_slot("select_job"), dispatcher, utter_menu=False)
        return result


######## utils ########
def get_screening_questions_for_job_id(tracker):
    job_id = tracker.get_slot("select_job")
    
    # read from sample file for now.
    # sample_questions_path = os.path.join("chatbot_data", "screening_questions", "sample_questions_after_job_apply.json")
    # questions_data = json.load(open(sample_questions_path, 'r'))["components"]
    
    # use hardcoded job id
    # test job id which has screening questions configured.
    # payload = {"action":"get","jobId": "1338", "recrId":"1893", "clientId": tracker.get_slot("client_id")}
    payload = {"action":"get","jobId": job_id, "recrId":"1893", "clientId": tracker.get_slot("client_id")}

    resp = requests.post(cfg.ACCUICK_JOBS_FORM_BUILDER_URL, json=payload)
    resp_json = resp.json()
    print(payload)
    
    questions_data_transformed, result = parse_form_bulder_json(resp_json, tracker)

    if len(questions_data_transformed) == 0:
        if utils.is_default_screening_form_preference_valid(tracker):
            return [], []
        logger.info("using default form builder questions")
        resp = requests.post(cfg.ACCUICK_JOBS_FORM_BUILDER_DEFAULT_FORM_URL, json={"clientId":"2", "action":"get"})
        resp_json1 = resp.json()
        questions_data_transformed, result = parse_form_bulder_json(resp_json1, tracker)
        result += [SlotSet("is_default_screening_questions", True)]
    else:
        result += [SlotSet("is_default_screening_questions", False)]
    
    return questions_data_transformed, result


def parse_form_bulder_json(resp_json, tracker):
    questions_data = []
    result = []
    if len(resp_json["json"].strip()) > 0:
        # json object is not empty
        questions_data = json.loads(resp_json["json"])["components"]

    questions_data_transformed = []
    for q in questions_data:
        if q["inputType"] in ["attachment", "fileupload"]:
            # if resume was cancelled, set it to None so that it can be asked later again....
            if tracker.get_slot("resume_upload") == "false":
                result += [SlotSet("resume_upload", None)]
            # resume has a separate slot, don't add in screening questions list
            continue

        # TODO text put here as adhoc for full_name
        elif q["fieldType"] in ["ssn", "email", "phone"]:
            # ignore these input types as they are mandatory.
            continue
        
        q_transformed = {"id": q.get("id"), "input_type": q["inputType"]}
        if q.get("labelName") is not None:
            q_transformed["text"] = q.get("labelName")
        inputType = q.get("inputType")
        if inputType == "radio":
            if q.get("fieldType") == "yes/no":
                q_transformed["buttons"] = [{"payload": "Yes", "title": "Yes"}, {"payload": "No", "title": "No"}]
            elif q.get("fieldType") == "multiplechoice":
                q_transformed["buttons"] = [{"payload": val.get("value"), "title": val.get("value")} for val in q.get("choices", [])]
            else:
                q_transformed["buttons"] = [{"payload": val.get("value"), "title": val.get("name")} for val in q.get("PossibleValue", [])]
        elif inputType == "text":
            pass
        questions_data_transformed.append(q_transformed)

    return questions_data_transformed, result