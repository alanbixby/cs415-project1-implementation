import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

import aiohttp
import motor.motor_asyncio
from dotenv import load_dotenv
from typing_extensions import NotRequired

load_dotenv()

from datetime_parser import _JSONDecoder


class OddsMarketOutcomes(TypedDict):
    name: str
    price: float
    points: NotRequired[float]


OddsMarketKeys = Literal["h2h", "spreads", "totals", "outrights"]


class OddsMarkets(TypedDict):
    key: OddsMarketKeys
    outcomes: List[OddsMarketOutcomes]


OddsBookmakerNames = Literal[  # Only US Bookmakers Labelled Here
    "barstool",
    "betonlineag",
    "betfair",
    "betmgm",
    "betrivers",
    "betus",
    "bovada",
    "circasports",
    "draftkings",
    "fanduel",
    "foxbet",
    "gtbets",
    "lowvig",
    "pointsbetus",
    "sugarhouse",
    "superbook",
    "twinspires",
    "unibet_us",
    "williamhill_us",
    "wynnbet",
]


class OddsBookmaker(TypedDict):
    key: OddsBookmakerNames  # unique slug, i.e. draftkings
    title: str  # formatted pretty version of it
    last_update: datetime
    markets: List[OddsMarkets]


class OddsGame(TypedDict):
    id: str
    home_team: str
    away_team: str
    commence_time: datetime
    sport_key: str
    sport_title: str
    bookmakers: List[OddsBookmaker]


OddsResponse = List[OddsGame]


OddsParams = TypedDict(
    "OddsParams",
    {
        "apiKey": NotRequired[str],
        "sport": NotRequired[
            Union[
                Literal[
                    "americanfootball_ncaaf",
                    "americanfootball_nfl",
                    "baseball_mlb",
                    "basketball_nba",
                    "icehockey_nhl",
                    "soccer_usa_mls",
                ],
                str,
            ]
        ],
        "regions": NotRequired[List[Literal["us", "uk", "eu", "au"]]],  # us
        "markets": NotRequired[List[OddsMarketKeys]],  # h2h
        "dateFormat": NotRequired[Literal["iso", "unix"]],  # iso
        "oddsFormat": NotRequired[Literal["decimal", "american"]],  # decimal
        "eventIds": NotRequired[List[str]],
        "boomakers": NotRequired[List[OddsBookmakerNames]],
    },
)


class OddsAPIKey(TypedDict):
    _id: str
    active: bool
    api_key: str
    created_at: datetime
    remaining: int


class HTTPError(Exception):
    pass


class RatelimitError(Exception):
    pass


client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
db = client[os.getenv("DB_NAME", "cs415_data_science_dev")]
key_collection = db["odds_api_keys"]


async def get_api_key() -> OddsAPIKey:
    doc: Optional[OddsAPIKey] = await key_collection.find_one_and_update(
        {"active": True, "remaining": {"$gte": 3}, "in_use": False},
        {"$set": {"in_use": datetime.now()}},
    )
    assert doc is not None
    return doc


async def free_api_key(api_key_doc: Any) -> None:
    await key_collection.find_one_and_update(
        {"_id": api_key_doc["_id"]}, {"$set": {"in_use": False}}
    )
    print(f"unset {api_key_doc['_id']}, {api_key_doc.get('remaining', 0)}")


async def fetch_odds_data(odds_params: OddsParams, retry_count: int = 0) -> None:

    if retry_count > 3:
        raise Exception("Failed 3 times!")

    api_key_doc = await get_api_key()
    print(api_key_doc["_id"], api_key_doc["remaining"])

    odds_params["apiKey"] = api_key_doc["api_key"]
    sport = odds_params.pop("sport")
    encoded_params = "&".join(
        [
            f"{key}={','.join(value) if isinstance(value, list) else str(value)}"
            for key, value in odds_params.items()
        ]
    )

    print()
    print(f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?{encoded_params}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?{encoded_params}"
            ) as res:
                remaining = res.headers.get("x-requests-remaining", None)
                if remaining is not None:
                    await key_collection.find_one_and_update(
                        {"_id": api_key_doc["_id"]},
                        {
                            "$set": {
                                "remaining": int(remaining),
                                "active": int(remaining) >= 3,
                                "last_accessed": datetime.now(),
                            }
                        },
                    )

                if res.status == 422:
                    raise Exception("Invalid parameter configuration!")
                if res.status == 429:
                    raise RatelimitError()
                if res.status != 200:
                    print(res.status, res)
                    raise HTTPError()

                parsed_json: OddsResponse = json.loads(
                    json.dumps(await res.json()), cls=_JSONDecoder
                )

                # print(parsed_json)

                for game in parsed_json:
                    for bookmaker in game["bookmakers"]:
                        match = await db[f"odds_{bookmaker['key']}"].find_one(
                            {
                                "_id": game["id"],
                            }
                        )
                        if match is None:
                            await db[f"odds_{bookmaker['key']}"].insert_one(
                                {
                                    "_id": game["id"],
                                    "sports_key": game["sport_key"],
                                    "sport_title": game["sport_title"],
                                    "home_team": game["home_team"],
                                    "away_team": game["away_team"],
                                    "commence_time": game["commence_time"],
                                    "last_update": bookmaker["last_update"],
                                }
                            )
                        elif match.get("last_update") == bookmaker["last_update"]:
                            pass
                        else:
                            market_keys: List[OddsMarketKeys] = [
                                market["key"] for market in bookmaker["markets"]
                            ]

                            output_dict: Dict[str, Any] = {
                                "commence_time": game["commence_time"],
                                "last_update": bookmaker["last_update"],
                            }

                            new_markets = dict(
                                [
                                    (
                                        market_b["key"],
                                        {
                                            "saved_at": datetime.now(),
                                            "outcomes": market_b["outcomes"],
                                        },
                                    )
                                    for market_b in bookmaker["markets"]
                                ]
                            )

                            for market_key in market_keys:
                                last_market_outcomes: Optional[
                                    OddsMarketOutcomes
                                ] = match.get(market_key, False) and match[market_key][
                                    0
                                ].get(
                                    "outcomes", None
                                )
                                new_market_outcomes: OddsMarketOutcomes = new_markets[market_key].get("outcomes", None)  # type: ignore

                                if last_market_outcomes != new_market_outcomes:
                                    print(market_key, last_market_outcomes)
                                    print(market_key, new_market_outcomes)
                                    print(
                                        market_key,
                                        last_market_outcomes == new_market_outcomes,
                                    )
                                    print(bookmaker["key"], game["id"])

                                if (
                                    new_market_outcomes is None
                                    or last_market_outcomes == new_market_outcomes
                                ):
                                    # print(f"not new data, skipping {market_key}")
                                    continue

                                if match.get(market_key, None) is not None:
                                    print("appending")
                                    output_dict[market_key] = match[market_key]
                                    output_dict[market_key].append(
                                        new_markets[market_key]
                                    )
                                else:
                                    print("setting")
                                    output_dict[market_key] = [new_markets[market_key]]

                                print()
                            # print()
                            # print(bookmaker["key"])
                            # print(output_dict)
                            # print()

                            await db[f"odds_{bookmaker['key']}"].find_one_and_update(
                                {"_id": game["id"]},
                                {"$set": output_dict},
                            )
    except RatelimitError:
        print("Ratelimit Error")
        await asyncio.sleep(3)
        await fetch_odds_data(odds_params, retry_count + 1)
    except HTTPError:
        print("HTTP Error")
        await asyncio.sleep(3)
        await fetch_odds_data(odds_params, retry_count + 1)

    await free_api_key(api_key_doc)

    # print(f"processed: {odds_params}")


print("started:", datetime.now())


async def do_them_all() -> None:
    sports: List[str] = [
        "americanfootball_ncaaf",
        "americanfootball_nfl",
        "baseball_mlb",
        "basketball_nba",
        "icehockey_nhl",
        "soccer_usa_mls",
    ]

    for sport in sports:
        await fetch_odds_data(
            {
                "sport": sport,
                "regions": ["us"],
                "markets": ["h2h", "spreads", "totals"],
                "oddsFormat": "american",
            }
        )

    championships: List[str] = [
        "icehockey_nhl_championship_winner",
        "basketball_nba_championship_winner",
        "baseball_mlb_world_series_winner",
        "americanfootball_nfl_super_bowl_winner",
    ]

    for championship in championships:
        await fetch_odds_data(
            {
                "sport": championship,
                "regions": ["us"],
                "oddsFormat": "american",
            }
        )

    print("done!")


asyncio.run(do_them_all())
