## Chatbot Logs and Analytics
HOST: http://52.40.250.118:8888
API endpoint: $HOST/api/analytics/?from_date=YYYY-MM-DDTHH:MM:SS&to_date=YYYY-MM-DDTHH:MM:SS

example: http://52.40.250.118:8888/api/analytics/?from_date=2023-08-23T10:20:30&to_date=2023-09-30T10:20:30

The parameters from_date and to_date are optionals and if they are not provided, the default value for from_date is 30 days ago and to_date is today.

### Metrics
#### total_sessions
The total number of chatbot sessions for the selected time period along with percentage change over previous timeperiod.

#### explore_jobs
The total number of times when the user selected explore jobs option. The user may select this option multiple times in a single conversation and the metric will reflect this fact.

#### ask_a_question
The total number of times when the user selected ask a question option. The user may select this option multiple times in a single conversation and the metric will reflect this fact.

#### resume_files_uploaded
The number of times a resume was uploaded during a conversation.

#### top_sessions_by_location
A list of unique locations along with the count of chatbot sessions, sorted in descending order

#### total_sessions_by_day
A time series of chatbot sessions on a daily time window.

#### recent_users
A list of users who recently used the chatbot

#### top_searched_jobs
A list of job_titles that were provided by users, either manually or extracted via resume parsing while searching for jobs.

Sample API Response:

```
[
  {
    "total_sessions": [
      {
        "count": 15,
        "percent_change": 252.83
      }
    ],
    "anon_sessions": [
      {
        "count": 158,
        "percent_change": 731.58
      }
    ],
    "explore_jobs": [
      {
        "count": 34,
        "percent_change": 67
      }
    ],
    "ask_a_question": [
      {
        "count": 4,
        "percent_change": -20

      }
    ],
    "resume_files_uploaded": [
      {
        "count": 11,
        "percent_change": 25
      }
    ],
    "top_sessions_by_location": [
      {
        "_id": "TX",
        "count": 29
      },
      {
        "_id": "CA",
        "count": 18
      }
    ],
    "total_sessions_by_day": [
      {
        "_id": "2023-08-31",
        "count": 5
      },
      {
        "_id": "2023-09-02",
        "count": 1
      },
      {
        "_id": "2023-09-05",
        "count": 1
      }
    ],
    "recent_users": [
      {
        "_id": "me@gmail.com",
        "full_name": "Me"
        "last_seen": "2023-09-05T13:47:42.583000"
      },
      {
        "_id": "me@email.com",
        "full_name": "me another"
        "last_seen": "2023-08-18T11:10:38.724000"
      },
      {
        "_id": "abc@gmail.com",
        "full_name": "abc",
        "last_seen": "2023-08-17T14:18:58.025000"
      }
    ],
    "recent_anon_users": [
      {
        "_id": "652ed611b7ef55e4d137e5b5",
        "last_seen": "2023-11-07T06:49:22.377000"
      },
      {
        "_id": "652f8615b7ef55e4d1381dd9",
        "last_seen": "2023-11-07T06:49:06.955000"
      },
      {
        "_id": "6549d6b6b7ef55e4d140b96c",
        "last_seen": "2023-11-07T06:19:44.609000"
      },
      {
        "_id": "65360a2bb7ef55e4d13a3cf5",
        "last_seen": "2023-11-07T06:04:10.149000"
      },
      {
        "_id": "6549cf81b7ef55e4d140b6f6",
        "last_seen": "2023-11-07T05:47:45.196000"
      }
    ],
    "top_searched_jobs": [
      {
        "_id": "Java Developer",
        "count": 58
      },
      {
        "_id": "Senior IT Specialist",
        "count": 15
      },
      {
        "_id": "Business Analyst",
        "count": 8
      }
    ],
    "drop_off_point_last_user_messages": [
      {
        "_id": "greet",
        "count": 132
      },
      {
        "_id": "explore_jobs",
        "count": 24
      },
      {
        "_id": "input_resume_upload_data",
        "count": 9
      },
      {
        "_id": "affirm",
        "count": 7
      },
      {
        "_id": "deny",
        "count": 5
      },
      {
        "_id": "refine_job_search",
        "count": 5
      },
      {
        "_id": "california",
        "count": 5
      },
      {
        "_id": "input_screening_response",
        "count": 4
      },
      {
        "_id": "ask_a_question",
        "count": 3
      },
      {
        "_id": "input_user_question",
        "count": 3
      }
    ]
  }
]
```

### Conversation Transcript
API endpoint: $HOST/api/transcript/?sender_id=id&email=email

**Only sender_id OR email should be send in the url parameters. If both are sent, only sender_id value will be considered for providing the response.**

If email is provided, the transcript of the last session of that given user will be returned.

Examples:
```
http://52.40.250.118:8888/api/transcript/?email=me@gmail.com
http://52.40.250.118:8888/api/transcript/?sender_id=b4b2cd14-4171-11ee-8866-390f976937e1
```

**Return Format**
A list of bot and user messages
```
[
    {
        "event": "bot",
        "text": "Hi there How can I help you today?",
        "timestamp": 1692766711.4709046,
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
    },
    {
        "event": "user",
        "text": "Explore Jobs",
        "timestamp": 1692766711.487466
    },
    {
        "event": "bot",
        "text": "Let's tailor job recommendations to match your unique background and interests.",
        "timestamp": 1692766711.514332
    }
    ...
]
```

**Usage**
In the recent users and recent anon users sections, the results displayed in the UI can be made clickable. Upon clicking, the transcript api can be called with either sender_id (for anon_users) or email (for recent users) as the url parameter.

### Get Session Details
API endpoint: $HOST/api/get_session_list/?from_date=YYYY-MM-DDTHH:MM:SS&to_date=YYYY-MM-DDTHH:MM:SS&query_type=type

The parameters from_date and to_date are optionals and if they are not provided, the default value for from_date is 30 days ago and to_date is today.

Possible values for query_type are:
- total_sessions
- anon_sessions
- explore_jobs
- ask_a_question
- resume_files_uploaded
- top_searched_jobs

examples:
```
http://localhost:8000/api/get_session_list/?query_type=total_sessions
http://localhost:8000/api/get_session_list/?query_type=anon_sessions
http://localhost:8000/api/get_session_list/?query_type=top_searched_jobs&job_title=Java%20Developer
```

**Return Format**
A list of sessions
```
[
 {
    "sender_id": "2127c434-4971-11ee-b5d3-533674769a29",
    "email": "me@gmail.com",
    "full_name": "John Doe",
    "last_seen": "2023-09-02T09:15:21.649000"
  },
  {
    "sender_id": "b8f8dfe0-4bf2-11ee-80e9-43cc2b744725",
    "email": "me@gmail.com",
    "full_name": "John Doe",
    "last_seen": "2023-09-05T13:47:42.583000"
  },
  {
    "sender_id": "31860a90-68b9-11ee-b788-75bb1468e698",
    "email": null,
    "full_name": null,
    "last_seen": "2023-10-12T04:38:35.894000"
  }
  ...
]

```

Since the format is same for all session types, the email and full_name value can also be null. There may also be repetitions of email and full_name since a single person may have multiple conversation sessions. However, the sender_id values will be unique.

**Usage**
Upon clicking the count values in the dashboard (eg. total_sessions), this API can be called to get a list of the corresponding sessions. To view the transcript of a single session, then transcript api can be be called.