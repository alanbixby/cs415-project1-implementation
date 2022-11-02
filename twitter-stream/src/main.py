import asyncio
import os

from dotenv import load_dotenv

from custom_eval import custom_eval
from twitter_stream import twitter_stream


async def main() -> None:
    load_dotenv()
    stream: twitter_stream = twitter_stream(
        os.environ["TWITTER_BEARER_TOKEN"],
        db_name=os.getenv("DB_NAME", "cs415_data_science_dev"),
        eval_func=custom_eval,
    )
    asyncio.create_task(
        stream.start_stream(
            twitter_params={
                "expansions": ["geo.place_id", "author_id"],
                "tweet.fields": [
                    "context_annotations",
                    "text",
                    "author_id",
                    "conversation_id",
                    "created_at",
                    "entities",
                    "lang",
                ],
                "user.fields": [
                    "id",
                    "verified",
                    "created_at",
                    "username",
                    "public_metrics",
                ],
                "place.fields": ["id", "country_code", "place_type", "full_name"],
            },
            start_n_process_workers=3,
        )
    )

    collection = stream.client[stream.db_name][stream.collection_primary]
    async for tweet in stream.stream_data_generator():
        print(tweet["_id"], tweet["created_at"])  # type: ignore
        try:
          collection.insert_one(tweet)
        except:
          pass


asyncio.run(main())
