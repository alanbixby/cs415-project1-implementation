# import asyncio
# import itertools
# from random import randrange

# loop = asyncio.get_event_loop()


# class binMaker:
#     def __init__(self) -> None:
#         self.bins = itertools.cycle(["a", "b", "c"])

#     async def update(self) -> None:
#         self.bins = itertools.cycle(["x", "y", "z"])


# subredditBins = binMaker()

# CONT = itertools.count()


# async def print_random_delay() -> None:
#     my_count = next(CONT)
#     delay = randrange(500, ) / 1000
#     await asyncio.sleep(delay)
#     print(f"{my_count} with a {delay * 1000}ms delay")


# async def loop_wrap() -> None:
#     while True:
#         asyncio.ensure_future(print_random_delay())
#         await asyncio.sleep(1)


# asyncio.ensure_future(loop_wrap())
# loop.run_forever()
