from datetime import datetime

from pymongo import MongoClient

mongo_client = None
db = None
messages_collection = None
allowed_users_collection = None


def set_uri(uri):
    global mongo_client, db, messages_collection, allowed_users_collection
    mongo_client = MongoClient(uri)
    db = mongo_client.dalle
    messages_collection = db.messages
    allowed_users_collection = db.allowed_users


def is_user_allowed(user_id):
    return allowed_users_collection.find_one({"user_id": user_id}) is not None


def store_message(user_id, text, image_url=None, origin_image_url=None):
    message_data = {
        'user_id': user_id,
        'text': text,
        'image_url': image_url,
        'origin_image_url': origin_image_url,
        'create_date': datetime.now()
    }
    messages_collection.insert_one(message_data)
