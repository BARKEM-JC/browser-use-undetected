# Captcha Integration for Browser-Use-Undetected

This document explains how to use the integrated captcha solving capabilities in browser-use-undetected.

## Overview

The captcha integration automatically detects and solves various types of captchas and bot detection systems:

### Supported Captcha Types
- **reCAPTCHA v2** (using playwright-recaptcha)
- **reCAPTCHA v3** (using playwright-recaptcha)
- **hCaptcha** (using capsolver as fallback)
- **FunCaptcha** (using capsolver as fallback)
- **GeeTest** (using capsolver as fallback)
- **Turnstile** (using capsolver as fallback)
- **Image-based captchas** (using capsolver as fallback)

### Supported Bot Detection
- **Cloudflare** bot detection
- **CloudFront** bot detection
- **Generic bot detection** systems

## Setup

### 1. Install Dependencies

The required dependencies are automatically installed with the project:
- `playwright-recaptcha` - For reCAPTCHA v2/v3 solving
- `capsolver` - For fallback captcha solving
- `pydub` - For audio processing
- `SpeechRecognition` - For audio captcha solving
- `tenacity` - For retry logic

### 2. Configure Capsolver API Key (Optional)

For fallback captcha solving, you can optionally configure a Capsolver API key:

1. Create a `.env` file in the project root (if it doesn't exist)
2. Add your Capsolver API key:
   ```
   CAPSOLVER_API_KEY=your_api_key_here
   ```

**Note:** The Capsolver API key is optional. reCAPTCHA v2/v3 will be solved using playwright-recaptcha without requiring an API key.

## Usage

### Basic Usage with StealthBrowserSession

```python
import asyncio
from browser_use.browser import StealthBrowserSession
from browser_use.browser.profile import BrowserProfile

async def main():
    # Create session with automatic captcha solving enabled (default)
    session = StealthBrowserSession(
        browser_profile=BrowserProfile(),
        auto_solve_captchas=True  # This is the default
    )
    
    # Start the session
    await session.start()
    
    # Navigate to a page with captchas - they will be automatically detected and solved
    await session.navigate("https://example.com/page-with-captcha")
    
    # The captcha will be automatically solved in the background
    # You can continue with your automation
    
    await session.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Usage with Custom Configuration

```python
import asyncio
from browser_use.browser import StealthBrowserSession
from browser_use.browser.profile import BrowserProfile

async def main():
    # Create session with custom captcha configuration
    session = StealthBrowserSession(
        browser_profile=BrowserProfile(),
        auto_solve_captchas=True,
        capsolver_api_key="your_api_key_here"  # Optional: override .env setting
    )
    
    await session.start()
    
    # Navigate to page
    await session.navigate("https://example.com/captcha-page")
    
    # Manual captcha solving (if auto-solving is disabled or fails)
    captcha_solved = await session.solve_captchas_manually(timeout=60)
    if captcha_solved:
        print("Captcha solved successfully!")
    else:
        print("No captcha found or solving failed")
    
    # Wait for captcha resolution with custom timeout
    await session.wait_for_captcha_resolution(timeout=120)
    
    await session.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### Using with StealthAgent

```python
import asyncio
from browser_use.agent import StealthAgent
from browser_use.browser.profile import BrowserProfile

async def main():
    # Create agent with captcha solving enabled
    agent = StealthAgent(
        task="Navigate to a website and fill out a form",
        llm=your_llm_instance,
        browser_profile=BrowserProfile(),
        auto_solve_captchas=True,  # Enable automatic captcha solving
        capsolver_api_key="your_api_key_here"  # Optional
    )
    
    # The agent will automatically handle captchas during task execution
    result = await agent.run()
    
    return result

if __name__ == "__main__":
    asyncio.run(main())
```

### Disabling Automatic Captcha Solving

```python
# Disable automatic captcha solving
session = StealthBrowserSession(
    browser_profile=BrowserProfile(),
    auto_solve_captchas=False
)
```

## API Reference

### StealthBrowserSession Parameters

- `auto_solve_captchas: bool = True` - Whether to automatically detect and solve captchas
- `capsolver_api_key: Optional[str] = None` - Capsolver API key for fallback solving

### Methods

#### `solve_captchas_manually(timeout: float = 60) -> bool`
Manually trigger captcha detection and solving on the current page.

**Parameters:**
- `timeout`: Maximum time to wait for captcha solving (seconds)

**Returns:**
- `bool`: True if captchas were found and solved, False otherwise

#### `wait_for_captcha_resolution(timeout: float = 60) -> bool`
Wait for any ongoing captcha solving to complete.

**Parameters:**
- `timeout`: Maximum time to wait (seconds)

**Returns:**
- `bool`: True if captcha was resolved, False if timeout

## How It Works

### Automatic Detection
When `auto_solve_captchas=True`, the system automatically:

1. **On page navigation**: Scans for captchas after each `navigate()` call
2. **On page refresh**: Scans for captchas after each `refresh()` call
3. **Detection process**: Checks for various captcha types and bot detection systems

### Solving Priority
1. **reCAPTCHA v2/v3**: Solved using playwright-recaptcha (no API key required)
2. **Other captchas**: Solved using Capsolver (requires API key)
3. **Bot detection**: Handled using appropriate methods for each system

### Error Handling
- If captcha solving fails, the system logs the error and continues
- Multiple retry attempts are made for transient failures
- Fallback methods are used when primary solving fails

## Troubleshooting

### Common Issues

1. **"No Capsolver API key found" warning**
   - This is normal if you only need reCAPTCHA v2/v3 solving
   - Add `CAPSOLVER_API_KEY` to `.env` if you need other captcha types

2. **Captcha solving timeout**
   - Increase the timeout parameter
   - Check your internet connection
   - Verify the captcha type is supported

3. **Audio processing errors**
   - Install ffmpeg: `apt-get install ffmpeg` (Linux) or `brew install ffmpeg` (macOS)
   - Required for audio captcha solving

### Debug Logging

Enable debug logging to see detailed captcha solving information:

```python
import logging
logging.getLogger('browser_use.captcha').setLevel(logging.DEBUG)
```

## Testing

Run the integration tests to verify everything is working:

```bash
# Simple integration test
python test_captcha_simple.py

# Full browser test (requires display/headless environment)
python test_captcha_integration.py
```

## Limitations

1. **Capsolver API costs**: Fallback captcha solving using Capsolver incurs API costs
2. **Success rates**: Captcha solving success rates vary by captcha type and complexity
3. **Detection time**: Some captchas may take time to appear after page load
4. **Bot detection**: Some advanced bot detection systems may still block automation

## Support

For issues related to:
- **reCAPTCHA solving**: Check [playwright-recaptcha documentation](https://github.com/Xewdy444/Playwright-reCAPTCHA)
- **Other captcha types**: Check [capsolver documentation](https://github.com/capsolver/capsolver-python)
- **Integration issues**: Create an issue in this repository