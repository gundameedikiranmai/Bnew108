import re

SLOT_IGNORE_VALUES = [None, "", "ignore"]

ACCUICK_SEARCH_JOBS_URL = "https://api.curately.ai/QADemoCurately/jobsearch"
N_JOBS_TO_SHOW = 20
ACCUICK_JOBS_FORM_BUILDER_URL = "https://www4.accuick.com/Accuick_API/Curately/Chatbot/getForm.jsp"
ACCUICK_JOBS_FORM_BUILDER_DEFAULT_FORM_URL = "https://app.curately.ai/Accuick_API/Curately/Chatbot/getDefaultForm.jsp"
ACCUICK_JOB_APPLY_URL = "https://api.cxninja.com/DemoCurately/jobsapply"
ACCUICK_CHATBOT_RESPONSE_SUBMIT_URL = "https://search.accuick.com/Twilio/webhook_chatbot.jsp"
SCREENING_FORM_BACK_KEYWORD = "BACK"

#### Dynamic form behaviour
# EXPLORE_JOBS_MATCHING_CRITERIA_SLOTS = [
#     "is_resume_upload",
#     "resume_upload",
#     "job_title",
#     "job_location",
# ]

#### Placeholders
PLACEHOLDER_EMAIL = "me@email.com"
PLACEHOLDER_PHONE_NUMBER = "123-456-7890"
PLACEHOLDER_FULL_NAME = "Type your full name.."

#### validations
EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+[^.@#$%^&*<>?/|\}\{\(\)\[\]:;\\\'\",`~]$)"
PHONE_REGEX = r'^([(]\d{3}[)][\s]*[.-]?\d{3}[\s]*[.-]?\d{4}[\s]*$)|^(\d{3}[\s]*[.-]?\d{3}[\s]*[.-]?\d{4}[\s]*$)|^\d{10}[\s]*$'
email_pattern = re.compile(EMAIL_REGEX)
phone_pattern = re.compile(PHONE_REGEX)
DATE_FORMAT = "%m-%d-%Y"
DATE_MIN_YEARS_DIFFERENCE = 19

RESUME_LAST_SEARCH_RELEVANT_SLOTS = ["is_resume_upload", "resume_upload", "job_title"]
USER_PREFERENCES_RELEVANT_SLOTS = ["job_screening_questions", "job_screening_questions_count", "screening_question_history"]
SCREENING_FORM_MANDATORY_QUESTIONS = ["resume_upload", "full_name", "email", "phone_number"]
SLOTS_TO_KEEP_AFTER_RESTART = SCREENING_FORM_MANDATORY_QUESTIONS + ["first_name", "applied_jobs", "last_job_search_timestamp", "is_resume_upload", "job_title", "job_location", "job_screening_questions_last_update_time"]

SCREENING_FORM_MIN_DAYS_THRESHOLD = 30
RESUME_LAST_SEARCH_MIN_DAYS_THRESHOLD = 7
