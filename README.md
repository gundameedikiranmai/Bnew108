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


### Pending Work

Explore Jobs
- **Add api call to chatbot/jobapply api in accuick after job selection. Pending due to errors in resume upload api.**

Job Screening
- **Display file upload component in resume upload question as part of job screening if resume wasn't uploaded during job search.**
- **Add validations for questions based on input type (email, phone etc.)**
- **Add placeholder text for screening questions wherever applicable.**