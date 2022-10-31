## Project Abstract

## Team - Gatorade

* Jacob Barkovitch, jbarkov1@binghamton.edu
* Guy Ben-Yishai, gbenyis1@binghamton.edu
* Alan Bixby, abixby1@binghamton.edu
* Jacob Coddington, jcoddin1@binghamton.edu
* Ryan Geary, rgeary1@binghamton.edu
* Joseph Lieberman, jliebe12@binghamton.edu

## Tech-stack

* `python` - The project is developed and tested using python v3.11. [Python Website](https://www.python.org/)
* `aiohttp` - v.3.8.3, {extras = [“speedups”]} Allows for asynchronous web requests. [AIOHTTP Website](https://docs.aiohttp.org/en/stable/)
* `aiolimiter` - v.1.0.0 Handles rate limiting. [aiolimiter docs](https://aiolimiter.readthedocs.io/en/latest/)
* `motor` - v.3.1.1 Asynchronous Python driver for MongoDB. [Motor docs](https://motor.readthedocs.io/en/stable/)
* `prtpy` - v.0.8.1 # A partitioning library. [prtpy docs](https://pypi.org/project/prtpy/)
* `python-dateutil` - v.2.8.2 makes date manipulation easier[dateutil docs](https://dateutil.readthedocs.io/en/stable/)
* `python-decouple` - v.3.6 Allows the use of .env variables
* `request` - HTTP networking module(aka library) for python programming language. [Request Website](https://docs.python-requests.org/en/latest/#)

## Three data-source documentation

This section must include two things for each source: (1) A specific end-point URL(aka API) or Website link if you are crawling web-pages (2) Documentation of the API

* `Twitter`
  * [Volume Stream API](https://api.twitter.com/2/tweets/sample/stream) - 
Live stream with 1% of tweets posted on twitter. We filter them for sports related keywords and annotations.
* `Reddit` - We are using `r/pics`, `r/news`, etc.
  * [r/pics](https://reddit.com/r/pics) - <Small description goes here. Yada, yada, yada...>
  * [API-1](https://google.com) - <Small description goes here. Yada, yada, yada...>
  * [API-2](https://google.com) - <Small description goes here. Yada, yada, yada...>
* `TheOddsAPI` - Will pull sports betting odds 
  * [API-Link1](https://api.the-odds-api.com/v4/sports/?apiKey={apiKey}) - Will return all  in-season sports
*[API-Link2](https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={apiKey}&regions={regions}&markets={markets}) - Will return all odds for upcoming games of a  specified league ({sport}) for a specific region ({regions}) for specific odds types ({markets}). 
* Example region: us, uk
* Example sport: americanfootball_nfl, baseball_mlb
* Example market: h2h, spreads
  * [Documentation-link](https://the-odds-api.com/) - This website provides documentation for TheOddsAPI. Will provide info on which leagues are available, what odds, and what regions are available. Provided generic website link as info is distributed between homepage and API page.

## System Architecture
** this is a diagram of what’s going on


## How to run the project?

Install `Python` and `PostgreSQL`

```bash
pip install pandas, numpy, psycopg3
cd project_1/src/
python main.py
```
**NOTE: You must mention all required details to run your project. We will not fix any `compilation` or `runtime` error by ourself. If something needs to be installed, mention it!**


## Database schema - NoSQL (Remove this section if you are using SQL database)

```bash

collection_1: twitter_volume
{
  "id": ...,
  "text": ...,
  "timestamp": ...
}

collection_2: reddit_comments
{
  "id": ...,
  "text": ...,
  "timestamp": ...
}

collection_3: 4chan_posts
{
  "id": ...,
  "text": ...,
  "timestamp": ...
}
```

**NOTE: You can have as many collections you want with whatever fields in document, we don't care. NoSQL is schemaless, but still add fields you are collecting, that's it!**

## Special instructions for us???
