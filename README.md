Master Branch; production code only
---
Use branches for your individual implementations, then we can merge them in a `dev` branch and once that is proven functional, push to `master`.

----
# TODO:

## Reddit (Full Pipe of Subreddits)
- Create a polled generator function that takes an array of subreddits as input
  - use a custom user-agent to prevent 429'ing
  - use oauth.reddit.com to double ratelimit
- Load Balancing
  - detect potential data miss (or near miss) and then rebalance
    -  for rebalancing, use complete greedy algorithm O(N) for multiway number partitioning (NP-Hard)
    - have a restraint that limits to 6750 characters in a query; minimize the number of expected content per poll and number of buckets
  - rebalance anyway every hour; or from trigger?
  - to facilitate this; TTL Redis entries; aggregate number of comments and number of posts in the past [time window]

## Twitter (NLP/Keyword Filtered)
- get a working data stream
- need NLP classifier for if it should be kept
  - consider making it influenced by Reddit data?
  - generate dictionary from team/player names
  - look into Twitter's native classifications
  - consider whitelisting top posts and all their replies
    - all draftkings, or official nfl tweets; etc
- investigate usefulness of filtered stream
  - may opt for using volume stream as a fallback/tweet count only if this is good enough

## The Odds (???)
- ~~investigate capabilities~~; create a wrapper for the most useful stuff
  - do odds change over time? will we need/should we poll for changes?
- automate token generation/refreshing
- investigate what 3rd party static data would be useful to influence what odds to fetch, (game schedules, etc)

###Odds Investigation Breakdown:
 - List of sports on website. Also see document shared by Ryan on 10/25
 - Can do championship odds, as well game odds for each team. Can do h2h and spread
 - Will provide commencement time and such, so most likely does not need a game schedule to pull
 - Can pull sport transaction news (trades, signings, etc.), injury reports to see odds changing. Can provide important dates for future sentiment analysis

###Odds Jobs Breakdown:
  - Create Endpoints for Scheduler to connect to
    - Have users ask for sports, markets, and region
      - Sports list in doc
    - Clean JSON for database connection
      - Ensure specification for each game, as well as related info
      - Ensure connection between game, oddsmaker, and odds
     - Eventually push to DB when that happens
     
---

## Integration Hell

tooling:
- decide on a database topology
  - Redis for Job Scheduling + Analytics + PostgresSQL for longterm storage?
  - MongoDB only?
- decide on dashboard/analytics tooling
  - tableau
  - grafana

warnings:
- create outage detection and notification system
- low disk warnings
- high latency/high rebalancing/429'ing
  - throttle this so we dont get 1000 pings at 4AM





