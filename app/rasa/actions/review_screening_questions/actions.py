import os
import json
from logging import getLogger
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from actions.screening_questions.actions import utter_screening_question
import actions.utils as utils
import actions.config_values as cfg

logger = getLogger(__name__)


class ReviewScreeningQuestionsForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_review_screening_questions_form"
    
    def validate_screening_question_options(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `screening_question_options` value."""
        logger.info(f"validating input {slot_value}")
        result_dict = {"screening_question_options": slot_value}
        if slot_value == "no_all_good":
            # end form here.
            dispatcher.utter_message(json_message={"screening_start": False})
            result_dict.update({
                "view_edit_preferences": "review_form_completed",
                "requested_slot": None,
            })
        return result_dict


    def validate_screening_question_display_q(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `screening_question_display_q` value."""
        logger.info(f"validating input {slot_value}")
        result_dict = {}
        
        screening_question_options = tracker.get_slot("screening_question_options")
        screening_question_history = tracker.get_slot("screening_question_history")
        screening_review_context = tracker.get_slot("screening_review_context")
        if screening_review_context is None:
            screening_review_context = []
        
        job_screening_questions = tracker.get_slot("job_screening_questions")
        for i, q in enumerate(job_screening_questions):
            # find the question that matches with the selected choice.
            if q["data_key"] == screening_question_options:
                # update the relevant value in screening_question_history slot.
                screening_question_history[i] = slot_value
                result_dict["screening_question_history"] = screening_question_history
        
        
        screening_review_context.append(screening_question_options)
        result_dict["screening_review_context"] = screening_review_context

        # decide if any question is remaining for editing
        if len(screening_review_context) < len(job_screening_questions):
            result_dict.update({
                "screening_question_options": None,
                "screening_question_display_q": None
            })
        else:
            # all questions have been edited at least once
            dispatcher.utter_message(json_message={"screening_start": False})
            result_dict["view_edit_preferences"] = "review_form_completed"
        
        return result_dict


class AskScreeningQuestionOptionsAction(Action):
    def name(self) -> Text:
        return "action_ask_screening_question_options"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        result = []
        screening_review_context = tracker.get_slot("screening_review_context")
        job_screening_questions = tracker.get_slot("job_screening_questions")
        if screening_review_context is None:
            dispatcher.utter_message(json_message={"screening_start": True})
            screening_review_context = []
            
        buttons = []
        for q in job_screening_questions:
            if q["data_key"] not in screening_review_context:
                buttons.append({"title": q["data_key"], "payload": q["data_key"]})
        buttons.append({"title": "No, all good", "payload": "no_all_good"})
        dispatcher.utter_message(buttons=buttons)
        
        return result


class AskScreeningQuestionDisplayQAction(Action):
    def name(self) -> Text:
        return "action_ask_screening_question_display_q"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        result = []
        screening_question_options = tracker.get_slot("screening_question_options")

        job_screening_questions = tracker.get_slot("job_screening_questions")
        for i, q in enumerate(job_screening_questions):
            # find the question that matches with the selected choice.
            if q["data_key"] == screening_question_options:
                # display the question
                utter_screening_question(dispatcher, job_screening_questions, i)
        
        return result


class ReviewScreeningQuestionsFormSubmit(Action):

    def name(self) -> Text:
        return "review_screening_questions_form_submit"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        """Define what the form has to do after all required slots are filled"""
        
        return []


############# utils #################
class DummyAction(Action):
    def name(self) -> Text:
        return "action_dummy_test"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        # either load from slot or look for job id value from metadata.
        result = []
        synced_data = utils.get_synced_sender_data("70e2d6c0-ce83-11ee-9013-8dfddd3614aa")
        # set the slots from synced data
        for slot in synced_data["data"]:
            result.append(SlotSet(slot, synced_data["data"][slot]))
        result.append(SlotSet("select_job_title", "DUMMY_JOB"))
        return result