import asyncio
import json
from time import sleep

from decouple import config

from redditStream import RedditSubredditStream

stream = RedditSubredditStream(
    config("REDDIT_USERNAME"),
    config("REDDIT_PASSWORD"),
    config("REDDIT_CLIENT_ID"),
    config("REDDIT_CLIENT_SECRET"),
    ["politics"],
)

print(
    json.dumps(
        asyncio.run(
            stream.fetch_multi_reddit(["politics", "askreddit"], "comments", skip_first_page=True)
        ),
        indent=2,
    )
)
i = 0
while True:
    sleep(1)
    new_stuff = asyncio.run(stream.fetch_multi_reddit(["politics", "askreddit"], "comments"))
    new_stuff_ids = [elem["subreddit"] for elem in new_stuff]
    print(f"{i}. {new_stuff_ids} <- new page")
    i = i + 1
    print()
    if (i % 5 == 0):
        print(stream.subreddit_comment_stats)
