# day0xan32
# AAAAAAAAAAAAAAAAAAAAAIMuhQEAAAAAHGeNASkLS6xv6Da%2B9VaSbcX%2BcMo%3D3b8o5bVJo5f1K0P8gtSI8caa1y8DVISRDdF0x7IerErB6lB0ql
import os
import json
import re
import asyncio
import requests
import aiohttp
import time
from keywords import*

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = "AAAAAAAAAAAAAAAAAAAAAIMuhQEAAAAAHGeNASkLS6xv6Da%2B9VaSbcX%2BcMo%3D3b8o5bVJo5f1K0P8gtSI8caa1y8DVISRDdF0x7IerErB6lB0ql"

print(keywords)

def parse(json_response, k):
    print("iteration:", k)
    for i in keywords:
        if re.search(f'{i}[?!., ()\"\'-:;_]+', json_response["data"]["text"].lower()) is not None:

            print("found: ", i)

            print(json_response["data"]["text"])
            print("*"*50)
            break


def create_url():
    return "https://api.twitter.com/2/tweets/sample/stream"


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2SampledStreamPython"
    return r

def async_aiohttp_get_all(urls):
    """
    performs asynchronous get requests
    """
    async def get_all(urls):
        async with aiohttp.ClientSession() as session:
            async def fetch(url):
                async with session.get(url) as response:
                    return await response.json()
            return await asyncio.gather(*[fetch(url) for url in urls])
    # call get_all as a sync function to be used in a sync context
    return os.sync.async_to_sync(get_all)(urls)

def connect_to_endpoint(url, parameters, k):
    start = time.monotonic()
    response = requests.request("GET", url, params=parameters, auth=bearer_oauth, stream=True)
    print(response.status_code)
    for response_line in response.iter_lines():
        # print(time.monotonic() - start)
        # if time.monotonic() - start >= 20:
        #     print("final: ", k)
        #     break
        if response_line:
            # print(response_line)
            json_response = json.loads(response_line)
            # k+=1
            # print(json.dumps(json_response, indent=4, sort_keys=True))
            if json_response["data"]["lang"] == "en":
                print(json.dumps(json_response, indent=4, sort_keys=True))
                # k += 1
            #     parse(json_response, k)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )


def main():
    query_params = {'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                    'tweet.fields': 'id,text,author_id,lang,created_at,context_annotations,public_metrics',
                    'user.fields': 'id,name,username,description,public_metrics,verified',
                    'place.fields': 'full_name,id,country,country_code,geo,name,place_type'}

    url = create_url()
    timeout = 0
    k = 0
    while True:
        connect_to_endpoint(url, query_params, k)
        timeout += 1


if __name__ == "__main__":
    main()