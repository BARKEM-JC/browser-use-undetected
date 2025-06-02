#!/usr/bin/env python3
"""
Test script for browser-use-undetected proxy functionality.
Tests StealthAgent with proxy support.
"""

import asyncio
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from langchain_openai import ChatOpenAI
from browser_use import StealthAgent, BrowserProfile
from browser_use import stealth_utils

async def test_proxy_functionality():
    """Test StealthAgent with proxy to verify IP change."""
    print("🔧 Testing StealthAgent with proxy functionality...")
    
    try:
        # Initialize the model
        llm = ChatOpenAI(
            model='gpt-4o-mini',
            temperature=0.0,
        )
        
        # Create a task to check IP address
        task = 'Go to whatismyipaddress.com and tell me what IP address is shown'
        
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
        
        # Create stealth agent with proxy
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
        print("🌐 Starting stealth browser session with proxy...")
        
        # Run the agent for a short time
        await agent.run()
        
        print("✅ StealthAgent proxy test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in StealthAgent proxy test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_no_proxy_functionality():
    """Test StealthAgent without proxy to compare IP."""
    print("🔧 Testing StealthAgent without proxy functionality...")
    
    try:
        # Initialize the model
        llm = ChatOpenAI(
            model='gpt-4o-mini',
            temperature=0.0,
        )
        
        # Create a task to check IP address
        task = 'Go to whatismyipaddress.com and tell me what IP address is shown'
        
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
        print("🌐 Starting stealth browser session without proxy...")
        
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
    print("🔧 Browser-use-undetected Proxy Functionality Test")
    print("=" * 60)
    
    # Test 1: StealthAgent without proxy
    print("\n📍 Test 1: StealthAgent without proxy (baseline IP)")
    success1 = await test_no_proxy_functionality()
    
    print("\n" + "=" * 60)
    
    # Test 2: StealthAgent with proxy
    print("\n📍 Test 2: StealthAgent with proxy (should show different IP)")
    success2 = await test_proxy_functionality()
    
    if success1 and success2:
        print("\n🎉 All proxy functionality tests passed!")
        print("📝 Note: Check the IP addresses shown in both tests to verify proxy is working")
    else:
        print("\n❌ Some proxy functionality tests failed!")
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