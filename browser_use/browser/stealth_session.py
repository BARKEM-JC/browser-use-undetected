import asyncio
import os
from typing import Self, Optional

import psutil
from pydantic import Field, InstanceOf, AliasChoices

from browser_use.browser.session import BrowserSession
from browser_use.browser.profile import BrowserProfile
from camoufox.async_api import AsyncCamoufox as StealthPlaywright
from camoufox.async_api import BrowserContext as StealthBrowserContext
from camoufox.async_api import Browser as StealthBrowser

from browser_use.browser.session import logger, _log_pretty_path
from browser_use.captcha import CaptchaSolver


class StealthBrowserSession(BrowserSession):
    proxy: dict | None = Field(
        default=None,
        description='Proxy URL to use for the browser, e.g. http://username:password@host:port',
        exclude=True,
    )
    playwright: InstanceOf[StealthPlaywright] | None = Field(
        default=None,
        description='Playwright library object returned by: await (playwright or patchright).async_playwright().start()',
        exclude=True,
    )
    browser: InstanceOf[StealthBrowser] | None = Field(
        default=None,
        description='playwright Browser object to use (optional)',
        validation_alias=AliasChoices('playwright_browser'),
        exclude=True,
    )
    browser_context: InstanceOf[StealthBrowserContext] | None = Field(
        default=None,
        description='playwright BrowserContext object to use (optional)',
        validation_alias=AliasChoices('playwright_browser_context', 'context'),
        exclude=True,
    )
    captcha_solver: Optional[CaptchaSolver] = Field(
        default=None,
        description='Captcha solver instance for automatic captcha detection and solving',
        exclude=True,
    )
    auto_solve_captchas: bool = Field(
        default=True,
        description='Whether to automatically detect and solve captchas',
    )
    capsolver_api_key: Optional[str] = Field(
        default=None,
        description='Capsolver API key for fallback captcha solving',
    )

    async def start(self) -> Self:
        async with self._start_lock:
            # if we're already initialized and the connection is still valid, return the existing session state and start from scratch
            if self.initialized and self.is_connected():
                return self
            self._reset_connection_state()

            self.initialized = True  # set this first to ensure two parallel calls to start() don't clash with each other
            try:
                # apply last-minute runtime-computed options to the the browser_profile, validate profile, set up folders on disk
                assert isinstance(self.browser_profile, BrowserProfile)
                self.browser_profile.prepare_user_data_dir()  # create/unlock the <user_data_dir>/SingletonLock
                self.browser_profile.detect_display_configuration()  # adjusts config values, must come before launch/connect

                # launch/connect to the browser:
                # setup playwright library client, Browser, and BrowserContext objects
                await self.setup_playwright()
                await self.setup_browser_via_passed_objects()
                await self.setup_browser_via_wss_url()
                await self.setup_new_browser_context()  # creates a new context in existing browser or launches a new persistent context
                assert self.browser_context, f'Failed to connect to or create a new BrowserContext for browser={self.browser}'

                # resize the existing pages and set up foreground tab detection
                await self._setup_viewports()
                await self._setup_current_page_change_listeners()
                
                # Initialize captcha solver if auto-solving is enabled
                if self.auto_solve_captchas:
                    await self._setup_captcha_solver()
            except Exception:
                self.initialized = False
                raise
            return self

    async def stop(self) -> None:
        """Shuts down the BrowserSession, killing the browser process if keep_alive=False"""

        self.initialized = False

        if self.browser_profile.keep_alive:
            return  # nothing to do if keep_alive=True, leave the browser running

        if self.browser_context or self.browser:
            try:
                await (self.browser_context or self.browser).close()
                logger.info(
                    f'🛑 Stopped the {self.browser_profile.channel.name.lower()} browser '
                    f'keep_alive=False user_data_dir={_log_pretty_path(self.browser_profile.user_data_dir) or "<incognito>"} cdp_url={self.cdp_url or self.wss_url} pid={self.browser_pid}'
                )
                self.browser_context = None
            except Exception as e:
                logger.debug(
                    f'❌ Error closing playwright BrowserContext {self.browser_context}: {type(e).__name__}: {e}')

        # kill the chrome subprocess if we were the ones that started it
        if self.browser_pid:
            try:
                psutil.Process(pid=self.browser_pid).terminate()
                logger.info(f' ↳ Killed browser subprocess with browser_pid={self.browser_pid} keep_alive=False')
                self.browser_pid = None
            except Exception as e:
                if 'NoSuchProcess' not in type(e).__name__:
                    logger.debug(
                        f'❌ Error terminating subprocess with browser_pid={self.browser_pid}: {type(e).__name__}: {e}')

    async def close(self) -> None:
        """Deprecated: Provides backwards-compatibility with old class method Browser().close()"""
        await self.stop()

    async def new_context(self, **kwargs):
        """Deprecated: Provides backwards-compatibility with old class method Browser().new_context()"""
        return self

    async def __aenter__(self) -> BrowserSession:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def setup_playwright(self) -> None:
        """
        Set up playwright library client object: usually the result of (await async_playwright().start())
        Override to customize the set up of the playwright or patchright library object
        """
        self.playwright = StealthPlaywright(
            geoip=True,
            proxy=self.proxy,
            humanize=True,
            headless=self.browser_profile.headless,
        )
        return self.playwright

    async def _get_playwright_async(self):
        """Get the underlying Playwright async API object for connection methods"""
        if not hasattr(self.playwright, 'browser') or not self.playwright.browser:
            await self.playwright.start()

        # Access the underlying Playwright async API
        from playwright.async_api._generated import Playwright
        playwright_impl = self.playwright.browser._impl_obj._browser_type._playwright
        return Playwright(playwright_impl)

    async def setup_browser_via_passed_objects(self) -> None:
        """Override to customize the set up of the connection to an existing browser"""

        # 1. check for a passed Page object, if present, it always takes priority, set browser_context = page.context
        self.browser_context = (self.agent_current_page and self.agent_current_page.context) or self.browser_context or None

        # 2. Check if the current browser connection is valid, if not clear the invalid objects
        if self.browser_context:
            try:
                # Try to access a property that would fail if the context is closed
                _ = self.browser_context.pages
                # Additional check: verify the browser is still connected
                if self.browser_context.browser and not self.browser_context.browser.is_connected():
                    self.browser_context = None
            except Exception:
                # Context is closed, clear it
                self.browser_context = None

        # 3. if we have a browser object but it's disconnected, clear it and the context because we cant use either
        if self.browser and not self.browser.is_connected():
            if self.browser_context and (self.browser_context.browser is self.browser):
                self.browser_context = None
            self.browser = None

        # 4. if we have a context now, it always takes precedence, set browser = context.browser, otherwise use the passed browser
        browser_from_context = self.browser_context and self.browser_context.browser
        if browser_from_context and browser_from_context.is_connected():
            self.browser = browser_from_context

        if self.browser or self.browser_context:
            logger.info(f'🌎 Connected to existing user-provided browser_context: {self.browser_context}')
            self._set_browser_keep_alive(True)  # we connected to an existing browser, dont kill it at the end

    async def setup_browser_via_browser_pid(self) -> None:
        """if browser_pid is provided, calcuclate its CDP URL by looking for --remote-debugging-port=... in its CLI args, then connect to it"""
        # NOTE: This function is not supported with Camoufox/Firefox because:
        # 1. Firefox doesn't support CDP (Chrome DevTools Protocol) connections
        # 2. Firefox uses its own remote debugging protocol which is not compatible with Playwright's connect_over_cdp
        # 3. The only remote connection method for Firefox is via WebSocket to a Playwright server
        logger.warning(
            "🚨 setup_browser_via_browser_pid is not supported with Camoufox/Firefox. "
            "Firefox doesn't support CDP connections. Use setup_browser_via_wss_url for remote connections."
        )
        return

    async def setup_browser_via_wss_url(self) -> None:
        """check for a passed wss_url, connect to a remote playwright browser server via WSS"""
        if self.browser or self.browser_context:
            return  # already connected to a browser
        if not self.wss_url:
            return  # no wss_url provided, nothing to do

        logger.info(f'🌎 Connecting to existing remote Firefox playwright node.js server over WSS: {self.wss_url}')

        playwright_async = await self._get_playwright_async()
        self.browser = self.browser or await playwright_async.firefox.connect(
            self.wss_url,
            **self.browser_profile.kwargs_for_connect().model_dump(),
        )
        self._set_browser_keep_alive(True)  # we connected to an existing browser, dont kill it at the end

    async def setup_browser_via_cdp_url(self) -> None:
        """check for a passed cdp_url, connect to a remote Firefox-based browser via CDP"""
        # NOTE: This function is not supported with Camoufox/Firefox because:
        # 1. Firefox doesn't support CDP (Chrome DevTools Protocol) connections
        # 2. CDP is a Chromium-specific protocol
        # 3. The only remote connection method for Firefox is via WebSocket to a Playwright server
        logger.warning(
            "🚨 setup_browser_via_cdp_url is not supported with Camoufox/Firefox. "
            "Firefox doesn't support CDP connections. Use setup_browser_via_wss_url for remote connections."
        )
        return

    async def setup_new_browser_context(self) -> None:
        """Launch a new browser and browser_context"""
        # For Camoufox, we need to handle browser and context creation differently
        current_process = psutil.Process(os.getpid())
        child_pids_before_launch = {child.pid for child in current_process.children(recursive=True)}

        # if we have a browser object but no browser_context, use the first context discovered or make a new one
        if self.browser and not self.browser_context:
            if self.browser.contexts:
                self.browser_context = self.browser.contexts[0]
                logger.info(f'🌎 Using first browser_context available in existing browser: {self.browser_context}')
            else:
                self.browser_context = await self.browser.new_context(
                    **self.browser_profile.kwargs_for_new_context().model_dump()
                )
                storage_info = (
                    f' + loaded storage_state={len(self.browser_profile.storage_state.cookies) if self.browser_profile.storage_state else 0} cookies'
                    if self.browser_profile.storage_state
                    else ''
                )
                logger.info(
                    f'🌎 Created new empty browser_context in existing browser{storage_info}: {self.browser_context}')

        # If we still don't have a browser, create one using Camoufox
        if not self.browser:
            logger.info(
                f'🌎 Launching local browser '
                f'driver=camoufox channel={self.browser_profile.channel.name.lower()} '
                f'user_data_dir={_log_pretty_path(self.browser_profile.user_data_dir) if self.browser_profile.user_data_dir else "<incognito>"}'
            )

            await self.playwright.start()
            self.browser = self.playwright.browser

            # Create browser context with appropriate settings
            if not self.browser_context:
                context_kwargs = self.browser_profile.kwargs_for_new_context().model_dump()

                # Filter out Firefox-unsupported permissions for Camoufox
                if 'permissions' in context_kwargs:
                    firefox_supported_permissions = ['notifications', 'geolocation', 'camera', 'microphone']
                    context_kwargs['permissions'] = [
                        perm for perm in context_kwargs['permissions']
                        if perm in firefox_supported_permissions
                    ]

                self.browser_context = await self.browser.new_context(**context_kwargs)
                storage_info = (
                    f' + loaded storage_state={len(self.browser_profile.storage_state.cookies) if self.browser_profile.storage_state else 0} cookies'
                    if self.browser_profile.storage_state
                    else ''
                )
                logger.info(f'🌎 Created new browser_context{storage_info}: {self.browser_context}')

        # Detect any new child camoufox processes that we might have launched above
        try:
            child_pids_after_launch = {child.pid for child in current_process.children(recursive=True)}
            new_child_pids = child_pids_after_launch - child_pids_before_launch
            new_child_procs = [psutil.Process(pid) for pid in new_child_pids]
            new_camoufox_procs = [proc for proc in new_child_procs if
                                  'Helper' not in proc.name() and proc.status() == 'running']
        except Exception as e:
            logger.debug(
                f'❌ Error trying to find child camoufox processes after launching new browser: {type(e).__name__}: {e}')
            new_camoufox_procs = []

        if new_camoufox_procs and not self.browser_pid:
            self.browser_pid = new_camoufox_procs[0].pid
            logger.debug(
                f' ↳ Spawned browser subprocess: browser_pid={self.browser_pid} {" ".join(new_camoufox_procs[0].cmdline())}'
            )
            self._set_browser_keep_alive(False)  # close the browser at the end because we launched it

        if self.browser:
            connection_method = 'WSS' if self.wss_url else 'CDP' if (self.cdp_url and not self.browser_pid) else 'Local'
            assert self.browser.is_connected(), (
                f'Browser is not connected, did the browser process crash or get killed? (connection method: {connection_method})'
            )
            logger.debug(
                f'🌎 {connection_method} browser connected: v{self.browser.version} {self.cdp_url or self.wss_url or self.browser_profile.executable_path or "(camoufox)"}'
            )

        assert self.browser_context, (
            f'Failed to create a playwright BrowserContext {self.browser_context} for browser={self.browser}'
        )

        # Add anti-detection scripts and setup
        init_script = """
					// check to make sure we're not inside the PDF viewer
					window.isPdfViewer = !!document?.body?.querySelector('body > embed[type="application/pdf"][width="100%"]')
					if (!window.isPdfViewer) {

						// Permissions
						const originalQuery = window.navigator.permissions.query;
						window.navigator.permissions.query = (parameters) => (
							parameters.name === 'notifications' ?
								Promise.resolve({ state: Notification.permission }) :
								originalQuery(parameters)
						);
						(() => {
							if (window._eventListenerTrackerInitialized) return;
							window._eventListenerTrackerInitialized = true;

							const originalAddEventListener = EventTarget.prototype.addEventListener;
							const eventListenersMap = new WeakMap();

							EventTarget.prototype.addEventListener = function(type, listener, options) {
								if (listener && typeof listener === 'function') {
									let listeners = eventListenersMap.get(this);
									if (!listeners) {
										listeners = [];
										eventListenersMap.set(this, listeners);
									}

									listeners.push({
										type,
										listener,
										listenerPreview: listener.toString().slice(0, 100),
										options
									});
								}

								return originalAddEventListener.call(this, type, listener, options);
							};

							window.getEventListenersForNode = (node) => {
								const listeners = eventListenersMap.get(node) || [];
								return listeners.map(({ type, listenerPreview, options }) => ({
									type,
									listenerPreview,
									options
								}));
							};
						})();
					}
					"""

        # Expose anti-detection scripts
        await self.browser_context.add_init_script(init_script)

        # Load cookies from file if specified
        await self.load_cookies_from_file()

    async def _setup_captcha_solver(self) -> None:
        """Initialize the captcha solver for the current page."""
        try:
            if self.agent_current_page and not self.agent_current_page.is_closed():
                # Use instance capsolver_api_key or fall back to environment variable
                api_key = self.capsolver_api_key or os.getenv('CAPSOLVER_API_KEY')
                self.captcha_solver = CaptchaSolver(
                    page=self.agent_current_page,
                    capsolver_api_key=api_key
                )
                logger.info("Captcha solver initialized for automatic captcha detection and solving")
            else:
                logger.debug("No current page available for captcha solver initialization")
        except Exception as e:
            logger.error(f"Failed to initialize captcha solver: {e}")

    async def navigate(self, url: str) -> None:
        """Navigate to URL with automatic captcha detection and solving."""
        # Call parent navigate method
        await super().navigate(url)
        
        # Auto-solve captchas if enabled
        if self.auto_solve_captchas and self.agent_current_page:
            await self._handle_page_captchas()

    async def refresh(self) -> None:
        """Refresh page with automatic captcha detection and solving."""
        # Call parent refresh method
        await super().refresh()
        
        # Auto-solve captchas if enabled
        if self.auto_solve_captchas and self.agent_current_page:
            await self._handle_page_captchas()

    async def _handle_page_captchas(self) -> None:
        """Handle captchas on the current page."""
        try:
            if not self.captcha_solver or not self.agent_current_page:
                # Reinitialize captcha solver if needed
                await self._setup_captcha_solver()
                
            if self.captcha_solver and self.agent_current_page:
                # Update captcha solver page reference
                self.captcha_solver.page = self.agent_current_page
                
                # Wait a moment for page to load
                await asyncio.sleep(1)
                
                # Detect and solve captchas
                solved = await self.captcha_solver.detect_and_solve_captchas(timeout=30)
                if solved:
                    logger.info("Successfully solved captchas on page")
                    # Wait a bit more for any redirects after solving
                    await asyncio.sleep(2)
                    
        except Exception as e:
            logger.error(f"Error handling page captchas: {e}")

    async def solve_captchas_manually(self, timeout: float = 30) -> bool:
        """
        Manually trigger captcha solving on the current page.
        
        Args:
            timeout: Maximum time to wait for captcha solving
            
        Returns:
            bool: True if captchas were solved, False otherwise
        """
        try:
            if not self.agent_current_page:
                logger.warning("No current page available for captcha solving")
                return False
                
            if not self.captcha_solver:
                await self._setup_captcha_solver()
                
            if self.captcha_solver:
                self.captcha_solver.page = self.agent_current_page
                return await self.captcha_solver.detect_and_solve_captchas(timeout=timeout)
                
        except Exception as e:
            logger.error(f"Error in manual captcha solving: {e}")
            
        return False

    async def wait_for_captcha_resolution(self, timeout: float = 60) -> bool:
        """
        Wait for any captcha or bot detection to be resolved.
        
        Args:
            timeout: Maximum time to wait
            
        Returns:
            bool: True if page is clear of captchas, False if timeout
        """
        try:
            if not self.agent_current_page:
                logger.warning("No current page available for captcha monitoring")
                return False
                
            if not self.captcha_solver:
                await self._setup_captcha_solver()
                
            if self.captcha_solver:
                self.captcha_solver.page = self.agent_current_page
                return await self.captcha_solver.wait_for_captcha_resolution(timeout=timeout)
                
        except Exception as e:
            logger.error(f"Error waiting for captcha resolution: {e}")
            
        return False