#!/usr/bin/env python3
"""
Test script for captcha solving integration in browser-use-undetected.
This script tests the captcha detection and solving capabilities.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from browser_use.browser import StealthBrowserSession
from browser_use.browser.profile import BrowserProfile


async def test_captcha_integration():
    """Test the captcha solving integration."""
    print("🧪 Testing captcha solving integration...")
    
    # Create a browser session with captcha solving enabled
    session = StealthBrowserSession(
        browser_profile=BrowserProfile(),
        auto_solve_captchas=True
    )
    
    try:
        # Start the browser session
        print("🚀 Starting browser session...")
        await session.start()
        print("✅ Browser session started successfully")
        
        # Test navigation to a page with potential captchas
        print("🌐 Navigating to test page...")
        await session.navigate("https://www.google.com/recaptcha/api2/demo")
        
        # Wait a moment for the page to load
        await asyncio.sleep(3)
        
        # Test manual captcha solving
        print("🔍 Testing manual captcha solving...")
        solved = await session.solve_captchas_manually(timeout=10)
        if solved:
            print("✅ Captchas solved successfully!")
        else:
            print("ℹ️ No captchas found or solving not needed")
        
        # Test waiting for captcha resolution
        print("⏳ Testing captcha resolution waiting...")
        clear = await session.wait_for_captcha_resolution(timeout=5)
        if clear:
            print("✅ Page is clear of captchas")
        else:
            print("⚠️ Captcha resolution timeout or issues detected")
        
        print("🎉 Captcha integration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during captcha integration test: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up
        print("🧹 Cleaning up...")
        try:
            await session.stop()
            print("✅ Browser session stopped")
        except Exception as e:
            print(f"⚠️ Error stopping session: {e}")


async def test_captcha_solver_import():
    """Test that the captcha solver can be imported and initialized."""
    print("📦 Testing captcha solver import...")
    
    try:
        from browser_use.captcha import CaptchaSolver
        print("✅ CaptchaSolver imported successfully")
        
        # Test initialization without page (should not fail)
        solver = CaptchaSolver(page=None)
        print("✅ CaptchaSolver initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing or initializing CaptchaSolver: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("🔧 Browser-use-undetected Captcha Integration Test")
    print("=" * 50)
    
    # Test 1: Import test
    import_success = await test_captcha_solver_import()
    if not import_success:
        print("❌ Import test failed, skipping integration test")
        return
    
    print("\n" + "=" * 50)
    
    # Test 2: Integration test
    await test_captcha_integration()
    
    print("\n" + "=" * 50)
    print("🏁 All tests completed!")


if __name__ == "__main__":
    # Set up environment
    os.environ.setdefault('CAPSOLVER_API_KEY', '')  # Optional
    
    # Run tests
    asyncio.run(main())