from Main import LOGGER
from config import MONGO_DB, DB_NAME

try:
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
    except ImportError:
        import os
        LOGGER(__name__).info("🛠️ The 'motor' library for asynchronous MongoDB operations is not installed. Attempting to install it...")
        os.system("pip3 install motor==2.5.0")
        LOGGER(__name__).info("✅ Installation complete!")
        from motor.motor_asyncio import AsyncIOMotorClient
    LOGGER(__name__).info("🔗 Connecting to the MongoDB database...")
    _mongo_async_ = AsyncIOMotorClient(MONGO_DB)
    mongodb = _mongo_async_[DB_NAME]
    LOGGER(__name__).info(f"🚀 Successfully connected to the MongoDB database '{DB_NAME}'!")
except Exception as err:
    LOGGER(__name__).error(f"❌ Failed to connect to the MongoDB database:\n\n {err}")
    import sys
    sys.exit()
