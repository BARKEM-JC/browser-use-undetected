"""
Browser Use Stealth - Undetected browser automation addon for browser-use

This package extends browser-use with stealth capabilities using Camoufox (Firefox-based) 
to avoid detection by anti-bot systems.
"""

from .stealth_agent import StealthAgent
from .stealth_session import StealthBrowserSession
from .stealth_utils import PROXY

__all__ = ['StealthAgent', 'StealthBrowserSession', 'PROXY']
__version__ = '1.0.0'