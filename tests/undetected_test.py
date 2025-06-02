import asyncio
import sys

from dotenv import load_dotenv
load_dotenv()
from browser_use import StealthAgent, stealth_utils
from langchain_openai import ChatOpenAI

async def main():
    agent = StealthAgent(
        task="Find the price difference of latest Iphone and Samsung in australia",
        llm=ChatOpenAI(model="gpt-4.1-nano-2025-04-14"),
        enable_memory=False,
        proxy=stealth_utils.PROXY(country_code='au', city='brisbane', session_time=10),
    )
    await agent.run()

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    else:
        asyncio.run(main())