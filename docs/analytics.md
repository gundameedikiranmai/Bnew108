## Chatbot Logs and Analytics
HOST: http://52.40.250.118:8888
API endpoint: $HOST/api/analytics/?from_date=YYYY-MM-DDTHH:MM:SS&to_date=YYYY-MM-DDTHH:MM:SS

example: http://52.40.250.118:8888/api/analytics/?from_date=2023-08-23T10:20:30&to_date=2023-09-30T10:20:30

The parameters from_date and to_date are optionals and if they are not provided, the default value for from_date is 30 days ago and to_date is today.

### Metrics
#### total_sessions
The total number of chatbot sessions for the selected time period

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
        "count": 15
      }
    ],
    "explore_jobs": [
      {
        "count": 34
      }
    ],
    "ask_a_question": [
      {
        "count": 4
      }
    ],
    "resume_files_uploaded": [
      {
        "count": 11
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
        "last_seen": "2023-09-05T13:47:42.583000"
      },
      {
        "_id": "me@email.com",
        "last_seen": "2023-08-18T11:10:38.724000"
      },
      {
        "_id": "abc@gmail.com",
        "last_seen": "2023-08-17T14:18:58.025000"
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
    ]
  }
]
```