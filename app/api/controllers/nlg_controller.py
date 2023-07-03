"""
api_controller.py
"""
import os
import re
import copy
import yaml
import random
import json
from fastapi import APIRouter, Request
from config.conf import settings
import controllers.utils as utils
from controllers.models import session

# intents to ignore
router = APIRouter()

def read_response_files():
    file_path = os.path.join("controllers", "rasa_responses", "responses.yml")
    # load this company's responses
    temp_file = open(file_path)
    ymlstring = temp_file.read()
    temp_file.close()
    return yaml.load(ymlstring, Loader=yaml.FullLoader)["responses"]

rasa_responses = read_response_files()

@router.post("/")
async def get_responses(request: Request):
    print("get responses---------------------------------------")
    nlg_data = await request.json()
    template = nlg_data.get("response")
    params = nlg_data.get("arguments")
    if params is not None:
        print("type : ", type(params))
        print("content : ", str(params))

    resolved_message = get_response_text(template, params)
    if resolved_message:
        resp = copy.copy(resolved_message)
        slots = re.findall(r'\{(.*?)\}', resp['text'])
        print("to replace....", slots)
        for slot in slots:
            slot_val = nlg_data["tracker"]["slots"].get(slot,params.get('slots'))
            if params.get('slots'):
                resp['text'] = resp['text'].replace("{" + slot + "}", str(params.get('slots').get(slot)))
            else:
                resp['text'] = resp['text'].replace("{" + slot + "}", str(slot_val))
        print("rasa response:", resp, resolved_message)
    return utils.JsonResponse(resp, 200)


def get_response_text(template, params):
    resp = copy.deepcopy(rasa_responses[template])
    print("get_response_text **********************")
    if params is not None:
        print("type : ", type(params))
        print("content : ", str(params))

    if len(resp) > 1:
        if "trigger_flag" in params.keys() and params["trigger_flag"] is True:
            resp_list = resp[random.randrange(1, len(resp), 1):]
            print("Random selection list :: {}".format(str(resp_list)))
            choice = random.choice(resp_list)
        else:
            choice = resp[0]
    # if there are only buttons but different text variations, choose text randomly 
    elif len(resp) == 1 and 'text' in resp[0].keys() and isinstance(resp[0]['text'], list):
        if "trigger_flag" in params.keys() and params["trigger_flag"] is True and len(resp[0]['text']) > 1:
            resp_cpy = resp
            resp_text = resp_cpy[0]['text'][random.randrange(1, len(resp_cpy[0]['text']), 1)]
            resp_cpy[0]['text'] = resp_text
            print("Random selection list :: {}, {}".format(len(resp_cpy[0]['text']), str(resp_cpy)))
            choice = resp_cpy[0]
        else:
            resp_cpy = resp
            resp_text = resp_cpy[0]['text'][0]
            resp_cpy[0]['text'] = resp_text
            print("first selection list :: {}".format(str(resp_cpy)))
            choice = resp_cpy[0]
    else:
        print("first selection :::")
        choice = resp[0]
    print("selected choice : ", choice)
    return choice