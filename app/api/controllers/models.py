"""Summary
"""
import json
import base64
from config.conf import settings
from datetime import timedelta
import copy

class ChatSession(object):

    """Summary

    Attributes:
        collection_name (str): Collection name to be used for storing data in Mongo DB.
    """

    def __init__(self):
        """Summary
        """
        self.collection_name = "chat_session"
        self.conversations_collection_name = "conversations"

    def get_search_value(self, user_data, search_key):
        if search_key == "email":
            return user_data.get('email')
        elif search_key == "phone":
            return user_data.get('phone')
        elif search_key == "uuid":
            return user_data.get("uuid")

    def get_session(self, user_data, search_key="email"):
        """Summary

        Args:
            user_data (string): user data dictionary

        Returns:
            session (dict): current session data
        """
        search_value = self.get_search_value(user_data, search_key)
        settings.logger.info("searching using {} {}".format(search_key, search_value))

        session = settings.db[self.collection_name].find_one({search_key: search_value})
        return session

    def set_session(self, user_data, search_key):
        """Summary

        Args:
            user_data (dict): session user data dictionary

        Returns:
            is_success (bool): whether set session was successful or not.
        """

        search_value = self.get_search_value(user_data, search_key)
        session = settings.db[self.collection_name].find_one({search_key: search_value})
        if session is not None:
            status = settings.db[self.collection_name].update_one({search_key: search_value}, {"$set": user_data})
            if status.modified_count > 0:
                return True
        else:
            settings.db[self.collection_name].insert_one(user_data)
            return True
        return False

    def set_last_message(self, user_data, message, search_key="email", user_email_input=None):
        """Summary

        Args:
            user_data (string): user data dictionary
            message (dict): last message for the user

        Returns:
            is_success (bool): whether set session was successful or not.
        """
        settings.logger.info("lastmessage = " + str(message)[:settings.MAX_LOGGING_LENGTH])
        settings.logger.info(f'{user_data}')

        search_value = self.get_search_value(user_data, search_key)

        session = settings.db[self.collection_name].find_one({search_key: search_value})
        # session = settings.db[self.collection_name].find_one({"phone": phone}, {"_id": 0})
        if session is not None:
            update_dict = {"last_message": message}
            if user_email_input is not None:
                update_dict["email"] = user_email_input
            if user_data.get("screening_start") is not None:
                update_dict["screening_start"] = user_data.get("screening_start")
            status = settings.db[self.collection_name].update_one({search_key: search_value}, {"$set": update_dict})
            if status.modified_count > 0:
                return True
            else:
                # check if saved message was same as current message
                saved_message_encoded = base64.urlsafe_b64encode(json.dumps(session["last_message"]).encode()).decode()
                message_encoded = base64.urlsafe_b64encode(json.dumps(message).encode()).decode()
                if saved_message_encoded == message_encoded:
                    return True
        return False
    
    def get_tracker_object(self, sender_id):
        settings.logger.info("fetching conversation for sender_id = " + sender_id)
        document_list = list(settings.db[self.conversations_collection_name].find({"sender_id": sender_id}).sort("latest_event_time", -1))
        if len(document_list) > 0:
            # get for latest session
            last_session_tracker = document_list[0]
            settings.logger.info(f"getting tracker object for sender_id = {last_session_tracker['sender_id']}")
            return last_session_tracker
        else:
            settings.logger.info(f"unable to get tracker object for sender_id = {sender_id}")
            return None
    

    ######## analytics #########
    def get_conversation_count(self, from_date, to_date, chatbot_type):
        def get_events_unwind_query_group_by_user(event, name, group_by_user=False, is_only_count=False, is_email_slot=True):
            match = {"$match": {"events.event": event, "events.name": name}}
            if is_email_slot:
                match["$match"].update({"slots.email": {"$ne": None}})
            # print(match)
            base_query = [
                {"$unwind": "$events"},
                match
                # {"$project": {"slots.email": 1}}
                # {"$count": "count"},
            ]
            if group_by_user:
                base_query += [{"$group": {"_id": "$slots.email", "count": { "$sum": 1 } }}]
            elif is_only_count:
                base_query += [{"$count": 'count' }]
            return base_query


        total_sessions = [{"$count": 'count' }]

        # count of anon user
        anon_sessions = [{"$match": {"slots.email": None}}, {"$count": 'count' }]

        top_sessions_by_location = [
            {"$match": {"slots.job_location": { "$nin" : [ None, "ignore" ] }} },
            # {"$group": {"_id": "$slots.job_location", "count": { "$sum": 1 } }},
            { "$sortByCount": "$slots.job_location" },
        ]

        recent_users = [
            {"$match": {"slots.email": {"$ne": None}} },
            { "$sort": { "latest_event_time": -1 } },
            {"$group": {"_id": "$slots.email", "last_seen": { "$first": "$latest_event_time" }, "full_name": { "$first": "$slots.full_name" } }},
            {"$project": {"last_seen": {"$toDate": {"$multiply": [1000, "$last_seen"]}}, "full_name": 1 }},
            { "$sort": { "last_seen": -1 } },
        ]

        recent_anon_users = [
            {"$match": {"slots.email": None} },
            { "$sort": { "latest_event_time": -1 } },
            # {"$group": {"_id": "$slots.email", "last_seen": { "$first": "$latest_event_time" }, "full_name": { "$first": "$slots.full_name" } }},
            {"$project": {"_id": "$sender_id", "last_seen": {"$toDate": {"$multiply": [1000, "$latest_event_time"]}} }},
            { "$limit": 5 },
        ]

        total_sessions_by_day = [
            {"$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": {
                            "$toDate": {"$multiply": [1000, "$latest_event_time"]}
                        },
                    }
                },
                "count": {"$sum": 1},
            }},
            {"$sort": {"_id":1} }
        ]

        resume_files_uploaded = [
            {"$unwind": "$events"},
            {"$match": {
                "events.event": "user",
                "events.parse_data.intent.name": "input_resume_upload_data",
                "events.parse_data.intent.confidence": 1,
                "slots.email": {"$ne": None}
            }},
            # {"$group": {"_id": "$slots.email", "count": { "$sum": 1 } }}
            {"$count": 'count' }
        ]

        returning_users_session_count = [
            {"$unwind": "$events"},
            {"$match": {"events.event": "bot", "events.metadata.utter_action": "utter_greet_known", "slots.email": {"$ne": None}}},
            {"$group": {"_id": "$slots.email", "count": { "$sum": 1 } }}
        ]

        top_searched_jobs = [
            {"$unwind": "$events"},
            {"$match": {
                "events.event": "slot",
                "events.name": "job_title",
                "events.value":  { "$nin" : [ None, "ignore" ] }
            }},
            { "$sortByCount": "$events.value" },
        ]

        drop_off_point_last_user_messages = [
            {"$match": {"slots.applied_jobs.0": {"$exists": False}, "latest_message.text": {"$ne": None} } },
            {"$project": {"latest_message": {"$ltrim": {"input": { "$arrayElemAt": [{"$split": ["$latest_message.text", "{"]}, 0] }, "chars": "/"}}  }},
            {"$group": {"_id": "$latest_message", "count": {"$sum": 1} }},
            { "$sort": { "count": -1 } },
            { "$limit": 10 },
        ]


        analytics = list(settings.db[self.conversations_collection_name].aggregate([
            {
                "$match": {
                    "latest_event_time": {"$gt": from_date.timestamp(), "$lt": to_date.timestamp()}
                }
            },
            {
                "$facet": {
                    "total_sessions": total_sessions,
                    "anon_sessions": anon_sessions,
                    "explore_jobs": get_events_unwind_query_group_by_user(event="action", name="action_start_explore_jobs", is_only_count=True),
                    "ask_a_question": get_events_unwind_query_group_by_user(event="action", name="utter_start_ask_a_question", is_only_count=True, is_email_slot=False),
                    # "job_applications": get_events_unwind_query_group_by_user(event="action", name="explore_jobs_form_submit", group_by_user=True),
                    # "screening_questions_completed": get_events_unwind_query_group_by_user(event="action", name="job_screening_form_submit", group_by_user=True),
                    "resume_files_uploaded": resume_files_uploaded,
                    "top_sessions_by_location": top_sessions_by_location,
                    "total_sessions_by_day": total_sessions_by_day,
                    "recent_users": recent_users,
                    "recent_anon_users": recent_anon_users,
                    "top_searched_jobs": top_searched_jobs,
                    "drop_off_point_last_user_messages": drop_off_point_last_user_messages
                    # "returning_users_session_count": returning_users_session_count
                }
            }
        ]))

        timeperiod_length = to_date - from_date
        settings.logger.info(timeperiod_length)
        to_date_previous = from_date - timedelta(days=1)
        from_date_previous = to_date_previous - timeperiod_length

        analytics_previous_timeperiod = list(settings.db[self.conversations_collection_name].aggregate([
            {
                "$match": {
                    "latest_event_time": {"$gt": from_date_previous.timestamp(), "$lt": to_date_previous.timestamp()}
                }
            },
            {
                "$facet": {
                    "total_sessions": total_sessions,
                    "anon_sessions": anon_sessions,
                    "explore_jobs": get_events_unwind_query_group_by_user(event="action", name="action_start_explore_jobs", is_only_count=True),
                    "ask_a_question": get_events_unwind_query_group_by_user(event="action", name="utter_start_ask_a_question", is_only_count=True, is_email_slot=False),
                    "resume_files_uploaded": resume_files_uploaded,
                }
            }
        ]))

        for metric, prev_value in analytics_previous_timeperiod[0].items():
            settings.logger.info(f"metric={metric}, prev_value={prev_value}")
            if len(analytics[0][metric]) == 0:
                analytics[0][metric] = [{"count": 0}]
            if len(prev_value) > 0:
                percent_change = round((analytics[0][metric][0]["count"]/prev_value[0]["count"] - 1)*100, 2)
                analytics[0][metric][0]["percent_change"] = percent_change
            else:
                analytics[0][metric][0]["percent_change"] = 0
        return analytics

    def get_transcript(self, sender_id, email):
        if sender_id is not None:
            match = {"sender_id": sender_id}
        elif email is not None:
            match = {"slots.email": email}
        docs = list(settings.db[self.conversations_collection_name].find(match, {"_id": 0}).sort("latest_event_time",  -1).limit(1))
        transcript = []
        if len(docs) == 0:
            return transcript
        print(docs[0]["sender_id"])
        events = docs[0].get("events", [])
        prev_buttons = None
        for e in events:
            if e["event"] == "user":
                msg = {k: e[k] for k in ('event', 'text', 'timestamp')}
                # if msg["text"] is not None:
                #     msg["text"] = settings.INTENT_TO_STRING_MAPPING.get(msg["text"], msg["text"])
                if prev_buttons is not None:
                    if prev_buttons["type"] == "btn":
                        for btn in prev_buttons["data"]:
                            if msg["text"] == btn["payload"]:
                                msg["text"] = btn["title"]
                    elif prev_buttons["type"] == "custom":
                        intent = prev_buttons["data"].get("intent")
                        entity = prev_buttons["data"].get("entity")
                        text = prev_buttons["data"]["ui_component"]
                        if "input_screening_response" in msg["text"]:
                            intent = "input_screening_response"
                            entity = "screening_response"
                            text = ""
                        if intent is not None and intent in msg["text"]:
                            if entity in msg["text"]:
                                entity = msg["text"].replace("/"+ intent, "").split(":")[1].strip().replace('"', "")[:-1]
                                if len(text) > 0:
                                    text += f": {entity}"
                                else:
                                    text = entity
                            msg["text"] = text
                transcript.append(msg)
            
            if e["event"] == "bot":
                msg = {k: e[k] for k in ('event', 'text', 'timestamp')}
                if e.get("data", {}).get("buttons") is not None:
                    msg["buttons"] = e.get("data", {}).get("buttons")
                    prev_buttons = copy.copy({"type": "btn", "data": msg["buttons"]})
                elif e.get("data", {}).get("custom") is not None:
                    msg["custom"] = e.get("data", {}).get("custom")
                    prev_buttons = copy.copy({"type": "custom", "data": msg["custom"]})
                else:
                    prev_buttons = None
                transcript.append(msg)
        return transcript


# export a chat session object for importing in other places
session = ChatSession()
