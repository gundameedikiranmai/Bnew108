from logging import getLogger
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, Action
from rasa_sdk.events import EventType, SlotSet
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