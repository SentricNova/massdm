from Main import LOGGER, db as mongoDB

string_sessions_db = mongoDB.string_sessions
susers = mongoDB.served_users
sub_users = mongoDB.sub_users

userbots_cache = []
served_users_cache = []

userbots_data = {}
idle_userbots = {}
users_subscription = {}


async def add_served_user(user_id):
    try:
        userId = int(user_id)
    except Exception as err:
        LOGGER(__name__).warning(f"ERROR IN ADD SERVED USER FUNCTION : {err}")
        return
    if mongoDB != False:
        user = await susers.find_one({"user_id": userId})
        if not user:
            await susers.insert_one({"user_id": userId})
    if userId not in served_users_cache:
        served_users_cache.append(userId)
    return True

async def get_updated_served_users() -> list:
    if mongoDB == False:
        return served_users_cache
    users_list = []
    async for user in susers.find({"user_id": {"$gt": 0}}):
        users_list.append(user)
    try:
        served_users_cache.clear()
        served_users_cache.extend([user["user_id"] for user in users_list if "user_id" in user])
        return users_list
    except Exception as err:
        LOGGER(__name__).warning(f"ERROR IN GET SERVED USER FUNCTION : {err}")
        return users_list

async def add_account(api_id, api_hash, string_session, account_name, account_id):
    document_data = {
        "_id": account_id,
        "account_name": account_name,
        "api_id": api_id,
        "api_hash": api_hash,
        "string_session": string_session
    }
    try:
        result = await string_sessions_db.insert_one(document_data)
        userbots_cache.append(document_data)
        return result
    except Exception as e:
        print(f"An error occurred during insertion: {e}")
        return None

async def get_all_account():
    if userbots_cache:
        return list(userbots_cache)
    userbots = []
    async for document in string_sessions_db.find():
        document['_id'] = str(document['_id'])
        userbots.append(document)
    try:
        userbots_cache.clear()
        userbots_cache.extend(userbots)
    except Exception as err:
        LOGGER(__name__).warning(f"ERROR IN GET ALL ACCOUNT CACHE UPDATE: {err}")
        pass
    return userbots

async def get_account(account_id):
    document = await string_sessions_db.find_one({"_id": account_id})
    if document:
        document['_id'] = str(document['_id'])
    return document

async def remove_account(account_id):
    if mongoDB == False:
        LOGGER(__name__).warning("MongoDB not initialized, cannot remove account.")
        return False
    try:
        result = await string_sessions_db.delete_one({"_id": account_id})
        if result.deleted_count > 0:
            userbots_cache.clear()
            await get_all_account()
            return True
        else:
            return False
    except Exception as err:
        LOGGER(__name__).error(f"Error removing account {account_id}: {err}")
        return False

def is_valid_key_value(key, value):
    if key is None or value is None:
        return False, "Key or value cannot be None"
    if not isinstance(key, (str, int)):
        return False, "Key must be a string or integer"
    return True, ""

def add_userbot(key, value):
    valid, msg = is_valid_key_value(key, value)
    if not valid:
        return msg
    idle_userbots[key] = value
    return "Done"

def remove_userbot(key):
    if key in idle_userbots:
        del idle_userbots[key]
        return f"Removed '{key}'"
    return f"'{key}' not found"

def get_userbot(key):
    return idle_userbots.get(key, f"'{key}' not found")

def get_userbots_by_keyname(value):
    return [k for k, v in idle_userbots.items() if v == value]

def get_all_userbots():
    return list(idle_userbots.values())

async def add_subscription(user_id: int, sub_limit: int):
    if mongoDB == False:
        LOGGER(__name__).warning("MongoDB not initialized, cannot add/update subscription.")
        return False
    try:
        result = await sub_users.update_one(
            {"_id": user_id},
            {"$set": {"sub_limit": sub_limit}},
            upsert=True
        )
        if result.upserted_id:
            LOGGER(__name__).info(f"Inserted new subscription for user {user_id}.")
            return True
        elif result.modified_count > 0:
            LOGGER(__name__).info(f"Updated subscription for user {user_id}.")
            return True
        else:
            LOGGER(__name__).info(f"Subscription for user {user_id} already exists with the same limit.")
            return False
    except Exception as err:
        LOGGER(__name__).error(f"Error adding/updating subscription for user {user_id}: {err}")
        return False

async def remove_subscription(user_id: int):
    if mongoDB == False:
        LOGGER(__name__).warning("MongoDB not initialized, cannot remove subscription.")
        return False
    try:
        result = await sub_users.delete_one({"_id": user_id})
        if result.deleted_count > 0:
            LOGGER(__name__).info(f"Removed subscription for user {user_id}.")
            return True
        else:
            LOGGER(__name__).info(f"No subscription found for user {user_id} to remove.")
            return False
    except Exception as err:
        LOGGER(__name__).error(f"Error removing subscription for user {user_id}: {err}")
        return False

async def get_subscription(user_id: int):
    if mongoDB == False:
        LOGGER(__name__).warning("MongoDB not initialized, cannot get subscription.")
        return 0
    try:
        document = await sub_users.find_one({"_id": user_id})
        if document:
            return document["sub_limit"]
        else:
            LOGGER(__name__).info(f"No subscription found for user {user_id}.")
            return 0
    except Exception as err:
        LOGGER(__name__).error(f"Error getting subscription for user {user_id}: {err}")
        return 0
