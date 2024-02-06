import os
import yaml
import random
from logging import getLogger
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import actions.utils as utils

logger = getLogger(__name__)

def load_faqs():
    faq_file = os.path.join("chatbot_data", "faq", "faq.yml")
    return yaml.load(open(faq_file), Loader=yaml.FullLoader)["faqs"]

faqs = load_faqs()

class ValidateAskAQuestionForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_ask_a_question_form"
    
    def validate_user_question(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `user_question` value."""
        faq_suggestion_context = tracker.get_slot("faq_suggestion_context")
        if faq_suggestion_context is None:
            faq_suggestion_context = []
        
        # close form if user wants to end in between.
        if slot_value == "NO_MORE_QUESTIONS":
            dispatcher.utter_message(response="utter_no_more_questions_response")
            return {"user_question": slot_value}
        
        result_dict = {
            "user_question": None,
            "faq_suggestion_context": faq_suggestion_context + [slot_value]
        }
        question_data = faqs[slot_value]
        dispatcher.utter_message(text=question_data["answer"])

        # check if all questions have been asked.
        if len(faq_suggestion_context) + 1 == len(faqs):
            dispatcher.utter_message(response="utter_no_more_questions_response")
            return {"user_question": slot_value}
        
        # if questions are still remaining, suggest more
        dispatcher.utter_message(response="utter_suggest_more_questions")
        return result_dict


class AskUserQuestionAction(Action):
    def name(self) -> Text:
        return "action_ask_user_question"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        result = []
        # sample_faqs = dict(random.sample(faqs.items(), 3))
        faq_suggestion_context = tracker.get_slot("faq_suggestion_context")
        if faq_suggestion_context is None:
            faq_suggestion_context = []
        buttons = []
        for faq_id, question_data in faqs.items():
            if faq_id not in faq_suggestion_context:
                btn_data = {
                    "payload": '/input_user_question{"user_question": "' + faq_id + '" }',
                    "title": question_data["question"]
                }
                buttons.append(btn_data)
        if len(faq_suggestion_context) > 0:
            buttons.append({
                "payload": '/input_user_question{"user_question": "NO_MORE_QUESTIONS" }',
                "title": "I have no more questions."
            })
        dispatcher.utter_message(buttons=buttons)
        return result


class AskAQuestionFormSubmit(Action):

    def name(self) -> Text:
        return "ask_a_question_form_submit"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[EventType]:
        """Define what the form has to do after all required slots are filled"""
        result = [
            SlotSet("user_question", None),
            SlotSet("faq_suggestion_context", None),
        ]
        return result
