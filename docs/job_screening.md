## Job Screening flow

### Follow up after Job search
[faq config](/app/rasa/chatbot_data/faq/faq.yml)

Based on the selected job_id from the search jobs from in [Ask a Question and explore jobs](/docs/greet.md) workflow, the Job search api: `https://sequence.accuick.com/Sequence/searchjobs` is used to fetch the relevant questions associated with the selected job.

#### Placeholder
A new ui_component with placeholder text will be present if needed.

```
[
    {
        "recipient_id": "9917edbe-2641-11ee-8f08-f5235bd2ce38",
        "text": "What is your email address? We promise to not send you spam emails"
    },
    {
        "recipient_id": "9917edbe-2641-11ee-8f08-f5235bd2ce38",
        "custom": {
            "ui_component": "placeholder",
            "placeholder_text": "me@email.com"
        }
    }
]
```

#### Datepicker
This component will be shown when datepicker has to be shown. No special intent_name, entity_name is needed, just plain text input should be sent after selecting a date.

```
[
    {
        "recipient_id": "9917edbe-2641-11ee-8f08-f5235bd2ce38",
        "text": "What is your date of birth?"
    },
    {
        "recipient_id": "9917edbe-2641-11ee-8f08-f5235bd2ce38",
        "custom": {
            "ui_component": "datepicker",
            "placeholder_text": "Please select a date"
        }
    }
]
```



### Initial implementation
The job screening flow is initiated by sending the following first message.

```
{
    "sender": UUID,
    "message": "/job_screening",
    "metadata": {
        "job_id": "2"
    }
}
```

The chatbot will then start asking the questions related to the given job_id in the metadata. If no job_id is given, a value of "1" is assumed as default.

### Multi-Select UI component
The chatbot message to display the multi-select UI component will be as follows:
```
[
    {
        "recipient_id": "9917edbe-2641-11ee-8f08-f5235bd2ce38",
        "custom": {
            "ui_component": "multi-select",
            "options": [
                {
                    "key": "Remote",
                    "Value": "1"
                },
                {
                    "key": "Hybrid",
                    "Value": "2"
                },
                {
                    "key": "On-Site",
                    "Value": "3"
                }
            ]
        }
    }
]
```

The UI should render the items present in the options array. The key should displayed on the UI whereas the value should be used for sending to chatbot. All the selected values should be sent as a comma separated string.

For eg, if user selects Remote and Hybrid, UI should send "1,2" as the user message.