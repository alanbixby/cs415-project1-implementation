import asyncio
import json
from time import sleep

from decouple import config

from reddit_stream import RedditSubredditStream

stream = RedditSubredditStream(
    config("REDDIT_USERNAME"),
    config("REDDIT_PASSWORD"),
    config("REDDIT_CLIENT_ID"),
    config("REDDIT_CLIENT_SECRET"),
    ["politics", "nfl", "cfb", "nba"],
    overlap_threshold=15,
)


async def printStream() -> None:
    asyncio.create_task(stream.start_poll_subreddits())
    i = 0
    async for item in stream.poll_subreddits():
        i = i + 1
        print(item["subreddit"])
        # add to database here


asyncio.run(printStream())
