### Bot API integration with UI
HOST: http://52.40.250.118:8888
API endpoint: $HOST/webhooks/rest/webhook

At the start of every session, the UI must generate a new UUID as a session ID and keep it during the entire conversation.

The bot request format is:

```
{
    "sender": UUID,
    "message": msg,
    "metadata": {
        "chatbot_type": "1", // "1" or "2"
        "job_location": "TX" // job location from cookie,
        "ip_address": "0.0.0.0",
        "client_id": "2",
        "user_id": None or "1234" //data type is string.
    }
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

### Identifying existing session
The UI should store the UUID in local storage and use it for sending chatbot messages. If local storage is empty, initialize new UUID and store it.


### Synchronising with Career Page
Whenever the user uploads the resume in Career Page, the UI container should set the value of "user_id" in metadata and refresh the session, i.e. clear existing messages in Chatbot window and send "/restart" and "/greet". The chatbot will pick up the user_id value and fetch the user details using the backend api and present the option of continue job exploration.

