import asyncio
import collections
import datetime
import time
from typing import (
    AsyncGenerator,
    Deque,
    Dict,
    List,
    Literal,
    NotRequired,
    Set,
    Tuple,
    TypedDict,
    Union,
)

import aiohttp
import motor.motor_asyncio
import prtpy
from aiolimiter import AsyncLimiter
from numpy import average, ceil

from RedditTypings import RedditCommentWrapper, RedditListing, RedditSubmissionWrapper

SubredditSearchMode = Literal["new", "comments"]

RedditOAuth2Response = TypedDict(
    "RedditOAuth2Response",
    {
        "access_token": str,
        "expires_in": int,
        "scope": str,
        "token_type": str,
    },
)

SubredditLocalStats = TypedDict(
    "SubredditLocalStats",
    {
        "last_access": float,
        "avg_per_second": NotRequired[float],
    },
)

SubredditStatsDoc = TypedDict(
    "SubredditStatsDoc",
    {"_id": str, "comments": SubredditLocalStats, "new": SubredditLocalStats},
)

SubredditPollingJob = TypedDict(
    "SubredditPollingJob", {"mode": SubredditSearchMode, "subreddits": List[str]}
)


class RedditSubredditStream:
    # Client Credentials
    username: str
    password: str
    client_id: str
    client_secret: str
    user_agent: str

    # Tracked Subreddits
    subreddits: List[str]
    subreddit_default_activity: float = 0.00025
    subreddit_bins: Dict[SubredditSearchMode, List[List[str]]] = {
        "comments": [],
        "new": [],
    }

    # High Water Management
    overlap_threshold: int = 10
    should_rebalance: Set[SubredditSearchMode] = set[SubredditSearchMode]()
    limiter = AsyncLimiter(max_rate=1, time_period=1)
    data_queue = asyncio.Queue[RedditCommentWrapper | RedditSubmissionWrapper]()

    # OAuth2
    access_token: str
    token_expiration: float = 0

    # Page Memory and Load Balancing
    # > per query request page history of ids of comments
    page_history: Dict[SubredditSearchMode, Dict[str, Deque[str]]] = {
        "comments": {},
        "new": {},
    }
    subreddit_stats: Dict[SubredditSearchMode, Dict[str, SubredditLocalStats]] = {
        "comments": {},
        "new": {},
    }

    client: motor.motor_asyncio.AsyncIOMotorClient  # type: ignore
    db_name: str
    collection_comments: str
    collection_submissions: str
    collection_stats: str

    def clear_page_history(self, mode: SubredditSearchMode) -> None:
        """Handles a rebalancing event, the query strings are likely going to change, so clear their keys,
        combine their memorized keys, then stuff them into a _reset_configuration to be looked at on new pages
        only to avoid duplicates"""
        if "_reset_configuration" in self.page_history[mode]:
            del self.page_history[mode]["_reset_configuration"]
        last_page_comments = [
            key
            for sublist in [elem for elem in self.page_history[mode].values()]
            for key in sublist
        ]
        self.page_history[mode].clear()
        self.page_history[mode]["_reset_configuration"] = collections.deque(
            last_page_comments
        )

    async def update_oauth2_token(self) -> str:
        """Check if the OAuth2 token is nearing expiration (within 5 minutes) and then refresh it, otherwise
        do nothing."""
        if time.monotonic() <= self.token_expiration - 300:
            return self.access_token
        current_time = time.monotonic()
        await self.limiter.acquire()
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
                    if res.status == 429:
                        raise Exception(f"{res.status} - RATELIMITED!!!")
                    raise Exception(f"{res.status} - failed to fetch OAuth2 Token")
                parsed: RedditOAuth2Response = await res.json()
                self.access_token = parsed["access_token"]
                self.token_expiration = current_time + parsed["expires_in"]
                return self.access_token

    async def fetch_multi_reddit(
        self,
        subreddits: List[str],
        mode: SubredditSearchMode,
        skip_first_page: bool = False,
    ) -> List[RedditSubmissionWrapper | RedditCommentWrapper]:
        """A single poll to the Reddit API for a given set of subreddits; this is intended to be used in an
        itertools cycle/chain which aggregates multiple requests as a AsyncGenerator."""
        assert len(subreddits) > 0
        multireddit = "+".join(subreddits)
        print(f"Fetching {mode}")
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
                parsed_json: RedditListing = await res.json()
                is_first_page: bool = False
                if multireddit not in self.page_history[mode]:
                    is_first_page = True
                    self.page_history[mode][multireddit] = collections.deque(maxlen=100)

                # Uniquely new posts based on the last page of results; compares against all queries on first attempt after a rebalance
                reddit_new_children = [
                    elem
                    for elem in parsed_json["data"]["children"]
                    if elem["data"]["id"] not in self.page_history[mode][multireddit]
                    or (
                        is_first_page
                        and elem["data"]["id"]
                        not in self.page_history[mode]["_reset_configuration"]
                    )
                ]

                if "_reset_configuration" in self.page_history[mode]:
                    del self.page_history[mode]["_reset_configuration"]

                # Append new posts to associated query for new data detection
                for child in reddit_new_children:
                    self.page_history[mode][multireddit].appendleft(child["data"]["id"])

                # Update local statistics for load balancing logic
                current_time = time.monotonic()
                for subreddit in subreddits:
                    # Store the time, but nothing more insightful can be determined yet
                    if subreddit not in self.subreddit_stats[mode]:
                        # intentionally omit avg_per_second on the first access
                        self.subreddit_stats[mode][subreddit] = {
                            "last_access": current_time
                        }
                        continue

                    # Get list of NEW posts that are associated with the current subreddit
                    subreddit_specific_new_data = [
                        elem
                        for elem in reddit_new_children
                        if elem["data"]["subreddit"].lower() == subreddit.lower()
                    ]

                    # Time delta of the last query to now; not necessarily n bin seconds due to rebalancing, etc
                    time_delta = (
                        current_time
                        - self.subreddit_stats[mode][subreddit]["last_access"]
                    )

                    # Take rolling average, don't average if an old value doesn't exist (aka don't average with 0 on first step),
                    if "avg_per_second" not in self.subreddit_stats[mode][subreddit]:
                        self.subreddit_stats[mode][subreddit] = {
                            "avg_per_second": len(subreddit_specific_new_data)
                            / time_delta,
                            "last_access": current_time,
                        }
                    elif self.subreddit_stats[mode][subreddit].get("last_access", 0) > (current_time - 60):
                        self.subreddit_stats[mode][subreddit] = {
                            "avg_per_second": self.subreddit_stats[mode][subreddit]["avg_per_second"],
                            "last_access": current_time,
                        }
                    else:
                        self.subreddit_stats[mode][subreddit] = {
                            "avg_per_second": (
                                ((len(subreddit_specific_new_data) / time_delta)
                                + (
                                    self.subreddit_stats[mode][subreddit][
                                        "avg_per_second"
                                    ]
                                )) / 2
                            ),
                            "last_access": current_time,
                        }

                # High Water Detection
                if (
                    not is_first_page
                    and "_reset_configuration" not in self.subreddit_stats[mode]
                    and 100 - len(reddit_new_children) < self.overlap_threshold
                ):
                    print()
                    print(
                        f"!!!!!!!!!!!!!! too big of bin! [{len(reddit_new_children)}] !!!!!!!!!!!!!!"
                    )  # Trigger Rebalance
                    print()
                    self.should_rebalance.add(mode)

                if is_first_page and skip_first_page:
                    return []
                return reddit_new_children


    def load_balance_subreddits(
        self,
        mode: Union[SubredditSearchMode, Literal["both"]],
    ) -> Tuple[List[float], List[List[str]]]:
        """The joys of premature optimization; used /r/AskReddit as a reference point which made this seem necessary.. 
        which happens to be among the most active subreddits, whereas most as very dead."""
        if mode == "both":
            self.load_balance_subreddits("new")
            mode = "comments"

        # The average based on the existing statistics, or a predefined value if DB is not initialized; used to populate unknown subreddits
        average_per_subreddit: float = (
            float(
                average(
                    [
                        elem["avg_per_second"]
                        for elem in self.subreddit_stats[mode].values()
                        if "avg_per_second" in elem
                    ]
                )
            )
            if len(self.subreddit_stats[mode]) > 0
            else self.subreddit_default_activity  # Used if no DB is initialized only
        )

        # Mapping of subreddit name -> expected posts per second
        subreddit_traffic = dict(
            [
                (
                    subreddit,
                    self.subreddit_stats[mode][subreddit]["avg_per_second"]
                    if hasattr(self.subreddit_stats[mode], subreddit)
                    and hasattr(self.subreddit_stats[mode][subreddit], "avg_per_second")
                    else average_per_subreddit,
                )
                for subreddit in self.subreddits
            ]
        )

        # The number of bins necessary based on the URI limitation
        bin_query_restricted: int = ceil(float(len("+".join(self.subreddits))) / 6750)

        # The number of bins necessary based on the amount of expected traffic; doubled to account for other mode
        bin_rate_restricted: int = ceil(
            2
            * sum([count for count in subreddit_traffic.values()])
            / (100 - self.overlap_threshold)
        )

        bin_fixing_offset: int = 0
        while True:
            print(
                f"using {max(bin_query_restricted, bin_rate_restricted) + bin_fixing_offset} bins with threshold of {self.overlap_threshold}"
            )
            if bin_fixing_offset > 5:
                raise Exception(f"fixing offset exceeded ({bin_fixing_offset})")
            sums: List[float]
            lists: List[List[str]]
            sums, lists = prtpy.partition(
                algorithm=prtpy.partitioning.greedy,
                items=subreddit_traffic,
                numbins=int(
                    max(bin_query_restricted, bin_rate_restricted) + bin_fixing_offset
                ),
                outputtype=prtpy.out.PartitionAndSumsTuple,
                # objective=prtpy.obj.MinimizeLargestSum,
            )

            # Hack: validate the load balancing, if it would still fail the threshold, try to increase it by 1 for a different shuffle
            # if max(sums) * len(sums) * 2 > (100 - (self.overlap_threshold)):
            #     bin_fixing_offset = bin_fixing_offset + 1
            #     continue

            print(lists)
            print(sums)

            # Valid load balance state was achieved; save it and get rid of old query result memory
            self.clear_page_history(mode)
            self.subreddit_bins[mode] = lists

            return (sums, lists)

    def add_subreddit(
        self,
        new_subreddits: Union[str, List[str]],
    ) -> None:
        if isinstance(new_subreddits, str):
            new_subreddits = [new_subreddits]
        new_subreddits = [subreddit.lower() for subreddit in new_subreddits]
        self.subreddits = self.subreddits + new_subreddits
        self.should_rebalance.add("comments")
        self.should_rebalance.add("new")

    def remove_subreddit(self, remove_subreddits: Union[str, List[str]]) -> None:
        if isinstance(remove_subreddits, str):
            remove_subreddits = [remove_subreddits]
        for subreddit in remove_subreddits:
            subreddit = subreddit.lower()
            if subreddit in self.subreddit_stats["comments"]:
                del self.subreddit_stats["comments"][subreddit]
            if subreddit in self.subreddit_stats["new"]:
                del self.subreddit_stats["new"][subreddit]
        self.should_rebalance.add("comments")
        self.should_rebalance.add("new")

    async def save_subreddit_stats(self) -> None:
        col = self.client[self.db_name][self.collection_stats]
        print("saving stats")
        for mode in self.subreddit_stats.keys():
            for subreddit, stat in self.subreddit_stats[mode].items():
                await col.find_one_and_update(
                    {"_id": subreddit},
                    {"$set": {mode: stat}},
                    upsert=True,
                )
        print("stats saved")
        return

    async def __subreddits_job_generator(
        self,
    ) -> AsyncGenerator[SubredditPollingJob, None]:
        """Infinite generator that creates fetch query parameters in a load balanced manner; on detected overflows,
        the cycle is finished THEN rebalanced to avoid potential starvation
        ..so itertools cycle.. but more manual because of rebalancing!"""
        while True:
            submission_bins = self.subreddit_bins["new"].copy()
            comment_bins = self.subreddit_bins["comments"].copy()
            for submission_bin in submission_bins:
                yield {"mode": "new", "subreddits": submission_bin}
            for comment_bin in comment_bins:
                yield {"mode": "comments", "subreddits": comment_bin}
            if len(self.should_rebalance) == 1:
                self.load_balance_subreddits(self.should_rebalance.pop())
            elif len(self.should_rebalance) == 2:
                self.load_balance_subreddits("both")
            await self.save_subreddit_stats()

    async def __fetch_and_add_to_queue(self, job_details: SubredditPollingJob) -> None:
        try:
            new_children: List[
                RedditSubmissionWrapper | RedditCommentWrapper
            ] = await self.fetch_multi_reddit(
                subreddits=job_details["subreddits"],
                mode=job_details["mode"],
                skip_first_page=True,
            )
            for child in new_children:
                self.data_queue.put_nowait(child)
        except Exception as e:
            # TODO: trigger a discord notification or something
            print(f"FETCH EXCEPTION {e}")

    async def populate_from_database(self) -> None:
        stats_col = self.client[self.db_name][self.collection_stats]
        docs = stats_col.find({"disabled": { "$ne": True }})
        async for doc in docs:
            for mode in ["new", "comments"]:
                print(mode)
                if mode in doc:
                    self.subreddit_stats[mode][doc["_id"]] = {  # type: ignore
                        "last_access": doc[mode]["last_access"],
                        "avg_per_second": doc[mode].get(
                            "avg_per_second", self.subreddit_default_activity
                        ),
                    }
                if doc["_id"] not in self.subreddits:
                    self.subreddits.append(doc["_id"].lower())

        self.page_history["comments"]["_reset_configuration"] = collections.deque(
            [
                comment["_id"]
                for comment in await self.client[self.db_name][self.collection_comments]
                .find({})
                .sort([("created_at", -1)])
                .to_list(length=1000)
            ]
        )

        # self.page_history[]["_reset_configuration"] =
        self.load_balance_subreddits("both")

    async def start_poll_subreddits(self) -> None:
        assert len(self.subreddits) > 0
        async for job_details in self.__subreddits_job_generator():
            await self.update_oauth2_token()  # OAuth2 Request uses the rate limit if needed
            await self.limiter.acquire()
            asyncio.create_task(self.__fetch_and_add_to_queue(job_details))

    async def poll_subreddits(
        self,
    ) -> AsyncGenerator[Union[RedditCommentWrapper, RedditSubmissionWrapper], None]:
        while True:
            yield await self.data_queue.get()
            self.data_queue.task_done()

    def __init__(
        self,
        username: str,
        password: str,
        client_id: str,
        client_secret: str,
        db_uri: str = "mongodb://localhost:27017",
        db_name: str = "cs415_data_science_dev",
        collection_comments: str = "reddit_stream_comments",
        collection_submissions: str = "reddit_stream_submissions",
        collection_stats: str = "subreddit_stats",
        subreddits: List[str] = [],
        subreddit_submission_stats: Dict[str, SubredditLocalStats] = {},
        subreddit_comment_stats: Dict[str, SubredditLocalStats] = {},
        user_agent: str = "ParlaysForDaysAPI/0.0.1",
        overlap_threshold: int = 10,
    ) -> None:
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.subreddits = [subreddit.lower() for subreddit in subreddits]
        self.subreddit_stats["new"] = subreddit_submission_stats
        self.subreddit_stats["comments"] = subreddit_comment_stats
        self.load_balance_subreddits("both")
        self.overlap_threshold = max(1, overlap_threshold)
        self.client = motor.motor_asyncio.AsyncIOMotorClient(db_uri)
        self.db_name = db_name
        self.collection_submissions = collection_submissions
        self.collection_comments = collection_comments
        self.collection_stats = collection_stats
