# Browser Use Stealth

An undetected browser automation addon for [browser-use](https://github.com/browser-use/browser-use) that provides stealth capabilities using Camoufox (Firefox-based) to avoid detection by anti-bot systems.

## Features

- **Stealth Browser Session**: Uses Camoufox for undetected browsing
- **Proxy Support**: Built-in proxy configuration
- **Captcha Solving**: Automatic captcha detection and solving
- **Drop-in Replacement**: Easy integration with existing browser-use code

## Installation

```bash
pip install browser-use[memory]
pip install browser-use-stealth
```

## Quick Start

```python
import asyncio
from browser_use_stealth import StealthAgent

async def main():
    agent = StealthAgent(
        task="Navigate to example.com and take a screenshot",
        llm=your_llm_instance,  # Your LLM instance (OpenAI, Anthropic, etc.)
        proxy={"server": "http://proxy:port", "username": "user", "password": "pass"},  # Optional
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
from browser_use_stealth import StealthBrowserSession
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
from browser_use_stealth import PROXY

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

## Dependencies

This addon requires:
- `browser-use[memory]` - The base browser automation framework
- `camoufox[geoip]` - Undetected Firefox-based browser
- `psutil` - System process utilities
- `pydantic` - Data validation
- `playwright-recaptcha` - reCAPTCHA solving
- `capsolver` - CAPTCHA solving service

## License

MIT License - see LICENSE file for details.

## Contributing

This is an addon for browser-use. For the main framework, see [browser-use](https://github.com/browser-use/browser-use).