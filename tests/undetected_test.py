import asyncio
import sys

from dotenv import load_dotenv
load_dotenv()
from browser_use import Agent, utils
from langchain_openai import ChatOpenAI

TASK_PROMPT = """
You are testing a stealth browser configuration against multiple bot detection websites. For each website:

1. Navigate to the target URL.
2. Interact with the page if required (e.g. click buttons, fill forms).
3. Wait for a short delay to allow page scripts to run (e.g. 3s–60s).
4. Capture a full-page screenshot.
5. Log any visible fingerprinting or bot detection results if possible.

Test Sites:
- https://kaliiiiiiiiii.github.io/brotector/
    - Wait 3 seconds after loading.
    - Click the button with ID `clickHere`.
    - Click randomly within the button area.
    - Take a screenshot before and after the click.

- https://abrahamjuliot.github.io/creepjs
    - Wait 60 seconds after the page loads.
    - Take a full-page screenshot.

- https://fingerprint.com/products/bot-detection/
    - Wait 30 seconds after the page loads.
    - Take a full-page screenshot.

- https://www.browserscan.net/
    - Wait 30 seconds after loading.
    - Take a full-page screenshot.

(Optional – skip if proxy gets blocked):
- https://bot.incolumitas.com/
    - Fill in name as "bot3000" and email as "bot3000@gmail.com".
    - Select "I want all the Cookies".
    - Click `smolCat`, `bigCat`, and `submit`.
    - Wait until the table appears.
    - Click `updatePrice0` and `updatePrice1` and wait until they update.
    - Parse the table rows into a dictionary of name, price, and url.
    - Parse and print `#new-tests` and `#detection-tests` JSON content.
    - Take a final screenshot.

Log screenshots to the debugging directory.
"""

async def main():
    agent = Agent(
        task=TASK_PROMPT,
        llm=ChatOpenAI(model="gpt-4.1-nano-2025-04-14"),
        enable_memory=False,
        proxy=utils.PROXY(country_code='au', city='brisbane', session_time=10),
    )
    await agent.run()

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    else:
        asyncio.run(main())