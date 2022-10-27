import asyncio
from decouple import config
from redditStream import RedditSubredditStream

stream = RedditSubredditStream(
    config("REDDIT_USERNAME"),
    config("REDDIT_PASSWORD"),
    config("REDDIT_CLIENT_ID"),
    config("REDDIT_CLIENT_SECRET"),
    ["politics"],
)

print(asyncio.run(stream.fetch_multi_reddit(["politics"], "comments")))
