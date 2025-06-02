# Browser Use Undetected

An undetected browser automation wrapper/addon for [browser-use](https://github.com/browser-use/browser-use) that provides stealth capabilities using Camoufox (Firefox-based) & proxies to avoid detection by anti-bot systems, with local ReCAPTCHA v2/v3 solving & cloud solving almost all other bot detection systems using CapSolver API

## Features

- **Stealth Browser Session**: Uses Camoufox for undetected browsing
- **Proxy Support**: Built-in proxy configuration
- **Captcha Solving**: Automatic captcha detection and solving using local methods & cloud (paid) services
- **Drop-in Replacement**: Easy integration with existing browser-use code

You can find demos near the bottom of the page.

## Issues
- [ ] Humanizer setting does not work with comboboxes/dropdowns
- [ ] Captcha solving not fully functional/tested
- [ ] Unable to enter extra arguments in agent specifically for camoufox

## Installation

Requires:
```bash
python 3.11 - 3.13
```

In terminal:
```bash
pip install browser-use-undetected
camoufox fetch
```

Add .env variables:
```bash
# proxy settings (optional) - can set using Agent arguments or globally
PROXY_USERNAME=
PROXY_PASSWORD=
PROXY_HOST=
PROXY_PORT=

# Capsolver API Key (optional) - for fallback captcha solving
# Get your API key from https://capsolver.com/
CAPSOLVER_API_KEY=
```

## Quick Start

```python
import asyncio
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI
from browser_use_undetected import StealthAgent, PROXY


async def main():
    agent = StealthAgent(
        task="Find a cheap Iphone <$500 using google",
		llm=ChatOpenAI(model="gpt-4.1-nano-2025-04-14"),
		#humanize=True, #Human movement, currently comboboxes/dropdowns do not work with this
        proxy=PROXY(), # Optional
		#proxy={
		#	"server": "http://proxy:port", 
		#	"username": "user", 
		#	"password": "pass"
		#},
        auto_solve_captchas=True,  # Optional
        capsolver_api_key="your_capsolver_key"  # Optional
    )

    result = await agent.run()
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Usage

### Using StealthBrowserSession directly

```python
from browser_use_undetected import StealthBrowserSession
from browser_use.agent.service import Agent

# Create a stealth browser session
browser_session = StealthBrowserSession(
    proxy={"server": "http://proxy:port", "username": "user", "password": "pass"},
    auto_solve_captchas=True,
    capsolver_api_key="your_capsolver_key"
)

# Use with regular Agent
agent = Agent(
    task="Your task here",
    llm=your_llm_instance,
    browser_session=browser_session
)
```

### Proxy Configuration

```python
from browser_use_undetected import PROXY

# Use predefined proxy format
proxy_config = PROXY(
    host="proxy.example.com",
    port="8080",
    username="user",
    password="pass"
)

agent = StealthAgent(
    task="Your task",
    llm=your_llm_instance,
    proxy=proxy_config
)
```

## Configuration Options

- `proxy`: Proxy configuration dict or PROXY object
- `auto_solve_captchas`: Enable automatic captcha solving (default: True)
- `capsolver_api_key`: API key for CapSolver service
- All other browser-use Agent parameters are supported

# Demos

<br/><br/>

Testing Bot Detection (takes abit to load, broken on pypi page, view using github link for now):

![Bot Detection](https://github.com/BARKEM-JC/browser-use-undetected/blob/main/Demos/BotDetection.gif)

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

### Roadmap

- [x] Anti-Detection Browser
- [x] Proxy support
- [x] Fix disabled features (Remote connection, Advanced context & browser connection)
- [x] Anti-Captcha (Free local solving)
- [ ] More proxy generation providers support
- [x] Anti-Captcha (Paid services)
- [ ] Extensive testing of Anti-Captcha

## Dependencies

This addon requires:
- `browser-use[memory]` - The base browser automation framework
- `camoufox[geoip]` - Undetected Firefox-based browser
- `psutil` - System process utilities
- `pydantic` - Data validation
- `playwright-recaptcha` - Local reCAPTCHA solving
- `capsolver` - Cloud CAPTCHA solving service

## License

MIT License - see LICENSE file for details.

## Contributing

We encourage contributions!

This is an addon for browser-use. For the main framework, see [browser-use](https://github.com/browser-use/browser-use).

## Versioning

The first 2 decimal points are the browser-use version e.g 0.2.5
What comes after the last (third) decimal point is the current version of browser-use-undetected

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
