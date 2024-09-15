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
from datetime import datetime, timedelta

logger = getLogger(__name__)

class ActionStartExploreJobs(Action):

    def name(self) -> Text:
        return "action_start_explore_jobs"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        result = []
        # set slot values 
        chatbot_type, chatbot_type_slot = utils.get_metadata_field(tracker, "chatbot_type")
        job_location, job_location_slot = utils.get_metadata_field(tracker, "job_location")
        
        if chatbot_type == "1" and tracker.get_slot("resume_last_search") is not None:
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
    
    def validate_resume_last_search(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `resume_last_search` value."""
        result_dict = {
            "resume_last_search": slot_value
        }
        if slot_value == "true":
            dispatcher.utter_message(response="utter_start_resume_last_search")
        elif slot_value=="false":
            # user wants to start new search
            # dispatcher.utter_message(response="utter_resume_last_search_cancel")
            
            # reset all params.
            for slot in cfg.RESUME_LAST_SEARCH_RELEVANT_SLOTS:
                result_dict[slot] = None
        return result_dict
    
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
            result_dict["update_contact_details"] = "ignore"
            result_dict["resume_upload"] = "false"
        return result_dict


    def validate_update_contact_details(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `update_contact_details` value."""
        result_dict = {
            "update_contact_details": slot_value
        }
        if slot_value == "true":
            try:
                contact_details = json.loads(tracker.get_slot("contact_details_temp"))
                result_dict.update(contact_details)
                success, err_msg = utils.reupload_resume_update_contact_details(tracker.get_slot("user_id"), contact_details["email"])
                if success:
                    dispatcher.utter_message(response="utter_update_contact_details_affirm")
                else:
                    dispatcher.utter_message(response="utter_update_contact_details_error", slots={"update_email_error": err_msg})
            except Exception as e:
                logger.error("Could not read contact_details_temp.")
                logger.error(e)
        elif slot_value == "false":
            dispatcher.utter_message(response="utter_update_contact_details_deny")
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
            if tracker.get_slot("requested_slot") == "resume_upload":
                # utter this message if the resume was cancelled by clicking on the cancel button.
                dispatcher.utter_message(response="utter_resume_upload_cancel")
            result_dict["resume_upload"] = None
            result_dict["is_resume_upload"] = None
            result_dict["update_contact_details"] = "ignore"
        else:
            result_dict["user_id"] = slot_value
        
        if tracker.get_slot("first_name") is not None and tracker.get_slot("is_resume_parsing_done") is not None:
            # the validate method is running after doing resume parsing
            dispatcher.utter_message(response="utter_nice_to_meet_you")
            # reset slot so that a page reload does not force the above utterance to be displayed
            result_dict["is_resume_parsing_done"] = None
        if tracker.get_slot("update_contact_details") == "set_to_none":
            result_dict["update_contact_details"] = None
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
                if str(job["jobId"]) == slot_value:
                    result_dict["select_job_title"] = job["jobTitle"]
                    break
        return result_dict


class AskIsResumeUploadAction(Action):
    def name(self) -> Text:
        return "action_ask_is_resume_upload"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        if tracker.get_slot("resume_last_search") == "false":
            dispatcher.utter_message(template="utter_ask_is_resume_upload_start_new_search")
        else:
            dispatcher.utter_message(template="utter_ask_is_resume_upload")


class AskResumeUploadAction(AskCustomBaseAction):
    def __init__(self):
        self.set_params(entity_name="user_id", intent_name="input_resume_upload_data", ui_component="resume_upload", action_name="resume_upload")

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
            # result += [SlotSet("refine_job_search_field", None)]
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
        # else:
            # result += [SlotSet("refine_job_search_field", None)]
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
    
    def fetch_jobs(self, tracker, is_refine_jobs):
        user_id = tracker.get_slot("user_id")

        if not is_refine_jobs and user_id is not None:
            # is_refine_jobs is False and user_id is available, send only userId in payload.
            payload = {
                "query": "",
                "city": "",
                "state": "",
                "zipcode": "",
                "radius": "50",
                "daysback": "",
                "isRemote": "",
                "jobType": "",
                "clientids": tracker.get_slot("client_id"),
                "next": 0,
                "userId": user_id,
                "type": "",
            }
        else:
            # send explicit search parameters
            location = utils.get_default_slot_value(tracker.get_slot("job_location")).strip()
            city, state, zipcode = "", "", ""
            if len(location) == 5:
                zipcode = location
            elif not (" " in location or "," in location) or len(location) == 2:
                state = location
            elif "," in location:
                locs = location.split(",")
                city = locs[0].strip()
                state = locs[1].strip()
                if len(locs) > 2:
                    zipcode = locs[2].strip()
            payload = {
                "query": utils.get_default_slot_value(tracker.get_slot("job_title")),
                "city": city,
                "state": state,
                "zipcode": zipcode,
                "radius": "50",
                "daysback": "",
                "isRemote": "",
                "jobType": "",
                "clientids": tracker.get_slot("client_id"),
                "next": 0,
                "type": "",
            }
        try:
            logger.info("job search params: " + str(payload))
            job_resp = requests.post(cfg.ACCUICK_SEARCH_JOBS_URL, json=payload)
            logger.info("job_resp status: {}".format(job_resp.status_code))
            if job_resp.status_code == 200:
                jobs = job_resp.json().get("List", [])
                logger.info(f"total job count: {len(jobs)}")
                applied_jobs = set(tracker.get_slot("applied_jobs") + utils.get_applied_jobs_in_portal(user_id))
                jobs_filtered = [j for j in jobs if str(j["jobId"]) not in applied_jobs]
                logger.info(f"filtered job count: {len(jobs_filtered)}")
                jobs_to_show = jobs_filtered[:cfg.N_JOBS_TO_SHOW]
                log_subset =  [{key: value for key, value in j.items() if key in ["jobId", "jobTitle"]} for j in jobs_to_show[:3]]
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
        is_refine_jobs = False
        resume_last_search = tracker.get_slot("resume_last_search")
        refine_job_search_field = tracker.get_slot("refine_job_search_field")
        if refine_job_search_field in ["job_title", "job_location"]:
            result += [SlotSet("refine_job_search_field", None)]
            is_refine_jobs = True
        
        jobs = self.fetch_jobs(tracker, is_refine_jobs)
        
        if jobs is None:
            dispatcher.utter_message(response="utter_error_explore_jobs")
        elif len(jobs) == 0:
            if resume_last_search=="true":
                dispatcher.utter_message(response="utter_explore_jobs_no_jobs_found_resume_last_search")
            else:
                dispatcher.utter_message(response="utter_explore_jobs_no_jobs_found")
        else:
            if resume_last_search=="true":
                dispatcher.utter_message(response="utter_explore_jobs_resume_last_search")
            elif refine_job_search_field in ["job_title", "job_location"]:
                dispatcher.utter_message(response="utter_explore_jobs_refine_search", slots={"refine_value": tracker.get_slot(refine_job_search_field)})
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
        
        questions_data, slots = utils.get_screening_questions_for_job_id(tracker)
        result += slots
        logger.info("asking questions: {}".format(json.dumps(questions_data, indent=4)))
        result += [
            # reset explore jobs form
            SlotSet("refine_job_search_field", None),
            # reset job_screening_form
            SlotSet("screening_question", None),
            SlotSet("screening_question_history", None),
        ]
        if len(questions_data) > 0:
            dispatcher.utter_message(json_message={"screening_start": True})
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
                dispatcher.utter_message(json_message={"screening_start": True})
                result += [
                    SlotSet("screening_question", "ignore"),
                    FollowupAction("job_screening_form")
                ]
                dispatcher.utter_message(response="utter_explore_jobs_apply_success")
                dispatcher.utter_message(response="utter_screening_start")
            else:
                # no screening question has to be asked.
                result += job_screening_submit_integration(tracker, tracker.get_slot("select_job"), dispatcher, greet_type="after_apply_no_screening_questions")
        return result