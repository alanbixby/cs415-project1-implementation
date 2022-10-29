from math import ceil
import time
from typing import Any, AsyncGenerator, Awaitable, Callable, List, Optional
import asyncio
import aiohttp
import json

from decouple import config
from twitter_typings import TwitterParams, TwitterResponse


class Error(Exception):
    resp: aiohttp.ClientResponse

    def __init__(self, resp: aiohttp.ClientResponse) -> None:
        self.resp = resp


class AuthError(Exception):
    pass


class FormattingError(Exception):
    pass


class HTTPError(Error):
    pass


class RatelimitError(Error):
    pass


# Started 11:54AM 10/28/2022 - Alan Bixby
class twitter_stream:
    bearer_token: str
    whitelisted_categories: List[str]
    read_high_water_warning: int
    process_high_water_warning: int
    processing_queue: asyncio.Queue[TwitterResponse] = asyncio.Queue()
    data_queue: asyncio.Queue[TwitterResponse] = asyncio.Queue()

    def __init__(
        self,
        bearer_token: str,
        whitelisted_categories: List[str] = [
            "6",  # Sports Events
            "11",  # Sport
            "12",  # Sports Team
            "26",  # Sports League
            "27",  # American Football Game
            "28",  # NFL Football Game
            "39",  # Basketball Game
            "40",  # Sports Series
            "43",  # Soccer Match
            "44",  # Baseball Game
            "60",  # Athlete
            "68",  # Hockey Game
            "92",  # Sports Personality
            "93",  # Coach (?) TODO: investigate if this is life coach vs sports coach
            "137",  # eSports Team
            "138",  # eSports Player
            "149",  # eSports League
        ],
        process_high_water_warning: int = 250,
        read_high_water_warning: int = 2500,
    ) -> None:
        self.bearer_token = bearer_token
        self.whitelisted_categories = whitelisted_categories
        self.read_high_water_warning = read_high_water_warning
        self.process_high_water_warning = process_high_water_warning

    def check_process_queue(self) -> bool:
        if self.processing_queue.qsize() > self.process_high_water_warning:
            print(f"Processing queue is large! [{self.process_high_water_warning}]")
            self.process_high_water_warning = self.process_high_water_warning * 2
            return True
        return False

    def check_data_queue(self) -> bool:
        if self.data_queue.qsize() > self.read_high_water_warning:
            print(f"Processing queue is large! [{self.read_high_water_warning}]")
            self.read_high_water_warning = self.read_high_water_warning * 2
            return True
        return False

    async def stream_data_generator(self) -> AsyncGenerator[TwitterResponse, None]:
        while True:
            yield await self.data_queue.get()

    async def process_queue_worker(
        self, eval_func: Optional[Callable[[TwitterResponse], Awaitable[bool]]]
    ) -> None:
        while True:
            self.check_data_queue()
            tweet: Any = (
                await self.processing_queue.get()
            )  # TODO: Finish typing response (remove "Any")
            context_annotations = tweet["data"].get("context_annotations", [])
            if len(context_annotations) > 0:
                context_ids = [
                    annotation["domain"]["id"] for annotation in context_annotations
                ]
                if not set(self.whitelisted_categories).isdisjoint(context_ids):
                    self.data_queue.put_nowait(tweet)  # send to output stream
                    self.processing_queue.task_done()
                    continue
            # TODO: Handle other checks; potentially use spaCy for tokenizer and lemma processing -> matcher; or just use existing dictionary logic (or do nothing)
            if eval_func is not None and await eval_func(tweet):
                self.data_queue.put_nowait(tweet)
            self.processing_queue.task_done()
            continue

    async def start_stream(
        self, twitter_params: TwitterParams = {}, start_n_process_workers: int = 0
    ) -> None:  # AsyncGenerator[TwitterResponse, Any]:
        delay: float
        retry_count: int = 0
        last_success = time.monotonic()
        for _ in range(start_n_process_workers):
            asyncio.create_task(self.process_queue_worker())
        while True:
            try:
                if retry_count > 0:
                    twitter_params["backfill_minutes"] = max(
                        0
                        if "backfill_minutes" not in twitter_params
                        else twitter_params["backfill_minutes"],
                        ceil((time.monotonic() - last_success) / 60),
                        5,
                    )
                assert "backfill_minutes" not in twitter_params or (
                    twitter_params["backfill_minutes"] >= 0
                    and twitter_params["backfill_minutes"] <= 5
                )
                encoded_params = "&".join(
                    [
                        f"{key}={','.join(value) if isinstance(value, list) else str(value)}"
                        for key, value in twitter_params.items()
                    ]
                )
                """The endpoint provides a 20-second keep alive heartbeat (it will look like a new line character). Use this signal to detect if you are being disconnected."""
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(sock_read=20)
                ) as session:
                    async with session.get(
                        url=f"https://api.twitter.com/2/tweets/sample/stream?{encoded_params}",
                        headers={
                            "Authorization": f"Bearer {self.bearer_token}",
                            "User-Agent": "ParlaysForDaysBot/0.0.1",
                        },
                    ) as resp:
                        if resp.status == 429:
                            retry_count = retry_count + 1
                            raise RatelimitError(resp)
                        if resp.status == 403:
                            raise AuthError("Invalid Bearer Token!")
                        if resp.status == 400:
                            print(resp.url)
                            print()
                            raise FormattingError("Bad Request!")
                        if resp.status != 200:
                            retry_count = retry_count + 1
                            print(resp.url)
                            raise HTTPError(resp)
                        retry_count = 0
                        last_success = time.monotonic()
                        last_line: str = ""
                        async for line in resp.content:
                            line_str = line.decode("utf-8").strip()
                            # Ignore heartbeat responses
                            if line_str == "":
                                continue
                            parsed_json: TwitterResponse = json.loads(line_str)
                            # print(json.dumps(parsed_json, indent=1, ensure_ascii=False))
                            # TODO: potentially send to a different queue, or just add to time-series directly from here for tracking ALL tweets
                            self.processing_queue.put_nowait(parsed_json)
                            self.check_process_queue()

            except aiohttp.ClientConnectionError:
                """Back off linearly for TCP/IP level network errors. These problems are generally temporary and tend to clear quickly. Increase the delay in reconnects by 250ms each attempt, up to 16 seconds."""
                delay = 0.25 * retry_count
                if delay >= 16:
                    raise Exception
                print(f"Connection Error, sleeping for {delay}s")
                await asyncio.sleep(delay)
            except HTTPError:
                """Back off exponentially for HTTP errors for which reconnecting would be appropriate. Start with a 5 second wait, doubling each attempt, up to 320 seconds."""
                delay = 5 * (2**retry_count)
                if delay > 320:
                    raise Exception
                print(f"HTTP Error, sleeping for {delay}s")
                await asyncio.sleep(delay)
            except RatelimitError:
                """Back off exponentially for HTTP 429 errors Rate limit exceeded. Start with a 1 minute wait and double each attempt. Note that every HTTP 429 received increases the time you must wait until rate limiting will no longer be in effect for your account."""
                delay = max(
                    int(
                        time.monotonic()
                        - int(RatelimitError.resp.headers["x-rate-limit-reset"])
                    ),
                    60 * (2**retry_count),
                )
                print(f"Ratelimit Error, sleeping for {delay}s")
                await asyncio.sleep(delay)


async def main() -> None:
    stream: twitter_stream = twitter_stream(config("TWITTER_BEARER_TOKEN"))
    asyncio.create_task(
        stream.start_stream(
            twitter_params={
                "tweet.fields": [
                    "context_annotations",
                    "text",
                    "author_id",
                    "conversation_id",
                    "created_at",
                    "entities",
                    "lang",
                    "public_metrics",
                ],
                "user.fields": ["id", "verified", "created_at"],
                "place.fields": ["id", "country_code", "place_type", "full_name"],
            },
            start_n_process_workers=3,
        )
    )
    async for tweet in stream.stream_data_generator():
        print(json.dumps(tweet, indent=1))
        # TODO: make call to save to database; probably would be good to batch depending on how quickly tweets pop up


asyncio.run(main())
