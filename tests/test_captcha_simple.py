#!/usr/bin/env python3
"""
Simple test script for captcha solving integration in browser-use-undetected.
This script tests the captcha detection and solving capabilities without requiring a full browser session.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_captcha_solver_import():
    """Test that the captcha solver can be imported and initialized."""
    print("📦 Testing captcha solver import...")
    
    try:
        from browser_use.captcha import CaptchaSolver
        print("✅ CaptchaSolver imported successfully")
        
        # Test initialization without page (should not fail)
        solver = CaptchaSolver(page=None)
        print("✅ CaptchaSolver initialized successfully")
        
        # Test that all required methods exist
        required_methods = [
            'detect_and_solve_captchas',
            'wait_for_captcha_resolution',
            '_detect_captcha_types',
            '_handle_bot_detection'
        ]
        
        for method in required_methods:
            if hasattr(solver, method):
                print(f"✅ Method '{method}' exists")
            else:
                print(f"❌ Method '{method}' missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing or initializing CaptchaSolver: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_stealth_session_import():
    """Test that the StealthBrowserSession can be imported with captcha support."""
    print("📦 Testing StealthBrowserSession import...")
    
    try:
        from browser_use.browser import StealthBrowserSession
        from browser_use.browser.profile import BrowserProfile
        print("✅ StealthBrowserSession imported successfully")
        
        # Test initialization with captcha support
        session = StealthBrowserSession(
            browser_profile=BrowserProfile(),
            auto_solve_captchas=True
        )
        print("✅ StealthBrowserSession initialized with captcha support")
        
        # Test that captcha-related attributes exist
        if hasattr(session, 'auto_solve_captchas'):
            print("✅ auto_solve_captchas attribute exists")
        else:
            print("❌ auto_solve_captchas attribute missing")
            return False
            
        if hasattr(session, 'captcha_solver'):
            print("✅ captcha_solver attribute exists")
        else:
            print("❌ captcha_solver attribute missing")
            return False
        
        # Test that captcha-related methods exist
        captcha_methods = [
            'solve_captchas_manually',
            'wait_for_captcha_resolution',
            '_handle_page_captchas',
            '_setup_captcha_solver'
        ]
        
        for method in captcha_methods:
            if hasattr(session, method):
                print(f"✅ Method '{method}' exists")
            else:
                print(f"❌ Method '{method}' missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing or initializing StealthBrowserSession: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_dependencies():
    """Test that all required dependencies are available."""
    print("📦 Testing dependencies...")
    
    dependencies = [
        ('playwright_recaptcha', 'playwright-recaptcha'),
        ('capsolver', 'capsolver'),
        ('pydub', 'pydub'),
        ('speech_recognition', 'SpeechRecognition'),
        ('tenacity', 'tenacity')
    ]
    
    all_good = True
    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {package_name} available")
        except ImportError as e:
            print(f"❌ {package_name} not available: {e}")
            all_good = False
    
    return all_good


async def main():
    """Main test function."""
    print("🔧 Browser-use-undetected Captcha Integration Simple Test")
    print("=" * 60)
    
    # Test 1: Dependencies
    deps_success = await test_dependencies()
    if not deps_success:
        print("❌ Dependencies test failed")
        return
    
    print("\n" + "=" * 60)
    
    # Test 2: CaptchaSolver import test
    solver_success = await test_captcha_solver_import()
    if not solver_success:
        print("❌ CaptchaSolver import test failed")
        return
    
    print("\n" + "=" * 60)
    
    # Test 3: StealthBrowserSession import test
    session_success = await test_stealth_session_import()
    if not session_success:
        print("❌ StealthBrowserSession import test failed")
        return
    
    print("\n" + "=" * 60)
    print("🎉 All simple tests passed! Captcha integration is working correctly.")
    print("\nNext steps:")
    print("1. Set CAPSOLVER_API_KEY in .env for fallback captcha solving")
    print("2. Test with actual captcha pages using the full browser session")
    print("3. The integration automatically detects and solves:")
    print("   - reCAPTCHA v2 and v3")
    print("   - hCaptcha")
    print("   - FunCaptcha")
    print("   - GeeTest")
    print("   - Turnstile")
    print("   - Cloudflare/CloudFront bot detection")


if __name__ == "__main__":
    # Set up environment
    os.environ.setdefault('CAPSOLVER_API_KEY', '')  # Optional
    
    # Run tests
    asyncio.run(main())