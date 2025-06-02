"""
Test script for browser-use-stealth addon
"""
import asyncio
import os
from langchain_openai import ChatOpenAI
from browser_use.agent.service import Agent
from browser_use_undetected import StealthAgent, StealthBrowserSession, PROXY


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
        task="Navigate to https://httpbin.org/ip and tell me what ip is being used",
        llm=llm,
        auto_solve_captchas=True,
        proxy=PROXY(),
    )
    await stealth_agent.run()

    # Test 2: Using StealthBrowserSession with regular Agent
    print("\n2. Testing StealthBrowserSession with regular Agent...")
    stealth_session = StealthBrowserSession(
        auto_solve_captchas=True
    )
    regular_agent = Agent(
        task="Navigate to https://httpbin.org/ip and tell me what ip is being used",
        llm=llm,
        browser_session=stealth_session
    )
    await regular_agent.run()

    print("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(test_stealth_addon())