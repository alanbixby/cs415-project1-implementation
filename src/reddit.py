import time
from time import sleep
from typing import Generator, List, Literal, Set, Union

import requests

from RedditTypings import RedditComment, RedditListing, RedditSubmission


# TODO: use custom exceptions
# TODO: incorporate better rate limiting logic using x-rate-limit headers
# TODO: use oauth. endpoints and add automatic refresh logic based on timestamp in DB
#   - have a timer get checked that triggers refresh during runtime too; probably 12 hour refresh on the 24 hour expiry token?
# ISSUE: if stream is not consumed fast enough then we'll be at >1 sec per request, probably a good thing though..


def streamReddit(
    subreddits: Union[str, List[str]] = ["all"],
    mode: Literal["new", "comments"] = "comments",
    skipExisting: bool = False,
    overlapBufferMinimum: int = 5,
) -> Generator[Union[RedditComment, RedditSubmission], None, None]:
    if type(subreddits) is str:
        subreddits = [subreddits]

    assert len(subreddits) > 0
    assert overlapBufferMinimum >= 0 and overlapBufferMinimum < 100

    session = requests.Session()
    currentPage: Set[str] = set()
    lastPage: Set[str] = {"uninitializedSet"}
    while True:
        lastRequestTimestamp = time.time()
        req = session.get(
            f"https://www.reddit.com/r/{'+'.join(subreddits)}/{mode}.json?limit=100",
            headers={"user-agent": "/u/parlaysfordays"},
        )

        if req.status_code != 200:
            print(req.status_code)
            sleep(max(1 - (time.time() - lastRequestTimestamp), 0))
            continue

        json: RedditListing = req.json()
        overlapCount = 0
        for child in json["data"]["children"]:
            currentPage.add(child["data"]["name"])
            if child["data"]["id"] in lastPage:
                overlapCount += 1
                continue
            if skipExisting and "uninitializedSet" in lastPage:
                continue
            yield child["data"]

        if overlapCount <= overlapBufferMinimum and "uninitializedSet" not in lastPage:
            if overlapCount == 0:
                raise Exception(
                    "Potential data loss!"
                )  # TODO: convert to custom exception; will be used to trigger rebalancing
            else:
                raise Exception(
                    "Overlap buffer below minimum threshold of "
                    + f"{overlapBufferMinimum} ({100 - overlapCount})"
                )  # TODO: convert to custom exception; will be used to trigger rebalancing

        lastPage = currentPage
        currentPage = set()

        # The above processing takes ~30ms, remove it from the polling interval
        sleep(max(1 - (time.time() - lastRequestTimestamp), 0))


# Example
for post in streamReddit(["all"], "new"):
    print(post["data"]["id"])
