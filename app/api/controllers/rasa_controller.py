"""
rasa_controller.py
"""
import os
import re
import copy
import json
import requests
from fastapi import APIRouter, Request
from config.conf import settings
import controllers.utils as utils
from controllers.models import session
from controllers.schema import RasaWebhook

# intents to ignore
router = APIRouter()


@router.get("/")
@router.post("/")
def hearbeat():
    """Summary: Heartbeat API to check online status

    Returns:
        str: Online Message status
    """
    settings.logger.info("this is a log")
    return "Online"

def retrieve_expected_intent(rasa_data):
    """
    returns expected_intent from custom rasa_data if exists else False
    """
    try:
        return rasa_data[-1].get("custom", {}).get("expected_intent") == "input_time"
    except IndexError:
        return False


def parse_response(text, user_data):
    """
        Summary: processing response which is to be sent to rasa webhook
        Args:
            text (string): last message for the user
            user_data (dict): user data dictionary

        Returns:
            is_success (bool): whether set session was successful or not.
            text message for rasa webhook
    """
    chat_session = session.get_session(user_data, "uuid")
    if chat_session is not None:
        last_message = chat_session.get("last_message", {})
        # last_message = last_message[::-1]
        if last_message is not None:
            settings.logger.info("type " + str(type(last_message)) + " last message = " + str(last_message) + ", text = " + text)
            if isinstance(last_message, dict):
                last_message = [last_message]
            # match with buttons only when screening is in place
            if chat_session.get("screening_start", False):
                buttons_present = False
                for d in last_message:
                    print("here.............")
                    if "buttons" in d and len(d["buttons"]) > 0:
                        buttons_present = True
                        for button in d["buttons"]:
                            if str(button["title"]).lower().strip() == text.lower().strip():
                                settings.logger.debug(button)
                                return True, '/input_screening_response{"screening_response": "' + button["payload"] + '"}'
                if buttons_present:
                    # buttons were present but still user entered something else
                    return False, "Please select a valid option"
                return True, '/input_screening_response{"screening_response": "' + text + '"}'
            
    else:
        return False, "could not get session details"
    return True, text

@router.post("/rest/webhook")
def rasa_webhook(rasa_data: RasaWebhook):
    data = rasa_data.dict()
    
    headers = {"Content-Type": "application/json"}
    user_data = {
        "uuid": data.get("sender").split(";;")[0],
        # "email": data.get("metadata", {}).get("email", ""),
        "last_message": {},
        "channel": "browser",
    }
    # don't update session for SMS channel and when message is restart
    if data["message"] != "/restart":
        # setting of session
        settings.logger.info("Message = " + str(data["message"]))
        settings.logger.debug("user data = " + str(user_data))
        chat_session = session.get_session(user_data, "uuid")
        if chat_session is None:
            user_data["first_intent"] = data["message"]
            session.set_session(user_data, "uuid")
        else:
            user_data["first_intent"] = chat_session["first_intent"]

        is_parsed, parsed_msg = parse_response(data["message"], user_data)
        settings.logger.info("parsed_msg " + str(parsed_msg))
        if is_parsed and len(parsed_msg) > 0:
            data["message"] = parsed_msg
            settings.logger.debug(data)
        else:
            err_msg = ["Your response was invalid: " + parsed_msg]
            return utils.JsonResponse({"error": "could not process the input provided by user"}, 500)
    
    rasa_core_url = settings.RASA_WEBHOOK["URL"] + "/webhooks/rest/webhook"

    response = requests.post(rasa_core_url, json=data, headers=headers)
    print(f'[🤖 API webhook]\nPosting data: {data}\n\n')

    if response.status_code == 200:
        rasa_data = response.json()
        settings.logger.info("response from rasa: " + json.dumps(rasa_data, indent=4))
        rasa_data, user_data = remove_state_messages(rasa_data, user_data)
        
        if len(rasa_data) > 0:
            session.set_last_message(user_data,rasa_data,"uuid")
        else:
            session.set_last_message(user_data, None, "uuid")
        return utils.JsonResponse(rasa_data, 200)
    else:
        settings.logger.error("error: " + response.text)
        return utils.JsonResponse({"error": "could not get response from rasa"}, 500)


def remove_state_messages(rasa_data, user_data):
    rasa_data_return = []
    for msg in rasa_data:
        if msg.get("custom", {}).get("screening_start") is not None:
            user_data["screening_start"] = msg.get("custom", {}).get("screening_start")
        else:
            rasa_data_return.append(msg)
    return rasa_data_return, user_data
