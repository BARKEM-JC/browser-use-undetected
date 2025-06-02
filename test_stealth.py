"""
Test script for browser-use-stealth addon
"""
import asyncio
import os
from langchain_openai import ChatOpenAI

# Import base browser-use classes
from browser_use.agent.service import Agent
from browser_use.browser.session import BrowserSession

# Import stealth classes to override
from browser_use_stealth import StealthAgent, StealthBrowserSession

async def test_stealth_addon():
    """Test the stealth addon functionality"""
    
    # Set up OpenAI LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    print("Testing Browser Use Stealth Addon...")
    
    # Test 1: Using StealthAgent directly
    print("\n1. Testing StealthAgent...")
    stealth_agent = StealthAgent(
        task="Navigate to https://httpbin.org/user-agent and tell me what user agent is being used",
        llm=llm,
        auto_solve_captchas=True
    )
    
    try:
        result = await stealth_agent.run()
        print(f"StealthAgent result: {result}")
    except Exception as e:
        print(f"StealthAgent error: {e}")
    
    # Test 2: Using StealthBrowserSession with regular Agent
    print("\n2. Testing StealthBrowserSession with regular Agent...")
    stealth_session = StealthBrowserSession(
        auto_solve_captchas=True
    )
    
    regular_agent = Agent(
        task="Navigate to https://httpbin.org/headers and tell me what headers are being sent",
        llm=llm,
        browser_session=stealth_session
    )
    
    try:
        result = await regular_agent.run()
        print(f"Regular Agent with StealthSession result: {result}")
    except Exception as e:
        print(f"Regular Agent with StealthSession error: {e}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(test_stealth_addon())