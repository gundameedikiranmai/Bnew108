from logging import getLogger
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import yaml

logger = getLogger(__name__)

question_dict = yaml.load(open("screening_questions.yml"), Loader=yaml.FullLoader)
questions = question_dict["job_questions"] + question_dict["common_questions"]
n_questions = len(questions)


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
        logger.info(f"validating input {slot_value}")
        history = tracker.get_slot("screening_question_history")
        n_history = len(history)
        result_dict = {
            "screening_question_history": history + [slot_value]
        }
        if n_history + 1 < n_questions:
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
        history = tracker.get_slot("screening_question_history")
        n_history = len(history)
        if n_history == 0:
            dispatcher.utter_message(json_message={"screening_start": True})
        if n_history < n_questions:
            # if n_history > 0 and questions[n_history - 1].get("validations") is not None:
            #     validation_info = questions[n_history - 1].get("validations")
            #     if history[n_history - 1] == validation_info["correct_answer"]:
            # logger.info(f"displaying question: {questions[n_history]}")
            logger.info(f"rendering: {questions[n_history]}")
            
            # if a question has some metadata, send all of it as a json message to avoid sending multiple messages.
            if questions[n_history].get("metadata"):
                dispatcher.utter_message(json_message=questions[n_history])
            else:
                dispatcher.utter_message(**questions[n_history])
            # dispatcher.utter_message(text=questions[n_history].get("text"), buttons=questions[n_history].get("buttons"), json_message=questions[n_history].get("custom"))
        else:
            dispatcher.utter_message(text="Error.... all questions have been answered...")
        return []


class JobScreeningFormSubmit(Action):

    def name(self) -> Text:
        return "job_screening_form_submit"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        """Define what the form has to do after all required slots are filled"""
        result = []
        # dispatcher.utter_message(text="Your responses are:" + ", ".join(tracker.get_slot("screening_question_history")))

        return result
