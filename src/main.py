from math import ceil
import time
from typing import TypedDict
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
    data_queue: asyncio.Queue[TwitterResponse]

    def __init__(self, bearer_token: str) -> None:
        self.bearer_token = bearer_token

    async def start_stream(
        self,
        twitter_params: TwitterParams = {},
    ) -> None:  # AsyncGenerator[TwitterResponse, Any]:
        delay: float
        retry_count: int = 0
        last_success = time.monotonic()
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
                            print(json.dumps(parsed_json, indent=1, ensure_ascii=False))
                            # yield parsed_json

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


stream: twitter_stream = twitter_stream(config("TWITTER_BEARER_TOKEN"))

asyncio.run(
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
        }
    )
)
