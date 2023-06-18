import os
from logging import getLogger
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import yaml
import actions.utils as utils

logger = getLogger(__name__)

def load_screening_questions():
    dir_path = os.path.join("screening_questions")
    question_dict = {}
    n_questions = {}
    for file in os.listdir(dir_path):
        name, ext = os.path.splitext(file)
        if ext in [".yml", ".yaml"]:
            file_data = yaml.load(open(os.path.join(dir_path, file)), Loader=yaml.FullLoader)
            question_dict[name.lower()] = file_data["job_questions"] + file_data["common_questions"]
            n_questions[name.lower()] = len(question_dict[name.lower()])
    return question_dict, n_questions

question_dict, n_questions = load_screening_questions()


class ValidateJobScreeningForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_job_screening_form"
    
    def validate_screening_question(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `screening_question` value."""
        job_id, _ = utils.get_metadata_field(tracker, "job_id")
        logger.info(f"validating input {slot_value}")
        history = tracker.get_slot("screening_question_history")
        n_history = len(history)
        result_dict = {
            "screening_question_history": history + [slot_value]
        }
        if n_history + 1 < n_questions.get(job_id):
            result_dict["screening_question"] = None
        else:
            result_dict["screening_question"] = slot_value
            dispatcher.utter_message(response="utter_submit")
            dispatcher.utter_message(json_message={"screening_start": False})
            print(history)
        return result_dict


class AskScreeningQuestionAction(Action):
    def name(self) -> Text:
        return "action_ask_screening_question"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        job_id, result = utils.get_metadata_field(tracker, "job_id")
        history = tracker.get_slot("screening_question_history")
        n_history = len(history)
        questions_data = question_dict.get(job_id)
        if n_history == 0:
            dispatcher.utter_message(json_message={"screening_start": True})
        if n_history < n_questions.get(job_id):
            # if n_history > 0 and questions[n_history - 1].get("validations") is not None:
            #     validation_info = questions[n_history - 1].get("validations")
            #     if history[n_history - 1] == validation_info["correct_answer"]:
            # logger.info(f"displaying question: {questions[n_history]}")
            logger.info(f"rendering: {questions_data[n_history]}")
            
            # if a question has some metadata, send all of it as a json message to avoid sending multiple messages.
            if questions_data[n_history].get("metadata"):
                dispatcher.utter_message(json_message=questions_data[n_history])
            else:
                dispatcher.utter_message(**questions_data[n_history])
            # dispatcher.utter_message(text=questions_data[n_history].get("text"), buttons=questions_data[n_history].get("buttons"), json_message=questions_data[n_history].get("custom"))
        else:
            dispatcher.utter_message(text="Error.... all questions have been answered...")
        return result


class JobScreeningFormSubmit(Action):

    def name(self) -> Text:
        return "job_screening_form_submit"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        """Define what the form has to do after all required slots are filled"""
        result = []
        # dispatcher.utter_message(text="Your responses are:" + ", ".join(tracker.get_slot("screening_question_history")))

        return result
