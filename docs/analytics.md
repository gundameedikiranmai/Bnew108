## Chatbot Logs and Analytics
HOST: http://52.40.250.118:8888
API endpoint: $HOST/api/analytics/?from_date=YYYY-MM-DDTHH:MM:SS&to_date=YYYY-MM-DDTHH:MM:SS

example: http://52.40.250.118:8888/api/analytics/?from_date=2023-08-23T10:20:30&to_date=2023-09-30T10:20:30

The parameters from_date and to_date are optionals and if they are not provided, the default value for from_date is 30 days ago and to_date is today.

### Metrics
#### total_sessions_by_chatbot_type
This metric is the count of chatbot sessions grouped by chatbot type

#### job_applications
A list of unique email id's along with the number of jobs applied by that user

#### screening_questions_completed
A list of unique email id's along with the number of times the user answered the screening questions after applying to a job. It should be noted that a user may not necessarily answer the questions and may drop off after showing interest in a job.

#### resume_files_uploaded
A list of unique email id's along with the number of times the user uploaded a resume file in distinct chatbot sessions, i.e. they accessed the chatbot as an unknown user, either via incognito mode or by clearing the cache or on multiple devices.

#### returning_users_session_count
A list of unique email id's along with the number of times they accessed the chatbot as a known user, i.e. their data was cached in browser cookies and they opened the chatbot again to be greeted by a welcome back message.


Sample API Response:

```
[
    {
        "total_sessions_by_chatbot_type": [
            {
                "_id": "1",
                "count": 18
            },
            {
                "_id": "2",
                "count": 31
            }
        ],
        "job_applications": [
            {
                "_id": "8df@gmail.com",
                "count": 1
            },
            {
                "_id": "me@gmail.com",
                "count": 25
            },
            {
                "_id": "jannet.j.morgan@me.com",
                "count": 9
            },
            {
                "_id": "a@gmail.com",
                "count": 1
            },
            {
                "_id": "me@email.com",
                "count": 2
            },
            {
                "_id": "abc@gmail.com",
                "count": 2
            }
        ],
        "screening_questions_completed": [
            {
                "_id": "me@gmail.com",
                "count": 8
            },
            {
                "_id": "8df@gmail.com",
                "count": 1
            },
            {
                "_id": "abc@gmail.com",
                "count": 2
            },
            {
                "_id": "a@gmail.com",
                "count": 1
            },
            {
                "_id": "me@email.com",
                "count": 2
            },
            {
                "_id": "jannet.j.morgan@me.com",
                "count": 7
            }
        ],
        "resume_files_uploaded": [
            {
                "_id": "a@gmail.com",
                "count": 1
            },
            {
                "_id": "me@gmail.com",
                "count": 7
            },
            {
                "_id": "abc@gmail.com",
                "count": 1
            },
            {
                "_id": "8df@gmail.com",
                "count": 1
            },
            {
                "_id": "jannet.j.morgan@me.com",
                "count": 11
            }
        ],
        "returning_users_session_count": [
            {
                "_id": "me@gmail.com",
                "count": 3
            }
        ]
    }
]
```