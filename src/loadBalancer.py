from math import ceil
from typing import Dict, Literal, Tuple, TypedDict, List

import prtpy


class SubredditStats(TypedDict):
    name: str
    comments: float
    submissions: float


# https://en.wikipedia.org/wiki/Multiway_number_partitioning
# Given an input of subreddits with their local statistics, create the minimum number of bins that can fit within the query limit, while simultaneous
# distributing the number of expected submissions/comments between bins to reduce the rate of missed data
def loadBalanceSubreddits(
    subredditStatistics: List[SubredditStats],
    context: Literal["comments", "submissions"],
    widthLimit: int = 6750,
    binLimit: int = 60,  # TODO: consider a bin limit that infers too many expected posts in a bin
    # This needs to get adjusted based on the number of bins; theres a shared ratelimit- this needs to be rethought entirely as a metric
    # since bins are nearly balanced; if the net sum of traffic > our read speed, all bins will miss
) -> List[List[str]]:

    # TODO: better handle how these fail
    assert widthLimit >= 20  # Each bin needs to hold at least 1 subreddit
    assert (
        max(stat[context] for stat in subredditStatistics) <= binLimit
    )  # Each subreddit needs to be an acceptable rate

    newDict: Dict[str, float] = {}
    for item in subredditStatistics:
        key = item["name"]
        newDict[key] = item[context]

    binOffset: int = 0  # TODO: improve logic for how binOffset increases based on the distance to target
    while binOffset < 3:
        numbins = (
            ceil((sum((len(key) + 1) for key in newDict.keys()) - 1) / widthLimit)
            + binOffset
        )

        subredditGroupings: Tuple[List[float], List[List[str]]] = prtpy.partition(
            algorithm=prtpy.partitioning.greedy,
            numbins=numbins,
            items=newDict,
            objective=prtpy.obj.MinimizeLargestSum,
            outputtype=prtpy.out.PartitionAndSums,
        )

        for grouping in subredditGroupings[1]:
            if len("+".join(grouping)) > widthLimit:
                binOffset = binOffset + 1
                continue

        if max(subredditGroupings[0]) < binLimit:
            binOffset = binOffset + 1
            continue

        return subredditGroupings[1]

    raise RuntimeError("Failed to balance subreddits")
