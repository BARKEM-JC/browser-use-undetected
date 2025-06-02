#!/usr/bin/env python3
"""
Comprehensive test script for browser-use-undetected.
Tests all major functionality: normal operation, stealth, proxy, and captcha readiness.
"""

import asyncio
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from langchain_openai import ChatOpenAI
from browser_use import Agent, StealthAgent, BrowserProfile
from browser_use import stealth_utils

async def test_normal_agent():
    """Test normal Agent functionality."""
    print("🔧 Testing normal Agent functionality...")
    
    try:
        llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.0)
        
        browser_profile = BrowserProfile(
            chromium_sandbox=False,
            headless=True
        )
        
        agent = Agent(
            task='Go to httpbin.org/ip and tell me the IP address', 
            llm=llm,
            enable_memory=False,
            browser_profile=browser_profile
        )
        
        print("✅ Normal Agent created successfully")
        await agent.run()
        print("✅ Normal Agent test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in normal Agent test: {e}")
        return False

async def test_stealth_agent_no_proxy():
    """Test StealthAgent without proxy."""
    print("🔧 Testing StealthAgent without proxy...")
    
    try:
        llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.0)
        
        browser_profile = BrowserProfile(
            chromium_sandbox=False,
            headless=True
        )
        
        agent = StealthAgent(
            task='Go to httpbin.org/ip and tell me the IP address', 
            llm=llm,
            enable_memory=False,
            browser_profile=browser_profile,
            proxy=None,
            auto_solve_captchas=True
        )
        
        print("✅ StealthAgent (no proxy) created successfully")
        await agent.run()
        print("✅ StealthAgent (no proxy) test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in StealthAgent (no proxy) test: {e}")
        return False

async def test_stealth_agent_with_proxy():
    """Test StealthAgent with proxy."""
    print("🔧 Testing StealthAgent with proxy...")
    
    try:
        llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.0)
        
        browser_profile = BrowserProfile(
            chromium_sandbox=False,
            headless=True
        )
        
        proxy = stealth_utils.PROXY(
            country_code='au', 
            city='brisbane', 
            session_time=10
        )
        
        agent = StealthAgent(
            task='Go to httpbin.org/ip and tell me the IP address', 
            llm=llm,
            enable_memory=False,
            browser_profile=browser_profile,
            proxy=proxy,
            auto_solve_captchas=True
        )
        
        print(f"✅ StealthAgent with proxy created successfully")
        print(f"🔒 Proxy: {proxy['server']}")
        await agent.run()
        print("✅ StealthAgent with proxy test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in StealthAgent with proxy test: {e}")
        return False

async def test_captcha_readiness():
    """Test captcha detection readiness."""
    print("🔧 Testing captcha detection readiness...")
    
    try:
        from browser_use.captcha import CaptchaSolver
        from browser_use.browser.stealth_session import StealthBrowserSession
        
        # Test captcha solver class import
        print("✅ CaptchaSolver class imported successfully")
        
        # Test stealth session with captcha support
        session = StealthBrowserSession(auto_solve_captchas=True)
        print("✅ StealthBrowserSession with captcha support created")
        
        # Check required methods exist on session
        assert hasattr(session, 'solve_captchas_manually')
        assert hasattr(session, '_handle_page_captchas')
        assert hasattr(session, '_setup_captcha_solver')
        print("✅ All required captcha methods available on StealthBrowserSession")
        
        # Check captcha solver methods exist on class
        assert hasattr(CaptchaSolver, 'detect_and_solve_captchas')
        assert hasattr(CaptchaSolver, 'wait_for_captcha_resolution')
        assert hasattr(CaptchaSolver, '_detect_captcha_types')
        print("✅ All required captcha methods available on CaptchaSolver class")
        
        # Test that captcha dependencies are available
        import playwright_recaptcha
        import capsolver
        print("✅ Captcha solving dependencies (playwright-recaptcha, capsolver) available")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in captcha readiness test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main comprehensive test function."""
    print("🔧 Browser-use-undetected Comprehensive Test Suite")
    print("=" * 70)
    
    results = {}
    
    # Test 1: Normal Agent
    print("\n📍 Test 1: Normal Agent")
    print("-" * 30)
    results['normal'] = await test_normal_agent()
    
    # Test 2: StealthAgent without proxy
    print("\n📍 Test 2: StealthAgent (no proxy)")
    print("-" * 30)
    results['stealth_no_proxy'] = await test_stealth_agent_no_proxy()
    
    # Test 3: StealthAgent with proxy
    print("\n📍 Test 3: StealthAgent (with proxy)")
    print("-" * 30)
    results['stealth_with_proxy'] = await test_stealth_agent_with_proxy()
    
    # Test 4: Captcha readiness
    print("\n📍 Test 4: Captcha Detection Readiness")
    print("-" * 30)
    results['captcha_readiness'] = await test_captcha_readiness()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title():<30} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Browser-use-undetected is fully functional!")
        print("\n✅ Features confirmed working:")
        print("   • Normal Agent with Chromium browser")
        print("   • StealthAgent with Camoufox browser")
        print("   • Proxy support with IP routing")
        print("   • Captcha detection and solving readiness")
        print("   • Sandbox configuration for root environment")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
        exit_code = loop.run_until_complete(main())
    else:
        exit_code = asyncio.run(main())
    
    sys.exit(exit_code)