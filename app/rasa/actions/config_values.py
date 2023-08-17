import re

SLOT_IGNORE_VALUES = [None, "", "ignore"]

ACCUICK_SEARCH_JOBS_URL = "https://sequence.accuick.com/CloudTalentApi/api/chatbotsearchjobs"
N_JOBS_TO_SHOW = 20
ACCUICK_JOBS_FORM_BUILDER_URL = "https://www4.accuick.com/Accuick/jobs_formbuilder_action.jsp"
ACCUICK_JOB_APPLY_URL = "https://www4.accuick.com/ChatBot/jobApply.jsp"
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