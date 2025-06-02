#!/usr/bin/env python3
"""
Basic test script for browser-use-undetected functionality.
Tests normal Agent functionality without stealth features.
"""

import asyncio
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from langchain_openai import ChatOpenAI
from browser_use import Agent, BrowserProfile

async def test_basic_agent():
    """Test basic Agent functionality."""
    print("🔧 Testing basic Agent functionality...")
    
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
        
        # Create agent
        agent = Agent(
            task=task, 
            llm=llm,
            enable_memory=False,
            browser_profile=browser_profile
        )
        
        print(f"✅ Agent created successfully with task: {task}")
        print("🌐 Starting browser session...")
        
        # Run the agent for a short time
        await agent.run()
        
        print("✅ Basic Agent test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in basic Agent test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🔧 Browser-use-undetected Basic Functionality Test")
    print("=" * 60)
    
    # Test basic Agent
    success = await test_basic_agent()
    
    if success:
        print("\n🎉 Basic functionality test passed!")
    else:
        print("\n❌ Basic functionality test failed!")
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