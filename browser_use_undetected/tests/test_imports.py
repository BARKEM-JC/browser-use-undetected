"""
Test script to verify browser-use-stealth addon imports work correctly
"""

def test_imports():
    """Test that all imports work correctly"""
    print("Testing browser-use-stealth addon imports...")
    
    try:
        # Test importing base browser-use classes
        from browser_use.agent.service import Agent
        from browser_use.browser.session import BrowserSession
        print("✅ Base browser-use imports successful")
        
        # Test importing stealth addon classes
        from browser_use_undetected import StealthAgent, StealthBrowserSession, PROXY
        print("✅ Stealth addon imports successful")
        
        # Test importing stealth captcha module
        from browser_use_undetected.stealth_captcha import CaptchaSolver
        print("✅ Stealth captcha imports successful")
        
        # Test that classes are properly defined
        assert issubclass(StealthAgent, Agent), "StealthAgent should inherit from Agent"
        assert issubclass(StealthBrowserSession, BrowserSession), "StealthBrowserSession should inherit from BrowserSession"
        print("✅ Class inheritance verified")
        
        # Test PROXY function
        proxy_config = PROXY(
            host="proxy.example.com",
            port="8080",
            username="user",
            password="pass"
        )
        assert isinstance(proxy_config, dict), "PROXY should return a dict"
        assert "server" in proxy_config, "PROXY should contain server"
        print("✅ PROXY function works correctly")
        
        print("\n🎉 All tests passed! The browser-use-stealth addon is properly configured.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_imports()