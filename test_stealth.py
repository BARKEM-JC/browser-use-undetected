#!/usr/bin/env python3
"""
Test script for browser-use-undetected stealth functionality.
Tests StealthAgent with proxy support and captcha solving.
"""

import asyncio
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from langchain_openai import ChatOpenAI
from browser_use import StealthAgent, BrowserProfile
from browser_use import stealth_utils

async def test_stealth_agent():
    """Test StealthAgent functionality with proxy."""
    print("🔧 Testing StealthAgent functionality...")
    
    try:
        # Initialize the model
        llm = ChatOpenAI(
            model='gpt-4o-mini',
            temperature=0.0,
        )
        
        # Create a simple task
        task = 'Go to google.com and search for "browser automation"'
        
        # Create browser profile with sandbox disabled (needed for running as root)
        browser_profile = BrowserProfile(
            chromium_sandbox=False,
            headless=True
        )
        
        # Create proxy configuration
        proxy = stealth_utils.PROXY(
            country_code='au', 
            city='brisbane', 
            session_time=10
        )
        
        # Create stealth agent
        agent = StealthAgent(
            task=task, 
            llm=llm,
            enable_memory=False,
            browser_profile=browser_profile,
            proxy=proxy,
            auto_solve_captchas=True
        )
        
        print(f"✅ StealthAgent created successfully with task: {task}")
        print(f"🔒 Proxy configured: {proxy['server']}")
        print("🌐 Starting stealth browser session...")
        
        # Run the agent for a short time
        await agent.run()
        
        print("✅ StealthAgent test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in StealthAgent test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_stealth_agent_no_proxy():
    """Test StealthAgent functionality without proxy."""
    print("🔧 Testing StealthAgent functionality without proxy...")
    
    try:
        # Initialize the model
        llm = ChatOpenAI(
            model='gpt-4o-mini',
            temperature=0.0,
        )
        
        # Create a simple task
        task = 'Go to google.com and search for "browser automation"'
        
        # Create browser profile with sandbox disabled (needed for running as root)
        browser_profile = BrowserProfile(
            chromium_sandbox=False,
            headless=True
        )
        
        # Create stealth agent without proxy
        agent = StealthAgent(
            task=task, 
            llm=llm,
            enable_memory=False,
            browser_profile=browser_profile,
            proxy=None,
            auto_solve_captchas=True
        )
        
        print(f"✅ StealthAgent created successfully with task: {task}")
        print("🌐 Starting stealth browser session (no proxy)...")
        
        # Run the agent for a short time
        await agent.run()
        
        print("✅ StealthAgent (no proxy) test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in StealthAgent (no proxy) test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🔧 Browser-use-undetected Stealth Functionality Test")
    print("=" * 60)
    
    # Test 1: StealthAgent without proxy
    print("\n📍 Test 1: StealthAgent without proxy")
    success1 = await test_stealth_agent_no_proxy()
    
    print("\n" + "=" * 60)
    
    # Test 2: StealthAgent with proxy
    print("\n📍 Test 2: StealthAgent with proxy")
    success2 = await test_stealth_agent()
    
    if success1 and success2:
        print("\n🎉 All stealth functionality tests passed!")
    else:
        print("\n❌ Some stealth functionality tests failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    # Handle Windows event loop
    if sys.platform.startswith("win"):
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
        exit_code = loop.run_until_complete(main())
    else:
        exit_code = asyncio.run(main())
    
    sys.exit(exit_code)