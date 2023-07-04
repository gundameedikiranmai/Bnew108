### Job Screening flow

The job screening flow is initiated by sending the following first message.

```
{
    "sender": UUID,
    "message": "/job_screening",
    "metadata": {
        "job_id": "2"
    }

```

The chatbot will then start asking the questions related to the given job_id in the metadata. If no job_id is given, a value of "1" is assumed as default.