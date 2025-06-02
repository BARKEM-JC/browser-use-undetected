from browser_use import Agent
from .stealth_session import StealthBrowserSession


class StealthAgent(Agent):
    def __init__(self, proxy=None, auto_solve_captchas=True, capsolver_api_key=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.browser_session = StealthBrowserSession(
            **kwargs,
            proxy=proxy,
            auto_solve_captchas=auto_solve_captchas,
            capsolver_api_key=capsolver_api_key,
        )

