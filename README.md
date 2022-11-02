## Project Abstract

An implementation that asynchronously ingests data from the Twitter V2 1% Sampled Stream, Reddit API, and the Odds API to enable data analysis surrounding the effectiveness of the "wisdom of the crowd" in sports betting plus sentiment and traffic analysis of fan groups surrouning sports games.

## Team - Gatorade

* Jacob Barkovitch, jbarkov1@binghamton.edu
* Guy Ben-Yishai, gbenyis1@binghamton.edu
* Alan Bixby, abixby1@binghamton.edu
* Jacob Coddington, jcoddin1@binghamton.edu
* Ryan Geary, rgeary1@binghamton.edu
* Joseph Lieberman, jliebe12@binghamton.edu

## Tech-stack

* `Python 3.11` - The project is developed and tested using python v3.11; this is supposedly 10% - 60% faster than previous releases and has more verbose static type checking capabilities. [Python Website](https://www.python.org/)
* `MongoDB v6.0.2` - An industry staple, [web scale](https://www.youtube.com/watch?v=HdnDXsqiPYo), NoSQL database- handles schemaless input and theres less of a concern for accidental SQL injections. [MongoDB](https://www.mongodb.com/)
* `pm2` - Automatic process restarting and cron job scheduling
* `asyncio` - Asyncio is a library to write concurrent code using the async/await syntax. [asyncio docs](https://docs.python.org/3/library/asyncio.html)
* `aiohttp` - Allows for asynchronous web requests; using the "speedups" extras which adds packages like `aiodns` for better performance. [AIOHTTP website](https://docs.aiohttp.org/en/stable/)
* `aiolimiter` - An efficient implementation of a rate limiter for asyncio; used to self-enforce ratelimits while permitting asynchronous calls for long replies. [aiolimiter docs](https://aiolimiter.readthedocs.io/en/latest/)
* `motor` - A coroutine-based API for non-blocking access to MongoDB with `asyncio`. [motor docs](https://motor.readthedocs.io/en/stable/)
* `prtpy` - Python code for multiway number partitioning and bin packing algorithms; used for load balancing multi-reddit queries. [prtpy docs](https://pypi.org/project/prtpy/)
* `dateutil` - The dateutil module provides powerful extensions to the standard datetime module, available in Python; largely used for converting ISODate strings to datetime objects in this project. [dateutil docs](https://dateutil.readthedocs.io/en/stable/)
* `python-dotenv` - Python-dotenv reads key-value pairs from a .env file and can set them as environment variables. [python-dotenv repo](https://github.com/theskumar/python-dotenv)

## Three data-source documentation

* `Twitter`
  * [Volume Stream API](https://api.twitter.com/2/tweets/sample/stream) - A request stream representing a 1% sample of all Twitter traffic; we are relying heavily on Twitter's [Tweet Annotation's](https://developer.twitter.com/en/docs/twitter-api/annotations/overview) classifier that are based on 144,753 entities across 175 domains.

      | #   | Context Domain         |
      |-----|------------------------|
      | 6   | Sports Events          |
      | 11  | Sport                  |
      | 12  | Sports Team            |
      | 26  | Sports League          |
      | 27  | American Football Game |
      | 28  | NFL Football Game      |
      | 39  | Basketball Game        |
      | 40  | Sports Series          |
      | 43  | Soccer Match           |
      | 44  | Baseball Game          |
      | 60  | Athlete                |
      | 68  | Hockey Game            |
      | 92  | Sports Personality     |
      | 93  | Coach                  |
      | 137 | eSports Team           |
      | 138 | eSports Player         |
      | 149 | eSports League         |

  * We are currently tracking 17 sports related domains, which encapsulate ~22K entities; and then manually are tracking [312 selected entities](https://github.com/2022-Fall-CS-415-515/project-1-implementation-team-gatorade/blob/master/twitter-stream/src/custom_eval.py) the fell outside th 17 domain set but were still pertitent- about half of which are `<Team> Stats` entities that fall under category `131`, `Unified Twitter Taxonomy` (aka popular), whereas others include bookmaker names such as "DraftKings" which falls under `47`, `Brand`, which is far too broad to be used in our filter. 

* `Reddit` 
  - 253 subreddits (excluding `/r/politics`) are currently tracked; this list was generated from the community aggregated `/r/ListOfSubreddits` list of sports and sports teams subreddits, and then seeing subreddits mentioned in the seed subreddit wiki's/descriptions. Ultimately that produced 4,417 associated subreddits, which was filtered down to 253 by using only subreddits in the `ad_category` of `sports` or were a seed subreddit from `/r/ListofSubreddits`.

  - We are utilizing the OAuth2 flow in our data collection to double our effective ingest bandwidth,

  - To support efficient querying of new content, subreddits are batched together as multireddits based on their activity; if it is detected that data loss may occur due to too many subreddits in one query, they are automatically split into multiple "bins" using `prtpy`'s greed multiway number partitioning.

    | subreddit |
    | ---- |
    | /r/29er |
    | /r/49ers |
    | /r/adrenaline |
    | /r/advancedrunning |
    | /r/adventureracing |
    | /r/afl |
    | /r/anaheimducks |
    | /r/angelsbaseball |
    | /r/astros |
    | /r/atlantahawks |
    | /r/azcardinals |
    | /r/azdiamondbacks |
    | /r/badminton |
    | /r/barefoot |
    | /r/barefoothiking |
    | /r/barefootrunning |
    | /r/baseball |
    | /r/basketball |
    | /r/bengals |
    | /r/bicycletouring |
    | /r/bicycling |
    | /r/billiards |
    | /r/bjj |
    | /r/bluejackets |
    | /r/bostonbruins |
    | /r/bostonceltics |
    | /r/bowling |
    | /r/boxing |
    | /r/braves |
    | /r/brewers |
    | /r/browns |
    | /r/buccaneers |
    | /r/buccos |
    | /r/buffalobills |
    | /r/calgaryflames |
    | /r/camping |
    | /r/campingandhiking |
    | /r/canes |
    | /r/canucks |
    | /r/caps |
    | /r/cardinals |
    | /r/cfb |
    | /r/cfl |
    | /r/chargers |
    | /r/charlottehornets |
    | /r/chibears |
    | /r/chicagobulls |
    | /r/clevelandcavs |
    | /r/climbing |
    | /r/collegebaseball |
    | /r/collegebasketball |
    | /r/collegehockey |
    | /r/collegesoccer |
    | /r/collegesoftball |
    | /r/coloradoavalanche |
    | /r/coloradorockies |
    | /r/colts |
    | /r/commanders |
    | /r/cowboys |
    | /r/coyotes |
    | /r/cricket |
    | /r/crosscountry |
    | /r/crossfit |
    | /r/cubs |
    | /r/curling |
    | /r/cycling |
    | /r/cyclocross |
    | /r/dallasstars |
    | /r/darts |
    | /r/denverbroncos |
    | /r/denvernuggets |
    | /r/detroitlions |
    | /r/detroitpistons |
    | /r/detroitredwings |
    | /r/devils |
    | /r/discgolf |
    | /r/dodgers |
    | /r/eagles |
    | /r/edmontonoilers |
    | /r/euroleague |
    | /r/falcons |
    | /r/fantasybball |
    | /r/fantasyfootball |
    | /r/fcs |
    | /r/fencing |
    | /r/fishing |
    | /r/fitness |
    | /r/floridapanthers |
    | /r/flyers |
    | /r/football |
    | /r/formula1 |
    | /r/formulae |
    | /r/gaa |
    | /r/golf |
    | /r/gonets |
    | /r/greenbaypackers |
    | /r/habs |
    | /r/handball |
    | /r/hawks |
    | /r/heat |
    | /r/hiking |
    | /r/hockey |
    | /r/hockeyplayers |
    | /r/hsxc |
    | /r/hurling |
    | /r/indycar |
    | /r/jaguars |
    | /r/judo |
    | /r/kansascitychiefs |
    | /r/kayaking |
    | /r/kcroyals |
    | /r/kettlebell |
    | /r/kings |
    | /r/laclippers |
    | /r/lacrosse |
    | /r/lakers |
    | /r/leafs |
    | /r/letsgofish |
    | /r/lifting |
    | /r/longboarding |
    | /r/losangeleskings |
    | /r/mariners |
    | /r/mastersrunning |
    | /r/mavericks |
    | /r/memphisgrizzlies |
    | /r/miamidolphins |
    | /r/minnesotatwins |
    | /r/minnesotavikings |
    | /r/mkebucks |
    | /r/mlb |
    | /r/mlrugby |
    | /r/mls |
    | /r/mma |
    | /r/motogp |
    | /r/motorcitykitties |
    | /r/motorcycles |
    | /r/motorsports |
    | /r/mountaineering |
    | /r/mtb |
    | /r/nascar |
    | /r/nationals |
    | /r/nba |
    | /r/nbacirclejerk |
    | /r/nbaspurs |
    | /r/nbaww |
    | /r/newyorkislanders |
    | /r/newyorkmets |
    | /r/nfl |
    | /r/nhl |
    | /r/nhlstreams |
    | /r/nolapelicans |
    | /r/nrl |
    | /r/nygiants |
    | /r/nyjets |
    | /r/nyknicks |
    | /r/nyyankees |
    | /r/oaklandathletics |
    | /r/oaklandraiders |
    | /r/olympics |
    | /r/openwaterswimming |
    | /r/orioles |
    | /r/orlandomagic |
    | /r/ottawasenators |
    | /r/outdoors |
    | /r/pacers |
    | /r/padres |
    | /r/panthers |
    | /r/parkour |
    | /r/patriots |
    | /r/peloton |
    | /r/penguins |
    | /r/phillies |
    | /r/politics |
    | /r/powerbuilding |
    | /r/powerlifting |
    | /r/predators |
    | /r/progolf |
    | /r/raceit |
    | /r/racquetball |
    | /r/rangers |
    | /r/ravens |
    | /r/reds |
    | /r/redskins |
    | /r/redsox |
    | /r/ripcity |
    | /r/rockets |
    | /r/rollerblading |
    | /r/rollerderby |
    | /r/rowing |
    | /r/rugbyunion |
    | /r/running |
    | /r/runningwithdogs |
    | /r/sabres |
    | /r/saints |
    | /r/sanjosesharks |
    | /r/scottishfootball |
    | /r/seahawks |
    | /r/sfgiants |
    | /r/sixers |
    | /r/skateboarding |
    | /r/skiing |
    | /r/skydiving |
    | /r/snooker |
    | /r/snowboarding |
    | /r/soccer |
    | /r/speedskating |
    | /r/sportdocumentaries |
    | /r/sports |
    | /r/sportsarefun |
    | /r/sportsmedicine |
    | /r/sprinting |
    | /r/squaredcircle |
    | /r/squash |
    | /r/steelers |
    | /r/stlouisblues |
    | /r/stlouisrams |
    | /r/strongman |
    | /r/suns |
    | /r/surfing |
    | /r/swimming |
    | /r/tampabaylightning |
    | /r/tampabayrays |
    | /r/tennesseetitans |
    | /r/tennis |
    | /r/texans |
    | /r/texasrangers |
    | /r/theocho |
    | /r/thunder |
    | /r/timberwolves |
    | /r/torontobluejays |
    | /r/torontoraptors |
    | /r/trackandfield |
    | /r/trailrunning |
    | /r/triathlon |
    | /r/ultimate |
    | /r/ultramarathon |
    | /r/uslpro |
    | /r/utahjazz |
    | /r/velo |
    | /r/volleyball |
    | /r/wahoostipi |
    | /r/wake |
    | /r/warriors |
    | /r/washingtonwizards |
    | /r/waterpolo |
    | /r/weightlifting |
    | /r/whitesox |
    | /r/wildhockey |
    | /r/winnipegjets |
    | /r/workout |
    | /r/worldcup |
    | /r/wrestling |
    | /r/xcountryskiing |
    | /r/yoga |

  This list is intentionally verbose, and we have the ability to filter it in the future.
  
* `TheOddsAPI`
  - [The Odds API](https://the-odds-api.com/liveapi/guides/v4/) - A fremium API that aggregates betting odds from 22 US bookmakers within 5 minutes of real-time.

    | Supported US Bookmakers |
    | -------- |
    | `barstool` |
    | `betonlineag` |
    | `betfair` |
    | `betmgm` |
    | `betrivers` |
    | `betus` |
    | `bovada` |
    | `circasports` |
    | `draftkings` |
    | `fanduel` |
    | `foxbet` |
    | `gtbets` |
    | `lowvig` |
    | `pointsbetus` |
    | `sugarhouse` |
    | `superbook` |
    | `twinspires` |
    | `unibet_us` |
    | `williamhill_us` |
    | `wynnbet` |

    | Betting Types |
    | ------------- |
    | `h2h` |
    | `spreads` |
    | `totals` |
    | `outrights`

  - In our current implementation, odds are checked for updates at an hourly rate, via a cron job in `pm2`. It is possible we will make a more sophisticated version that increases this search rate when approaching major games. 

---

## System Architecture

> PM2 Monitors Everything; if it fails, PM2 restarts it.

**Twitter:** Watches stream, on data adds to `twitter_stream_counts` and send to processing queue, processing queue picks it up and determines yes/no; if yes, sent to data_queue where it is read as an async generator to push into the DB.

**Reddit:** Pulls the last 1000 posts/submissions from the database and uses the `subreddit_stats` collection to determine what subeddits to use and how to load balance them in to `n` bins; on each web request the ids of the posts are compared with that of the previous request to determine new items, and if >85 posts are seen in a page response, a rebalancing event is triggered. This prevents if something like a major football game happens that `/r/nfl` doesn't miss data because it is in a multi-reddit of 100 other subreddits. Posts deemed "new" are sent to the database for storage with most logic occurring in memory. For the rebalancing event, the full cycle must finish (every subreddit is looked up once) to prevent starvation. Before every request, the age of the OAuth2 token is checked, if it is less than 5 minutes from expiration then it is updated (consuming 1 second of the ratelimit).

**Odds API:** Requests are made to the Odds API to fetch bookmakers stats on `["americanfootball_ncaaf", "americanfootball_nfl", "baseball_mlb", "basketball_nba", "icehockey_nhl","soccer_usa_mls"]`; data is then mapped and compared against the previous entry of the game id per bookmaker and if new odds are generated, it is appended to the document with a timestamp accordingly.

---

## How to run the project?

Install `Python 3.11` and `MongoDB` and run `poetry install` in each data source directory to install your dependencies.

You may need to install/update C build dependencies compatible with Python 3.11 such as `htmllib5`; this can usually be remedied through `sudo apt install python3.11-distutils`

Optionally, use `poetry use env python3.11` to construct a virtual environment before installing dependencies. Use `poetry env info` to find the venv Python executable path.

If accessing via the VM, use `poetry shell` within the directory to enter the appropriate virtual environment.

Populate the `example.env` in `twitter-stream` and `reddit-stream` with the corresponding OAuth2 bearer token or Reddit password OAuth flow impormation, then rename the file to `.env`. Restart handling for `twitter-stream` requires an Academic Researcher bearer token.

Create several Odds API keys using `email+something@binghamton.edu`, add them to the dictionary in `odds-stream` and run `add_keys_to_db.py` to save them in the database.

**Start the processes:**

```bash
pm2 start --name="reddit-stream" --interpreter="<path to python venv if applicable>" reddit-stream/src/main.py

pm2 start --name="twitter-stream" --interpreter="<path to python venv if applicable>" twitter-stream/src/main.py

pm2 start --name="odds-api" --interpreter="<path to python venv if applicable>" twitter-stream/src/odds_stream.py --cron="59 * * * *" # Opted for minute 59 since many bets close a X:00
```

Use `pm2 list` and `pm2 logs` to validate that the proesses are running.

---

## Database Schema - NoSQL

### Connection String: `mongodb://localhost:27017`, default, no authentication, local only

---

## reddit_stream_comments

```ts
interface RedditComment {
  _id:           string;
  comment_id:    string;
  author:        string;
  text:          string;
  subreddit:     string;
  subreddit_id:  string;
  submission_id: string;
  parent_id:     string;
  created_at:    datetime;
}
```

---

## reddit_stream_submissions

```ts
interface RedditSubmission {
  _id:                    string;
  submission_id:          string;
  title:                  string;
  text:                   string;
  is_self:                boolean;
  subreddit:              string;
  subreddit_id:           string;
  url:                    string;
  url_overridden_by_dest: string;
  crosspost_parent:       string;
  created_at:             datetime;
}
```

---

## subreddit_stats

```ts
interface SubredditStats {
  _id:      string;
  comments: ModeStatistic;
  new:      ModeStatistic;
}

interface ModeStatistic {
  avg_per_second: number;
  last_access:    number;
}
```

---

## twitter_stream

```ts
interface Tweet {
  _id:                    string;
  author_id:              string;
  context_annotations:    ContextAnnotation[];
  conversation_id:        string;
  created_at:             datetime;
  edit_history_tweet_ids: string[];
  entities:               Entities;
  geo:                    Geo;
  lang:                   string;
  text:                   string;
  includes:               Includes;
}

interface ContextAnnotation {
  domain: DataWrapper;
  entity: DataWrapper;
}

interface DataWrapper {
  id:           string;
  name:         string;
  description?: string;
}

interface Entities {
  annotations: Annotation[];
}

interface Annotation {
  start:           number;
  end:             number;
  probability:     number;
  type:            string;
  normalized_text: string;
}

interface Geo {
  place_id: string;
}

interface Includes {
  users:  User[];
  places: Place[];
}

interface Place {
  country_code: string;
  full_name:    string;
  id:           string;
  place_type:   string;
}

interface User {
  created_at:     datetime;
  id:             string;
  name:           string;
  public_metrics: PublicMetrics;
  username:       string;
  verified:       boolean;
}

interface PublicMetrics {
  followers_count: number;
  following_count: number;
  tweet_count:     number;
  listed_count:    number;
}
```

---

## twitter_stream_counts

```ts
interface MinimalTweet {
  _id:        string;
  tweet_id:   string;
  created_at: datetime;
  lang:       string;
  is_stored:  boolean;
}
```

---

## odds_api_keys

```ts
interface OddsAPIKeys {
  _id: string;
  active: boolean;
  api_key: string;
  created_at: datetime;
  remaining: number;
  last_accessed: datetime;
  in_use: datetime;
}
```

---

## odds_`<bookmaker_name>`
The collection name is generated dynamically based on the bookmakers encountered.

```ts
interface BookmakerOdds {
  _id: string;
  sports_key: string;
  sport_title: string;
  home_team: string;
  away_team: string;
  commence_time: datetime;
  last_update: string;
  h2h: OutcomeDatum[];
  spreads: OutcomeDatum[];
  totals: OutcomeDatum[];
}

interface OutcomeDatum {
  saved_at: datetime;
  outcomes: Outcome[];
}

interface Outcome {
  name:  string;
  price: number;
  point?: number;
}
```