"""
Utils
"""
from bson import json_util
import json
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