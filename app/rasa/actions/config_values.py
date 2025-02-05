import os, re

SLOT_IGNORE_VALUES = [None, "", "ignore"]

HOST = os.getenv("HOST")
print(f"Using host: {HOST}")

ACCUICK_SEARCH_JOBS_URL = f"{HOST}/QADemoCurately/sovrenjobsearch"
N_JOBS_TO_SHOW = 20
# ACCUICK_JOBS_FORM_BUILDER_URL = "https://www4.accuick.com/Accuick_API/Curately/Chatbot/getForm.jsp"
# ACCUICK_JOBS_FORM_BUILDER_DEFAULT_FORM_URL = "https://app.curately.ai/Accuick_API/Curately/Chatbot/getDefaultForm.jsp"
ACCUICK_JOB_APPLY_URL = f"{HOST}/QADemoCurately/jobsapply"
ACCUICK_CHATBOT_RESPONSE_SUBMIT_URL = f"{HOST}/Accuick_API/Curately/Webhook/webhook_chatbot.jsp"
SCREENING_FORM_BACK_KEYWORD = "BACK"
CURATELY_EMAIL_SYNC_API = f"{HOST}/QADemoCurately/savechatbotinformation"
REUPLOAD_RESUME_UPDATE_CONTACT_DETAILS = f"{HOST}/QADemoCurately/updateemail"

GET_USER_DETAILS_API = HOST + "/QADemoCurately/getUserDetails/{user_id}/{client_id}"

GET_APPLIED_JOBS_URL = HOST + "/QADemoCurately/getjobs/{user_id}"

GET_CUSTOM_JOB_FORM = HOST + "/QADemoCurately/getjobdata/{job_id}/{user_id}/{client_id}"

# user preferences
ACCUICK_CHATBOT_USER_PREFERENCE_GET_URL = f"{HOST}/QADemoCurately/CandidatePreferenceJson/"
ACCUICK_CHATBOT_USER_PREFERENCE_POST_URL = f"{HOST}/QADemoCurately/saveorupdateChatBotPref"

# fixed question ids
FIXED_FORM_BUILDER_PROFILE_IDS = {
    "b148be5c-c346-4555-969e-8dbc392cb06b": "email",
    "4fe857a5-ee43-491a-8f7b-9f68f1539d48": "firstName",
    "04ae1498-154f-4725-bb0d-09d3d92791d0": "lastName",
    "afd5afa2-9827-4033-9d6c-b0ee121e6eb2": "phoneNo",
    "37c3a99e-68ec-4cac-a1bf-6d5ae3062b57": "resume",
}

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
SLOTS_TO_KEEP_AFTER_RESTART = SCREENING_FORM_MANDATORY_QUESTIONS + ["first_name", "applied_jobs", "last_job_search_timestamp", "is_resume_upload", "job_title", "job_location", "job_screening_questions_last_update_time", "update_contact_details"]

SCREENING_FORM_MIN_DAYS_THRESHOLD = 30
