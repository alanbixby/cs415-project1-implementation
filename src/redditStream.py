import time
from typing import Dict, List, Literal, OrderedDict, Type, TypeVar

import requests
from RedditTypings import RedditComment, RedditListing, RedditOAuth2Response, RedditSubmission
import aiohttp
import asyncio
from dateutil.parser import *
import collections


def updateRedditOAuth2(
    username: str,
    password: str,
    client_public_key: str,
    client_secret_key: str,
    user_agent: str,
) -> RedditOAuth2Response:
    res = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=requests.auth.HTTPBasicAuth(client_public_key, client_secret_key),
        data={
            "grant_type": "password",
            "username": username,
            "password": password,
            "duration": "permanent",
        },
        headers={"User-Agent": user_agent},
    )
    if res.status_code != 200:
        raise Exception(f"{res.status_code} - failed to fetch OAuth2 Token")
    parsed_json: RedditOAuth2Response = res.json()
    return parsed_json


class RedditSubredditStream:
    username: str
    password: str
    client_id: str
    client_secret: str
    user_agent: str

    # OAuth2
    access_token: str
    token_expiration: float

    # Page Memory
    
    page_history: Dict[str, collections.deque[str]] = {}  # query string

    def clear_page_history(self) -> None:
        self.page_history.clear()

    async def updateOAuth2Token(self) -> str:
        if time.monotonic() <= self.token_expiration - 300:
            return self.access_token
        current_time = time.monotonic()
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=aiohttp.BasicAuth(self.client_id, self.client_secret),
                data={
                    "username": self.username,
                    "password": self.password,
                    "grant_type": "password",
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

    async def RedditFetch(
        self,
        subreddits: List[str] = ["politics"],
        mode: Literal["new", "comments"] = "new",
        overlap_threshold: int = 10,
        skip_first_page: bool = False,
    ) -> List[RedditSubmission | RedditComment]: # AsyncGenerator[Any, None]:
        assert len(subreddits) > 0
        await self.updateOAuth2Token()
        multireddit = "+".join(subreddits)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://oauth.reddit.com/r/{multireddit}/{mode}.json?limit=100",
                auth=aiohttp.BasicAuth(self.client_id, self.client_secret),
                headers={"User-Agent": self.user_agent},
            ) as res:
                if res.status != 200:
                    raise Exception(f"{res.status} - failed to fetch Reddit data")
                parsed: RedditListing = await res.json()
                if self.page_history[multireddit] == None:
                    self.page_history[multireddit] = collections.deque(maxlen=100)
                redditChildren = [
                    elem
                    for elem in parsed["data"]["children"]["data"]
                    if elem["id"] not in self.page_history[multireddit]
                ]
                print("hello world")
                return redditChildren

    def __init__(
        self,
        username: str,
        password: str,
        client_id: str,
        client_secret: str,
        subreddits: List[str],
    ) -> None:
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.subreddits = subreddits
        self.user_agent = "ParlaysForDaysAPI/0.0.1"
        oauth_data = updateRedditOAuth2(
            self.username,
            self.password,
            self.client_id,
            self.client_secret,
            self.user_agent,
        )
        self.access_token = oauth_data["access_token"]
        self.token_expiration = time.monotonic() - 1


stream = RedditSubredditStream(
    "parlaysfordays-bot",
    "2BncavX2JZkCHQ",
    "Qbh12CbgtwBFWO3ixgGRJA",
    "dHQ6aIearW3a-e5xjzvU3ZQ-YQu63w",
    ["politics"],
)
