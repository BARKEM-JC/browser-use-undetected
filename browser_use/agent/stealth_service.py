from browser_use.agent.service import Agent
from browser_use.browser import StealthBrowserSession


class StealthAgent(Agent):
    def __init__(self, proxy=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.browser_session = StealthBrowserSession(
            browser_profile=kwargs['browser_profile'],
            browser=kwargs['browser'],
            browser_context=kwargs['browser_context'],
            proxy=proxy,
        )

