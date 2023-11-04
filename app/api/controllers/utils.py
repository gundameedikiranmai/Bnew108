"""
Utils
"""
from bson import json_util
import json
import time
from config.conf import settings
import requests
import traceback

from fastapi import Response

def JsonResponse(data, status):
    return Response(content=json.dumps(data, default=json_util.default), media_type="application/json", status_code=status)


def nlu(text):
    # API documentation: https://legacy-docs-v1.rasa.com/api/http-api/#operation/parseModelMessage
    params = {
        "token": settings.RASA_WEBHOOK["TOKEN"],
    }
    payload = {
        "text": text,
        "message_id": ""
    }

    response = requests.post(settings.RASA_WEBHOOK["URL"] + "/model/parse", json=payload, params=params)
    # response = response.json()
    # app.logger.info("nlu: " + json.dumps(response, indent=4))

    entity = None
    try:
        response = response.json()
        # settings.logger.debug("info: " + json.dumps(response, indent=4))
        print("info: " + json.dumps(response, indent=4))
        intent_name = response["intent"]["name"]
        assert(intent_name is not None)
        intent_conf = response["intent"]["confidence"]
        if len(response["entities"]) > 0:
            entity = response["entities"][0]
    except:
        traceback.print_exc()
        intent_name = None
        intent_conf = -1

    return intent_conf, intent_name, entity


def add_events_to_rasa(sender_id, data):
    params = {
        "token": settings.RASA_WEBHOOK["TOKEN"],
    }
    headers = {"Content-Type": "application/json"}
    rasa_x_url = settings.RASA_WEBHOOK["URL"] + f'/conversations/{sender_id}/tracker/events'
    rasa_response = requests.post(rasa_x_url, json=data, headers=headers,params=params)

    return rasa_response


def add_slot_set_events(sender_id, slots):
    """slots is a dict of slots that need to be set"""
    data = []
    payload = {
        "event": "slot",
        "timestamp": time.time(),
    }
    for slot in slots:
        # only append if slot has an actual value
        if slots[slot] is not None and len(slots[slot]) > 0:
            update_dict = {}
            update_dict["name"] = slot
            update_dict["value"] = slots[slot]
            append_dict = {**payload,**update_dict}
            data.append(append_dict)
    if len(data) > 0:
        return add_events_to_rasa(sender_id, data)
    return None

def parse_rasa_message(message):
    return message.split("{")[0].replace("/", "")