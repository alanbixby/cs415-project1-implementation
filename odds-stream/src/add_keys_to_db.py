import asyncio
import motor.motor_asyncio
from typing import Dict

# (<email_identifier>, <api_key>)
keys: Dict[str, str] = {
  "danny": "01457544e642ecfbe2aa8ec12478e803" # expired
}

async def add_keys_to_db() -> None:
  client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
  db = client[os.getenv("DB_NAME", "cs415_data_science_dev")]
  key_collection = db["odds_api_keys"]

  for _id, api_key in keys.items():
    await key_collection.find_one_and_update({ "_id": _id }, {
      "$set": {
        "api_key": api_key,
        "active": True,
        "remaining": 500
      }
    })

asyncio.run(add_keys_to_db())