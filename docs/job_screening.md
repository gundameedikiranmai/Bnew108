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

#### Address
```
[
    {
        "recipient_id": "681754ea-5df2-11ef-a41f-f45c89a10c23",
        "text": "Understood. This question is for capturing address"
    },
    {
        "recipient_id": "681754ea-5df2-11ef-a41f-f45c89a10c23",
        "custom": {
            "ui_component": "address",
            "placeholder_text": "(Text Area) Your Question here"
        }
    }
]
```

#### SSN
```
[
    {
        "recipient_id": "681754ea-5df2-11ef-a41f-f45c89a10c23",
        "text": "This field is to capture SSN"
    },
    {
        "recipient_id": "681754ea-5df2-11ef-a41f-f45c89a10c23",
        "custom": {
            "ui_component": "ssn",
            "placeholder_text": "SSN"
        }
    }
]
```

#### Rating
```
[
    {
        "recipient_id": "681754ea-5df2-11ef-a41f-f45c89a10c23",
        "text": "This field is for Rating"
    },
    {
        "recipient_id": "681754ea-5df2-11ef-a41f-f45c89a10c23",
        "custom": {
            "ui_component": "rating",
            "placeholder_text": "(Text Area) Your Question here"
        }
    }
]
```

#### Ranking
```
[
    {
        "recipient_id": "681754ea-5df2-11ef-a41f-f45c89a10c23",
        "text": "This field is for ranking  purposes"
    },
    {
        "recipient_id": "681754ea-5df2-11ef-a41f-f45c89a10c23",
        "custom": {
            "ui_component": "ranking",
            "placeholder_text": "(Text Area) Your Question here",
            "ranks": [
                {
                    "id": 1,
                    "value": "Choice 1",
                    "rank": 1,
                    "chosen": false
                },
                {
                    "id": 2,
                    "value": "Choice 2",
                    "rank": 2
                },
                {
                    "id": 3,
                    "value": "Choice 3",
                    "rank": 3
                }
            ]
        }
    }
]
```

Message to chatbot : id as comma separated string, eg, "3,1,2"

#### Multiple Choice
```
[
    {
        "recipient_id": "681754ea-5df2-11ef-a41f-f45c89a10c23",
        "text": "This field is for multiple choice"
    },
    {
        "recipient_id": "9917edbe-2641-11ee-8f08-f5235bd2ce38",
        "custom": {
            "ui_component": "multi-select",
            "options": [{
                "key": "Choice 1",
                "value": "Choice 1"
            }, {
                "key": "Choice 2",
                "value": "Choice 2"
            }, {
                "key": "Choice 3",
                "value": "Choice 3"
            }, {
                "key": "Choice 4",
                "value": "Choice 4"
            }],
            "anyRadioButton": None,
            "is_back_button_enabled": true

        }
    }
]
```

#### Net Promoter Score
```
[
    {
        "recipient_id": "681754ea-5df2-11ef-a41f-f45c89a10c23",
        "text": "This field is for Net promoter Score"
    },
    {
        "recipient_id": "681754ea-5df2-11ef-a41f-f45c89a10c23",
        "custom": {
            "ui_component": "netprometer",
            "choices": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        }
    }
]
```

#### Opinion Scale
```
[
    {
        "recipient_id": "681754ea-5df2-11ef-a41f-f45c89a10c23",
        "text": "This field is for Opinion Scale"
    },
    {
        "recipient_id": "681754ea-5df2-11ef-a41f-f45c89a10c23",
        "custom": {
            "ui_component": "opinionscale",
            "choices": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
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
            "checkbox_options": [
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
            ],
            "any_radio_button": {
                "Name": "Any",
                "Type": "RadioButton",
                "LookupId": 10013004
            },
            "is_back_button_enabled": true

        }
    }
]
```

The UI should render the items present in the options array. The key should displayed on the UI whereas the value should be used for sending to chatbot. All the selected values should be sent as a comma separated string.

For eg, if user selects Remote and Hybrid, UI should send "1,2" as the user message.

any_radio_button will be optional and will either be null or have a dictionary value. It will be used on the UI to select/deselect the checkboxes.

### Workflow URL
After a job is applied at the end of the preference submission, the job apply url returns a workflowURL in the response. This url value may or may not be present. If it is available, the chatbot will emit a custom utterance which the UI should pick as a trigger for redirecting the user to the provided workflowURL. The bot message will be:

```
[
    {
        "recipient_id": "9917edbe-2641-11ee-8f08-f5235bd2ce38",
        "custom": {
            "ui_component": "workflow",
            "workflow_url": "https://app.curately.ai/workflow/#/stages/uick113-uick13h-uick1vs-uick1ef-cuickzl"

        }
    }
]
```