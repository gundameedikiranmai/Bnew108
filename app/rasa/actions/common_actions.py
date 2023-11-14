from logging import getLogger
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, Action
from rasa_sdk.events import EventType, SlotSet, Restarted
from rasa_sdk.executor import CollectingDispatcher
import actions.utils as utils
import actions.config_values as cfg

logger = getLogger(__name__)


class AskCustomBaseAction(Action):
    action_name = None
    entity_name = None
    intent_name = None
    ui_component = None

    def name(self) -> Text:
        if self.action_name is None:
            return "action_ask_custom_base_dummy_action"
        return "action_ask_" + self.action_name

    def set_params(self, entity_name, intent_name=None, ui_component=None, action_name=None):
        self.entity_name = entity_name
        # set expected intent as per input
        if intent_name is None:
            self.intent_name = "input_" + self.entity_name
        else:
            self.intent_name = intent_name
        
        if ui_component is None:
            self.ui_component = self.entity_name
        else:
            self.ui_component = ui_component
        
        if action_name is None:
            self.action_name = self.entity_name
        else:
            self.action_name = action_name
        

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict, **kwargs
    ) -> List[EventType]:
        result = []
        if "responses" in kwargs:
            for response in kwargs["responses"]:
                dispatcher.utter_message(response=response)
        utt = {
            "ui_component": self.ui_component,
            "intent": self.intent_name,
            "entity": self.entity_name
        }
        if "data" in kwargs:
            utt.update(kwargs["data"])
        dispatcher.utter_message(json_message=utt)
        return result


class AskUtteranceWithPlaceholderAction(AskCustomBaseAction):
    """Custom Class to show an utterance followed by a placeholder text"""
    placeholder = None

    def set_params(self, entity_name, placeholder, action_name=None):
        self.placeholder = placeholder
        super().set_params(entity_name, intent_name=None, ui_component=None, action_name=action_name)
        

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict, **kwargs
    ) -> List[EventType]:
        result = []
        dispatcher.utter_message(response=f"utter_ask_{self.entity_name}")
        add_placeholder_utterance(dispatcher, self.placeholder)


class ActionRestart(Action):
    
    def name(self) -> Text:
        return "action_restart"
    
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict, **kwargs
    ) -> List[EventType]:
        slots_to_retain = []
        for slot in cfg.SLOTS_TO_KEEP_AFTER_RESTART:
        # for slots in ["full_name", "email", "phone_number"]
            if tracker.get_slot(slot) is not None:
                slots_to_retain.append(SlotSet(slot, tracker.get_slot(slot)))
        return [Restarted()] + slots_to_retain


class ActionUtterGreet(Action):
    
    def name(self) -> Text:
        return "action_utter_greet"
    
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict, **kwargs
    ) -> List[EventType]:
        _, result = utils.get_metadata_field(tracker, "ip_address")
        if tracker.get_slot("first_name") is not None:
            greet_param = "known"
        else:
            greet_param = "unknown"
        dispatcher.utter_message(response="utter_greet", greet=greet_param)
        return result


def add_placeholder_utterance(dispatcher, placeholder_text):
    utt = {
        "ui_component": "placeholder",
        "placeholder_text": placeholder_text
    }
    dispatcher.utter_message(json_message=utt)


def add_date_utterance(dispatcher):
    utt = {
        "ui_component": "datepicker",
        "placeholder_text": "Please enter a date (mm-dd-yyyy)"
    }
    dispatcher.utter_message(json_message=utt)