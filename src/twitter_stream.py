import asyncio
import aiohttp
import json

# started at 7:04PM 10/28/2022
class TwitterSteam():
  user_agent: str
  bearer_token: str

  async def start_stream(self) -> None:
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(sock_read=20)) as session:
      async with session.get(f"https://api.twitter.com/2/tweets/sample/stream", auth={}, headers={"Authorization": f"Bearer {self.bearer_token}", "User-Agent": self.user_agent}) as resp:
        async for line in resp.content:
          parsed_json = json.loads(line.decode('utf-8'))
          
  def __init__(self, user_agent: str = "ParlaysForDaysAPI/0.0.1") -> None:
    pass
