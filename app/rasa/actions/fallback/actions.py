from typing import Dict, Text, Any, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import UserUtteranceReverted, SlotSet, FollowupAction, UserUttered, ActionExecuted, ConversationPaused
from rasa_sdk.executor import CollectingDispatcher

class ActionCoreDefault(Action):

    def name(self) -> Text:
        return "action_core_default"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("action_core_default")
        dispatcher.utter_message(response="utter_greet") # utter_default is default rasa response which is used in 2 stage fallback
        # dispatcher.utter_message(template="utter_services_after_two_stage_fallback")
        return [UserUtteranceReverted()]