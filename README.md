# chatbot

Contains Fast Api gateway for accepting incoming messages and rerouting to Rasa

Rasa core + actions containing the chatbot implementation

### Installation
Install conda env via the environment.yml file. It uses python 3.10.6 and rasa 3.4


### Bot API integration with UI
HOST: http://52.40.250.118:8888
API endpoint: $HOST/webhooks/rest/webhook

At the start of every session, the UI must generate a new UUID as a session ID and keep it during the entire conversation.

The bot request format is:

```
{
    "sender": UUID,
    "message": msg,
    "metadata": {},
}
```

The first message should be "/restart" to clear out any previous message history in case of duplicate UUID or collisions.

The bot response format is (buttons array is optional and may not always be present):

```
{
    "recipient_id": "a6aaa57c-0119-11ee-be37-9331dbf74573",
    "text": "Do you have any concerns about working in a call center environment on a recorded line?",
    "buttons": [
        {
            "payload": "Yes",
            "title": "Yes"
        },
        {
            "payload": "No",
            "title": "No"
        }
    ]
}
```

If buttons array is provided, then the text input box should not be shown.