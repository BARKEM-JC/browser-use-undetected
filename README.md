<h1 align="center">Enable AI to control your browser 🤖 (Now undetected with proxy support!)</h1>

🌐 Browser-use-undetected is the easiest way to connect your AI agents with the browser without detection & proxy support.

Forked from the official https://github.com/browser-use/browser-use If you give me a star please give them a star for their great work.

To make it work initially i have disabled some things like Remote connection, Advanced context & browser connection. Will be disabled until i can confirm they work.

🕵️‍♂️ Detection Results
(Proxy is usually detected but not blocked, use a AI web unblocker proxy for more invisibility)
| Site                                                           | Status | Notes                            |
| -------------------------------------------------------------- | ------ | -------------------------------- |
| [Google](https://www.google.com)                               | ✅ Pass | No bot detection triggered       |
| [Brotector](https://kaliiiiiiiiii.github.io/brotector/)        | ✅ Pass | Click interaction successful     |
| [CreepJS](https://abrahamjuliot.github.io/creepjs)             | ✅ Pass | No fingerprinting flags detected |
| [Fingerprint](https://fingerprint.com/products/bot-detection/) | ✅ Pass | No bot behavior detected         |
| [BrowserScan](https://www.browserscan.net/)                    | ✅ Pass | Report appears clean             |
| [Incolumitus](https://bot.incolumitas.com/)                    | ❌ Fail | Proxy blocked                    |

# Quick start

Install with:
```bash
pip install browser-use-undetected
```

Then once installed run this in the terminal:
```bash
camoufox fetch
```

For memory functionality (requires Python<3.13 due to PyTorch compatibility):  

```bash
pip install "browser-use-undetected[memory]"
```

To clone the entire repo:
```bash
git clone https://github.com/BARKEM-JC/browser-use-undetected.git
```

Spin up your agent:

```python
import asyncio
import sys

from dotenv import load_dotenv
load_dotenv()
from browser_use import Agent, utils
from langchain_openai import ChatOpenAI

async def main():
    agent = Agent(
        task="Compare prices of the latest iPhone and Samsung Galaxy in Australia",
        llm=ChatOpenAI(model="gpt-4.1-nano-2025-04-14"),
        enable_memory=False,
        proxy=utils.PROXY(), # Set as arguments or in .env, The following arguments only work with oxylabs currently: country_code='au', city='brisbane', session_time=10 
		#proxy={
		#	'server': f'http://host:port',
		#	'username': proxy_username,
		#	'password': self.password
		#}
	)
    await agent.run()

if __name__ == "__main__":
	# Fixes issues with running from different contexts on windows
    if sys.platform.startswith("win"):
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    else:
        asyncio.run(main())
```

Add your API keys for the provider you want to use to your `.env` file.

```bash
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_KEY=
GOOGLE_API_KEY=
DEEPSEEK_API_KEY=
GROK_API_KEY=
NOVITA_API_KEY=
```

You can add your proxy settings globally to your `.env` file (or just specify in the Agent call).
```bash
PROXY_USERNAME=
PROXY_PASSWORD=
PROXY_HOST=
PROXY_PORT=
```

For other settings, models, and more, check out the original [documentation 📕](https://docs.browser-use.com).

### Roadmap

- [x] Anti-Detection Browser
- [x] Proxy support
- [ ] Fix disabled features (Remote connection, Advanced context & browser connection)
- [ ] Anti-Captcha (Free local solving)
- [ ] More proxy generation providers support
- [ ] Anti-Captcha (Paid services)

### Test with UI
(Have not tested)

You can test browser-use using its Web UI or Desktop App.

Or simply run the gradio example:
``` bash
uv pip install gradio
python examples/gradio.py
```

### Test with an interactive CLI
(Have not tested)

You can also use our `browser-use` interactive CLI (similar to `claude` code):
```bash
pip install browser-use[cli]
browser-use
```

# Demos

<br/><br/>

Testing Bot Detection (takes abit to load, broken on pypi page, view using github link for now):

![Bot Detection](https://github.com/BARKEM-JC/browser-use-undetected/raw/main/static/BotDetection.gif)

<br/><br/>

[Task](https://github.com/browser-use/browser-use/blob/main/examples/use-cases/shopping.py): Add grocery items to cart, and checkout.

[![AI Did My Groceries](https://github.com/user-attachments/assets/a0ffd23d-9a11-4368-8893-b092703abc14)](https://www.youtube.com/watch?v=L2Ya9PYNns8)

<br/><br/>

Prompt: Add my latest LinkedIn follower to my leads in Salesforce.

![LinkedIn to Salesforce](https://github.com/user-attachments/assets/50d6e691-b66b-4077-a46c-49e9d4707e07)

<br/><br/>

[Prompt](https://github.com/browser-use/browser-use/blob/main/examples/use-cases/find_and_apply_to_jobs.py): Read my CV & find ML jobs, save them to a file, and then start applying for them in new tabs, if you need help, ask me.'

https://github.com/user-attachments/assets/171fb4d6-0355-46f2-863e-edb04a828d04

<br/><br/>

[Prompt](https://github.com/browser-use/browser-use/blob/main/examples/browser/real_browser.py): Write a letter in Google Docs to my Papa, thanking him for everything, and save the document as a PDF.

![Letter to Papa](https://github.com/user-attachments/assets/242ade3e-15bc-41c2-988f-cbc5415a66aa)

<br/><br/>

[Prompt](https://github.com/browser-use/browser-use/blob/main/examples/custom-functions/save_to_file_hugging_face.py): Look up models with a license of cc-by-sa-4.0 and sort by most likes on Hugging face, save top 5 to file.

https://github.com/user-attachments/assets/de73ee39-432c-4b97-b4e8-939fd7f323b3

<br/><br/>

## More examples

For more examples see the [examples](examples) folder or join the official browser-use [Discord](https://link.browser-use.com/discord) and show off your project. You can also see [`awesome-prompts`](https://github.com/browser-use/awesome-prompts) repo for prompting inspiration.

# Vision

Tell your computer what to do, and it gets it done.

## Contributing

We love contributions! Feel free to open issues for bugs or feature requests. To contribute to the docs, check out the `/docs` folder.

## Local Setup

To learn more about the library, check out the [local setup 📕](https://docs.browser-use.com/development/local-setup).


`main` is the primary development branch with frequent changes. For production use, install a stable [versioned release](https://github.com/browser-use/browser-use/releases) instead.

---

## Citation

```bibtex
@software{browser_use2024,
  author = {Müller, Magnus and Žunič, Gregor},
  title = {Browser Use: Enable AI to control your browser},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/browser-use/browser-use}
}
```
 </div>
