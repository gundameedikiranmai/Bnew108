## Greet

The job screening flow is initiated by sending the following first message.

```
{
    "sender": UUID,
    "message": "/greet",
    "metadata": {}
}
```

This message will trigger the greet flow which will display two options:
- Explore jobs
- Ask a Question

```
[{
    "recipient_id": UUID,
    "text": "Hi! How can we be at your side today?",
    "buttons": [
        {
            "payload": "/explore_jobs",
            "title": "Explore Jobs"
        },
        {
            "payload": "/ask_a_question",
            "title": "Ask a question"
        }
    ]
}]
```

### Pending Work
- **The upload resume path is not implemented yet. only answer questions will work.**
- **Job application after user selects a job. Currently, the bot shows the greeting message again.**

### Ask a Question
selecting ask_a_question option will present a set of questions. There are 4 questions configured as of now in [faq config](/app/rasa/chatbot_data/faq/faq.yml). Out of the 4, a randomly selected sample of 3 questions will be displayed.

```
[
    {
        "recipient_id": "60b277fc-1a50-11ee-b692-7de41f0c3d53",
        "text": "OK! Here are a few popular questions to help you get started."
    },
    {
        "recipient_id": "60b277fc-1a50-11ee-b692-7de41f0c3d53",
        "buttons": [
            {
                "payload": "/input_user_question{\"user_question\": \"4\" }",
                "title": "Does the company provide health insurance?"
            },
            {
                "payload": "/input_user_question{\"user_question\": \"2\" }",
                "title": "Will I be compensated for overtime?"
            },
            {
                "payload": "/input_user_question{\"user_question\": \"1\" }",
                "title": "How much salary you offer in your company?"
            }
        ]
    }
]
```

Upon clicking any question, the answer will displayed along with further suggestions for FAQ's.

```
[
    {
        "recipient_id": "60b277fc-1a50-11ee-b692-7de41f0c3d53",
        "text": "We determine base pay as a function of position and experience level. As a pay for performance organization, we also use base pay as a means to recognize and reward employees that make the greatest contributions to our successes. Our Recruiters are happy to provide more details on compensation as you move throughout the hiring process."
    },
    {
        "recipient_id": "60b277fc-1a50-11ee-b692-7de41f0c3d53",
        "text": "Here are a few questions that might be relevant for you"
    },
    {
        "recipient_id": "60b277fc-1a50-11ee-b692-7de41f0c3d53",
        "buttons": [
            {
                "payload": "/input_user_question{\"user_question\": \"4\" }",
                "title": "Does the company provide health insurance?"
            },
            {
                "payload": "/input_user_question{\"user_question\": \"3\" }",
                "title": "What benefits should i expect from the company?"
            },
            {
                "payload": "/input_user_question{\"user_question\": \"1\" }",
                "title": "How much salary you offer in your company?"
            }
        ]
    }
]
```

#### Switch to Explore jobs between FAQ
The sender can send an explore jobs prompt to the chatbot to switch the chabot flow after asking a question.
```
{
    "sender": "93efe5b4-1a50-11ee-b62b-994dfc471e25",
    "message": "/explore_jobs",
    "metadata": {}
}
```

This will trigger the explore jobs flow described below


### Explore Jobs
After clicking on explore jobs button, the user will be asked to provide their information like resume, title, job location etc.

```
[
    {
        "recipient_id": "93efe5b4-1a50-11ee-b62b-994dfc471e25",
        "text": "We want to personalize your job recommendations."
    },
    {
        "recipient_id": "93efe5b4-1a50-11ee-b62b-994dfc471e25",
        "text": "To find you the right job, we need to know more about your background and interests."
    },
    {
        "recipient_id": "93efe5b4-1a50-11ee-b62b-994dfc471e25",
        "text": "Would you like to upload your resume or answer questions?",
        "buttons": [
            {
                "payload": "/affirm",
                "title": "Upload Resume"
            },
            {
                "payload": "/deny",
                "title": "Answer Questions"
            }
        ]
    }
]
```

#### Answer Questions: Job title and location
Bot will respond by asking job title and location. Both questions require a custom UI component.

```
[
    {
        "recipient_id": "a0c526cc-1a51-11ee-9858-a19875d5b355",
        "text": "Great!"
    },
    {
        "recipient_id": "a0c526cc-1a51-11ee-9858-a19875d5b355",
        "text": "Next question. What's your preferred job title? We'll try finding similar jobs."
    },
    {
        "recipient_id": "a0c526cc-1a51-11ee-9858-a19875d5b355",
        "custom": {
            "ui_component": "job_title",
            "titles": ["client", "software developer"],
            "intent": "input_job_title",
            "entity": "job_title"
        }
    }
]

```

After answering title and location, the bot will query job search api (https://sequence.accuick.com/Sequence/searchjobs) to fetch matching jobs and display.

**UI component**: The UI component will be selected if a "ui_component" key is present in the custom field for a given message.

##### Job title
A dropdown list using the values in the "titles" key has to be displayed. The responses have to be sent in the format - '/intent{"entity": "selected_value"}'. The intent and entity values are to be read from the input message.

example:
```
{
    "sender": "a0c526cc-1a51-11ee-9858-a19875d5b355",
    "message": "/input_job_title{\"job_title\": \"client\"}",
    "metadata": {}
}
```

##### Job location
The ui should implement a location component, using some publicly available libraries and send the data back to the chatbot. For the time being, the following message can be sent to proceed without having a location UI component.

```
{
    "sender": "a0c526cc-1a51-11ee-9858-a19875d5b355",
    "message": "/input_job_location{\"job_location\": \"california\"}",
    "metadata": {}
}
```

##### Display jobs
The ui has to show a carousel displaying the jobs as cards. When user clicks "I'm intertested", the payload jobid should be sent as a message to chatbot, using the intent and entity values in the bot message.

Bot message:
```
[
    {
        "recipient_id": "a0c526cc-1a51-11ee-9858-a19875d5b355",
        "custom": {
            "ui_component": "select_job",
            "jobs": [
                {
                    "date": "2023-06-21 10:28:19.0",
                    "isremote": false,
                    "jobtitle": " RAC Collections Agent - TX/AZ",
                    "city": "Tempe",
                    "description": "html formatted string....",
                    "jobtype": "Full-Time Contract",
                    "zipcode": "",
                    "jobid": "228332",
                    "assessment": "ALL",
                    "state": "AZ",
                    "payrange": "15.00",
                    "compname": "ASK Consulting",
                    "paytype": "",
                    "status": "1: Open Req"
                },
                .....
            ],
            "intent": "input_select_job",
            "entity": "select_job"
        }
    }
]
```

User message:
```
{
    "sender": "a0c526cc-1a51-11ee-9858-a19875d5b355",
    "message": "/input_select_job{\"select_job\": \"225454\"}",
    "metadata": {}
}
```