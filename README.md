# chatbot

Contains Fast Api gateway for accepting incoming messages and rerouting to Rasa

Rasa core + actions containing the chatbot implementation

### Installation
Install conda env via the environment.yml file. It uses python 3.10.6 and rasa 3.4

### Documentation
See detailed documentation in docs directory.

- [UI Integration](/docs/integration.md)
- [Job screening](/docs/job_screening.md)
- [Ask a Question and explore jobs](/docs/greet.md)


### Finished in Last Update
- **Display file upload component in resume upload question as part of job screening if resume wasn't uploaded during job search.**
- **add is_cancel_allowed in upload resume**
- **Add placeholder text for screening questions wherever applicable.**

### Pending Work

Explore Jobs

Job Screening
- **Add validations for questions based on input type (email, phone etc.)**


