"""Summary
"""
import json
import base64
from config.conf import settings

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
        settings.logger.info("lastmessage = " + str(message))
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



# export a chat session object for importing in other places
session = ChatSession()
