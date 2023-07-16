## Job Screening flow

### Follow up after Job search
[faq config](/app/rasa/chatbot_data/faq/faq.yml)

Based on the selected job_id from the search jobs from in [Ask a Question and explore jobs](/docs/greet.md) workflow, the Job search api: `https://sequence.accuick.com/Sequence/searchjobs` is used to fetch the relevant questions associated with the selected job.



### Initial implementation
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