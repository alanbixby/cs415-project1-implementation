import time
from typing import Dict, List, Literal, Deque

from RedditTypings import (
    RedditComment,
    RedditListing,
    RedditOAuth2Response,
    RedditSubmission,
)
import aiohttp
import asyncio
from dateutil.parser import *
import collections


class RedditSubredditStream:
    # Client Credentials
    username: str
    password: str
    client_id: str
    client_secret: str
    user_agent: str

    # OAuth2
    access_token: str
    token_expiration: float = 0

    # Page Memory and Load Balancing
    stats_cycle_limit: int
    # > per query request page history of ids of comments
    page_comment_history: Dict[str, Deque[str]] = {}
    page_submission_history: Dict[str, Deque[str]] = {}
    # > per subreddit matches per cycle
    subreddit_comment_stats: Dict[str, Deque[int]] = {}
    subreddit_submission_stats: Dict[str, Deque[int]] = {}

    """Handles a rebalancing event, the query strings are likely going to change, so clear their keys, 
    combine their memorized keys, then stuff them into a _resetConfiguration to be looked at on new pages 
    only to avoid duplicates"""

    def clear_page_history(self, mode: Literal["new", "comments"]) -> None:
        page_history = (
            self.page_comment_history
            if mode == "comments"
            else self.page_submission_history
        )
        del page_history["_resetConfiguration"]
        last_page_comments = [
            key
            for sublist in [elem for elem in page_history.values()]
            for key in sublist
        ]
        page_history.clear()
        page_history["_resetConfiguration"] = collections.deque(last_page_comments)

    """Check if the OAuth2 token is nearing expiration (within 5 minutes) and then refresh it, otherwise
    do nothing."""

    async def update_oauth2_token(self) -> str:
        if time.monotonic() <= self.token_expiration - 300:
            return self.access_token
        current_time = time.monotonic()
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=aiohttp.BasicAuth(self.client_id, self.client_secret),
                data={
                    "grant_type": "password",
                    "username": self.username,
                    "password": self.password,
                    "duration": "permanent",
                },
                headers={"User-Agent": self.user_agent},
            ) as res:
                if res.status != 200:
                    raise Exception(f"{res.status} - failed to fetch OAuth2 Token")
                parsed: RedditOAuth2Response = await res.json()
                self.access_token = parsed["access_token"]
                self.token_expiration = current_time + parsed["expires_in"]
                return self.access_token

    """A single poll to the Reddit API for a given set of subreddits; this is intended to be used in an
    itertools cycle/chain which aggregates multiple requests as a AsyncGenerator."""

    async def fetch_multi_reddit(
        self,
        subreddits: List[str],
        mode: Literal["new", "comments"],
        overlap_threshold: int = 10,
        skip_first_page: bool = False,
    ) -> List[RedditSubmission | RedditComment]:  # AsyncGenerator[Any, None]:
        assert len(subreddits) > 0
        page_history = (
            self.page_comment_history
            if mode == "comments"
            else self.page_submission_history
        )
        subreddit_stats = (
            self.subreddit_comment_stats
            if mode == "comments"
            else self.subreddit_submission_stats
        )
        multireddit = "+".join(subreddits)
        await self.update_oauth2_token()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://oauth.reddit.com/r/{multireddit}/{mode}.json?limit=100",
                headers={
                    "User-Agent": self.user_agent,
                    "Authorization": f"Bearer {self.access_token}",
                },
            ) as res:
                if res.status != 200:
                    raise Exception(f"{res.status} - failed to fetch Reddit data")
                parsed: RedditListing = await res.json()
                is_first_page: bool = False
                if multireddit not in page_history:
                    is_first_page = True
                    page_history[multireddit] = collections.deque(maxlen=100)
                reddit_new_children = [
                    elem["data"]
                    for elem in parsed["data"]["children"]
                    if elem["data"]["id"] not in page_history[multireddit]
                    or (
                        is_first_page
                        and elem["data"]["id"]
                        not in page_history["_resetConfiguration"]
                    )
                ]
                for subreddit in subreddits:
                    if subreddit not in subreddit_stats:
                        subreddit_stats[
                            subreddit
                        ] = (
                            collections.deque()
                        )  # TODO: replace this logic using DefaultDict
                    subreddit_stats[subreddit].appendleft(
                        len(
                            [
                                elem
                                for elem in reddit_new_children
                                if elem["subreddit"] == subreddit
                            ]
                        )
                    )
                for child in reddit_new_children:
                    page_history[multireddit].appendleft(child["id"])
                if len(reddit_new_children) >= 100 - overlap_threshold:
                    print("too big of bin!")
                    # Trigger Rebalance
                if is_first_page and skip_first_page:
                    return []
                return reddit_new_children

    def __init__(
        self,
        username: str,
        password: str,
        client_id: str,
        client_secret: str,
        subreddits: List[str],
        user_agent: str = "ParlaysForDaysAPI/0.0.1",
        stats_cycle_limit: int = 600,
    ) -> None:
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.subreddits = subreddits
        self.user_agent = user_agent
        self.stats_cycle_limit = stats_cycle_limit
