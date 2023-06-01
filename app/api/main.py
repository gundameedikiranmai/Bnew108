from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel
import os
import requests
import json


####### config #######
RASA_WEBHOOK_HOST = os.getenv("RASA_WEBHOOK_HOST", "rasa-core")
RASA_WEBHOOK_PORT = os.getenv("RASA_WEBHOOK_PORT", 5005)
RASA_WEBHOOK_URL = f"http://{RASA_WEBHOOK_HOST}:{RASA_WEBHOOK_PORT}"

class WebhookRequest(BaseModel):
    sender: str
    # metadata: dict
    message: str

app = FastAPI()

# ---------------------
# Health check endpoint
# ---------------------
@app.get("/health", include_in_schema=False)
def health_check():
    return {'status': 'ok'}


@app.get("/")
def read_root():
    return {"Hello": "World"}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}

@app.post("/webhooks/{channel}/webhook")
def get_webhook(
    channel: str,
    webhook_data: WebhookRequest
):
    rasa_webhook_url = f'{RASA_WEBHOOK_URL}/webhooks/{channel}/webhook'
    headers = {"Content-Type": "application/json"}
    
    # -----------------------------------
    # Forward the webhook to Rasa webhook
    # -----------------------------------
    if webhook_data.message not in ["/job_screening", "hi"]:
        webhook_data.message = '/input_screening_response{"screening_response": "' + webhook_data.message + '"}'
    res = requests.post(rasa_webhook_url, json=webhook_data.dict(), headers=headers)
    # logger.debug(f'[🤖 RasaGPT API webhook]\nPosting data: {json.dumps(webhook_data)}\n\n[🤖 RasaGPT API webhook]\nRasa webhook response: {res.text}')
    print(f'[🤖 API webhook]\nPosting data: {webhook_data.dict()}\n\n[🤖 RasaGPT API webhook]\nRasa webhook response: {res.text}')

    return res.json()