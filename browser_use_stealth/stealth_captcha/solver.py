import asyncio
import logging
import os
from typing import Optional, Dict, Any, Union
from urllib.parse import urlparse

import capsolver
from playwright.async_api import Page
from playwright_recaptcha import AsyncSolverV2, AsyncSolverV3
from playwright_recaptcha.errors import RecaptchaNotFoundError, RecaptchaTimeoutError, RecaptchaSolveError

logger = logging.getLogger(__name__)


class CaptchaSolver:
    """
    Comprehensive captcha and bot detection solver that automatically detects and solves:
    - reCAPTCHA v2 and v3 (using playwright-recaptcha)
    - All other captcha types and bot detection (using capsolver as fallback)
    - Cloudflare, CloudFront, and other bot detection systems
    """

    def __init__(self, page: Page, capsolver_api_key: Optional[str] = None):
        self.page = page
        self.capsolver_api_key = capsolver_api_key or os.getenv('CAPSOLVER_API_KEY')
        
        # Initialize solvers
        self.recaptcha_v2_solver = None
        self.recaptcha_v3_solver = None
        
        if self.capsolver_api_key:
            capsolver.api_key = self.capsolver_api_key
            logger.info("Capsolver API key configured for fallback captcha solving")
        else:
            logger.warning("No Capsolver API key found. Fallback captcha solving will be disabled.")

    async def detect_and_solve_captchas(self, timeout: float = 30) -> bool:
        """
        Automatically detect and solve any captchas or bot detection on the current page.
        
        Args:
            timeout: Maximum time to wait for captcha solving
            
        Returns:
            bool: True if captchas were found and solved, False if no captchas detected
        """
        logger.info("Scanning page for captchas and bot detection...")
        
        # Check for various captcha types and bot detection
        detection_results = await self._detect_captcha_types()
        
        if not detection_results['has_captcha']:
            logger.debug("No captchas detected on current page")
            return False
            
        logger.info(f"Detected captcha types: {detection_results['types']}")
        
        # Solve detected captchas in order of priority
        solved = False
        
        # Try reCAPTCHA v2 first (most common)
        if 'recaptcha_v2' in detection_results['types']:
            solved = await self._solve_recaptcha_v2(timeout)
            if solved:
                return True
                
        # Try reCAPTCHA v3
        if 'recaptcha_v3' in detection_results['types']:
            solved = await self._solve_recaptcha_v3(timeout)
            if solved:
                return True
                
        # Try other captcha types with capsolver
        if detection_results['types'] and self.capsolver_api_key:
            solved = await self._solve_with_capsolver(detection_results, timeout)
            if solved:
                return True
                
        # Handle Cloudflare/CloudFront detection
        if detection_results['cloudflare'] or detection_results['cloudfront']:
            solved = await self._handle_bot_detection(detection_results, timeout)
            if solved:
                return True
                
        logger.warning("Failed to solve detected captchas/bot detection")
        return False

    async def _detect_captcha_types(self) -> Dict[str, Any]:
        """Detect various types of captchas and bot detection systems on the page."""
        detection_results = {
            'has_captcha': False,
            'types': [],
            'cloudflare': False,
            'cloudfront': False,
            'hcaptcha': False,
            'funcaptcha': False,
            'geetest': False,
            'turnstile': False
        }
        
        try:
            # Check for reCAPTCHA v2
            recaptcha_v2_elements = await self.page.query_selector_all('.g-recaptcha, [data-sitekey], iframe[src*="recaptcha"]')
            if recaptcha_v2_elements:
                detection_results['types'].append('recaptcha_v2')
                detection_results['has_captcha'] = True
                logger.debug("Detected reCAPTCHA v2")
                
            # Check for reCAPTCHA v3 (usually invisible)
            recaptcha_v3_script = await self.page.query_selector('script[src*="recaptcha/api.js"]')
            if recaptcha_v3_script or await self.page.evaluate('() => window.grecaptcha !== undefined'):
                detection_results['types'].append('recaptcha_v3')
                detection_results['has_captcha'] = True
                logger.debug("Detected reCAPTCHA v3")
                
            # Check for hCaptcha
            hcaptcha_elements = await self.page.query_selector_all('.h-captcha, [data-hcaptcha-sitekey]')
            if hcaptcha_elements:
                detection_results['types'].append('hcaptcha')
                detection_results['hcaptcha'] = True
                detection_results['has_captcha'] = True
                logger.debug("Detected hCaptcha")
                
            # Check for FunCaptcha
            funcaptcha_elements = await self.page.query_selector_all('[data-pkey], .funcaptcha, #funcaptcha')
            if funcaptcha_elements:
                detection_results['types'].append('funcaptcha')
                detection_results['funcaptcha'] = True
                detection_results['has_captcha'] = True
                logger.debug("Detected FunCaptcha")
                
            # Check for GeeTest
            geetest_elements = await self.page.query_selector_all('.geetest_holder, .geetest_widget')
            if geetest_elements:
                detection_results['types'].append('geetest')
                detection_results['geetest'] = True
                detection_results['has_captcha'] = True
                logger.debug("Detected GeeTest")
                
            # Check for Cloudflare Turnstile
            turnstile_elements = await self.page.query_selector_all('.cf-turnstile, [data-cf-turnstile-sitekey]')
            if turnstile_elements:
                detection_results['types'].append('turnstile')
                detection_results['turnstile'] = True
                detection_results['has_captcha'] = True
                logger.debug("Detected Cloudflare Turnstile")
                
            # Check for Cloudflare bot detection
            page_content = await self.page.content()
            if any(indicator in page_content.lower() for indicator in [
                'cloudflare', 'cf-browser-verification', 'checking your browser',
                'ddos protection', 'security check', 'ray id'
            ]):
                detection_results['cloudflare'] = True
                detection_results['has_captcha'] = True
                logger.debug("Detected Cloudflare bot detection")
                
            # Check for CloudFront bot detection
            if any(indicator in page_content.lower() for indicator in [
                'cloudfront', 'aws cloudfront', 'request blocked'
            ]):
                detection_results['cloudfront'] = True
                detection_results['has_captcha'] = True
                logger.debug("Detected CloudFront bot detection")
                
            # Check page title and URL for common bot detection patterns
            title = await self.page.title()
            url = self.page.url
            
            bot_detection_patterns = [
                'access denied', 'blocked', 'security check', 'verification',
                'bot detection', 'suspicious activity', 'please wait'
            ]
            
            if any(pattern in title.lower() for pattern in bot_detection_patterns):
                detection_results['has_captcha'] = True
                logger.debug(f"Detected bot detection in page title: {title}")
                
        except Exception as e:
            logger.error(f"Error during captcha detection: {e}")
            
        return detection_results

    async def _solve_recaptcha_v2(self, timeout: float = 30) -> bool:
        """Solve reCAPTCHA v2 using playwright-recaptcha."""
        try:
            if not self.recaptcha_v2_solver:
                self.recaptcha_v2_solver = AsyncSolverV2(
                    self.page,
                    attempts=3,
                    capsolver_api_key=self.capsolver_api_key
                )
                
            logger.info("Attempting to solve reCAPTCHA v2...")
            await asyncio.wait_for(self.recaptcha_v2_solver.solve_recaptcha(), timeout=timeout)
            logger.info("Successfully solved reCAPTCHA v2")
            return True
            
        except RecaptchaNotFoundError:
            logger.debug("reCAPTCHA v2 not found on page")
            return False
        except RecaptchaTimeoutError:
            logger.warning("reCAPTCHA v2 solving timed out")
            return False
        except RecaptchaSolveError as e:
            logger.error(f"Failed to solve reCAPTCHA v2: {e}")
            return False
        except asyncio.TimeoutError:
            logger.warning("reCAPTCHA v2 solving timed out")
            return False
        except Exception as e:
            logger.error(f"Unexpected error solving reCAPTCHA v2: {e}")
            return False

    async def _solve_recaptcha_v3(self, timeout: float = 30) -> bool:
        """Solve reCAPTCHA v3 using playwright-recaptcha."""
        try:
            if not self.recaptcha_v3_solver:
                self.recaptcha_v3_solver = AsyncSolverV3(self.page, timeout=timeout)
                
            logger.info("Attempting to solve reCAPTCHA v3...")
            await self.recaptcha_v3_solver.solve_recaptcha()
            logger.info("Successfully solved reCAPTCHA v3")
            return True
            
        except RecaptchaNotFoundError:
            logger.debug("reCAPTCHA v3 not found on page")
            return False
        except RecaptchaTimeoutError:
            logger.warning("reCAPTCHA v3 solving timed out")
            return False
        except RecaptchaSolveError as e:
            logger.error(f"Failed to solve reCAPTCHA v3: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error solving reCAPTCHA v3: {e}")
            return False

    async def _solve_with_capsolver(self, detection_results: Dict[str, Any], timeout: float = 30) -> bool:
        """Solve captchas using capsolver as fallback."""
        if not self.capsolver_api_key:
            logger.warning("Capsolver API key not available for fallback solving")
            return False
            
        try:
            logger.info("Attempting to solve captcha with Capsolver...")
            
            # Get page information
            url = self.page.url
            domain = urlparse(url).netloc
            
            # Try different captcha types based on detection
            if detection_results['hcaptcha']:
                return await self._solve_hcaptcha_with_capsolver(domain, timeout)
            elif detection_results['funcaptcha']:
                return await self._solve_funcaptcha_with_capsolver(domain, timeout)
            elif detection_results['geetest']:
                return await self._solve_geetest_with_capsolver(domain, timeout)
            elif detection_results['turnstile']:
                return await self._solve_turnstile_with_capsolver(domain, timeout)
            else:
                # Try generic image captcha solving
                return await self._solve_image_captcha_with_capsolver(timeout)
                
        except Exception as e:
            logger.error(f"Error solving captcha with Capsolver: {e}")
            return False

    async def _solve_hcaptcha_with_capsolver(self, domain: str, timeout: float = 30) -> bool:
        """Solve hCaptcha using Capsolver."""
        try:
            # Get hCaptcha sitekey
            sitekey_element = await self.page.query_selector('[data-hcaptcha-sitekey]')
            if not sitekey_element:
                logger.error("Could not find hCaptcha sitekey")
                return False
                
            sitekey = await sitekey_element.get_attribute('data-hcaptcha-sitekey')
            
            # Solve with Capsolver
            solution = capsolver.solve({
                "type": "HCaptchaTaskProxyless",
                "websiteURL": self.page.url,
                "websiteKey": sitekey,
            })
            
            if solution and 'gRecaptchaResponse' in solution:
                # Inject solution
                await self.page.evaluate(f"""
                    document.querySelector('[name="h-captcha-response"]').value = '{solution['gRecaptchaResponse']}';
                    if (window.hcaptcha && window.hcaptcha.submit) {{
                        window.hcaptcha.submit();
                    }}
                """)
                logger.info("Successfully solved hCaptcha with Capsolver")
                return True
                
        except Exception as e:
            logger.error(f"Error solving hCaptcha with Capsolver: {e}")
            
        return False

    async def _solve_funcaptcha_with_capsolver(self, domain: str, timeout: float = 30) -> bool:
        """Solve FunCaptcha using Capsolver."""
        try:
            # Get FunCaptcha public key
            pkey_element = await self.page.query_selector('[data-pkey]')
            if not pkey_element:
                logger.error("Could not find FunCaptcha public key")
                return False
                
            pkey = await pkey_element.get_attribute('data-pkey')
            
            # Solve with Capsolver
            solution = capsolver.solve({
                "type": "FunCaptchaTaskProxyless",
                "websiteURL": self.page.url,
                "websitePublicKey": pkey,
            })
            
            if solution and 'token' in solution:
                # Inject solution
                await self.page.evaluate(f"""
                    if (window.parent && window.parent.postMessage) {{
                        window.parent.postMessage({{
                            eventId: 'challenge-complete',
                            payload: {{
                                sessionToken: '{solution['token']}'
                            }}
                        }}, '*');
                    }}
                """)
                logger.info("Successfully solved FunCaptcha with Capsolver")
                return True
                
        except Exception as e:
            logger.error(f"Error solving FunCaptcha with Capsolver: {e}")
            
        return False

    async def _solve_geetest_with_capsolver(self, domain: str, timeout: float = 30) -> bool:
        """Solve GeeTest using Capsolver."""
        try:
            # GeeTest solving requires more complex integration
            # This is a simplified version
            solution = capsolver.solve({
                "type": "GeeTestTaskProxyless",
                "websiteURL": self.page.url,
                "gt": await self._extract_geetest_gt(),
                "challenge": await self._extract_geetest_challenge(),
            })
            
            if solution:
                logger.info("Successfully solved GeeTest with Capsolver")
                return True
                
        except Exception as e:
            logger.error(f"Error solving GeeTest with Capsolver: {e}")
            
        return False

    async def _solve_turnstile_with_capsolver(self, domain: str, timeout: float = 30) -> bool:
        """Solve Cloudflare Turnstile using Capsolver."""
        try:
            # Get Turnstile sitekey
            sitekey_element = await self.page.query_selector('[data-cf-turnstile-sitekey]')
            if not sitekey_element:
                logger.error("Could not find Turnstile sitekey")
                return False
                
            sitekey = await sitekey_element.get_attribute('data-cf-turnstile-sitekey')
            
            # Solve with Capsolver
            solution = capsolver.solve({
                "type": "AntiTurnstileTaskProxyless",
                "websiteURL": self.page.url,
                "websiteKey": sitekey,
            })
            
            if solution and 'token' in solution:
                # Inject solution
                await self.page.evaluate(f"""
                    const responseElement = document.querySelector('[name="cf-turnstile-response"]');
                    if (responseElement) {{
                        responseElement.value = '{solution['token']}';
                    }}
                """)
                logger.info("Successfully solved Turnstile with Capsolver")
                return True
                
        except Exception as e:
            logger.error(f"Error solving Turnstile with Capsolver: {e}")
            
        return False

    async def _solve_image_captcha_with_capsolver(self, timeout: float = 30) -> bool:
        """Solve image-based captcha using Capsolver."""
        try:
            # Look for captcha images
            captcha_images = await self.page.query_selector_all('img[src*="captcha"], img[alt*="captcha"], .captcha img')
            
            if not captcha_images:
                return False
                
            # Get the first captcha image
            captcha_img = captcha_images[0]
            img_src = await captcha_img.get_attribute('src')
            
            if img_src:
                # Convert to base64 if needed
                if img_src.startswith('data:image'):
                    img_data = img_src.split(',')[1]
                else:
                    # Download image and convert to base64
                    response = await self.page.request.get(img_src)
                    import base64
                    img_data = base64.b64encode(await response.body()).decode()
                
                # Solve with Capsolver
                solution = capsolver.solve({
                    "type": "ImageToTextTask",
                    "body": img_data,
                })
                
                if solution and 'text' in solution:
                    # Find input field and fill it
                    captcha_input = await self.page.query_selector('input[name*="captcha"], input[id*="captcha"], .captcha input')
                    if captcha_input:
                        await captcha_input.fill(solution['text'])
                        logger.info("Successfully solved image captcha with Capsolver")
                        return True
                        
        except Exception as e:
            logger.error(f"Error solving image captcha with Capsolver: {e}")
            
        return False

    async def _handle_bot_detection(self, detection_results: Dict[str, Any], timeout: float = 30) -> bool:
        """Handle Cloudflare/CloudFront bot detection."""
        try:
            logger.info("Handling bot detection...")
            
            # Wait for potential automatic resolution
            await asyncio.sleep(5)
            
            # Check if we're still on a bot detection page
            current_detection = await self._detect_captcha_types()
            
            if not current_detection['cloudflare'] and not current_detection['cloudfront']:
                logger.info("Bot detection resolved automatically")
                return True
                
            # If Cloudflare challenge is present, try to solve it
            if detection_results['cloudflare']:
                return await self._solve_cloudflare_challenge(timeout)
                
            # For other bot detection, wait and retry
            max_wait = min(timeout, 30)
            wait_time = 0
            
            while wait_time < max_wait:
                await asyncio.sleep(2)
                wait_time += 2
                
                current_detection = await self._detect_captcha_types()
                if not current_detection['cloudflare'] and not current_detection['cloudfront']:
                    logger.info("Bot detection resolved after waiting")
                    return True
                    
            logger.warning("Bot detection not resolved within timeout")
            return False
            
        except Exception as e:
            logger.error(f"Error handling bot detection: {e}")
            return False

    async def _solve_cloudflare_challenge(self, timeout: float = 30) -> bool:
        """Solve Cloudflare challenge."""
        try:
            # Look for Cloudflare challenge elements
            challenge_elements = await self.page.query_selector_all('.cf-browser-verification, #cf-challenge-running')
            
            if challenge_elements:
                logger.info("Waiting for Cloudflare challenge to complete...")
                
                # Wait for challenge to complete
                max_wait = min(timeout, 30)
                wait_time = 0
                
                while wait_time < max_wait:
                    await asyncio.sleep(1)
                    wait_time += 1
                    
                    # Check if challenge is complete
                    challenge_running = await self.page.query_selector('#cf-challenge-running')
                    if not challenge_running:
                        logger.info("Cloudflare challenge completed")
                        return True
                        
                logger.warning("Cloudflare challenge did not complete within timeout")
                return False
                
        except Exception as e:
            logger.error(f"Error solving Cloudflare challenge: {e}")
            
        return False

    async def _extract_geetest_gt(self) -> Optional[str]:
        """Extract GeeTest GT parameter."""
        try:
            return await self.page.evaluate("""
                () => {
                    const scripts = document.querySelectorAll('script');
                    for (const script of scripts) {
                        const content = script.textContent || script.innerText;
                        const match = content.match(/gt['"\\s]*:['"\\s]*([a-f0-9]{32})/i);
                        if (match) return match[1];
                    }
                    return null;
                }
            """)
        except:
            return None

    async def _extract_geetest_challenge(self) -> Optional[str]:
        """Extract GeeTest challenge parameter."""
        try:
            return await self.page.evaluate("""
                () => {
                    const scripts = document.querySelectorAll('script');
                    for (const script of scripts) {
                        const content = script.textContent || script.innerText;
                        const match = content.match(/challenge['"\\s]*:['"\\s]*([a-f0-9]{32})/i);
                        if (match) return match[1];
                    }
                    return null;
                }
            """)
        except:
            return None

    async def wait_for_captcha_resolution(self, timeout: float = 60) -> bool:
        """
        Wait for any captcha or bot detection to be resolved.
        Useful for monitoring pages that might show captchas later.
        
        Args:
            timeout: Maximum time to wait
            
        Returns:
            bool: True if page is clear of captchas, False if timeout
        """
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            detection_results = await self._detect_captcha_types()
            
            if not detection_results['has_captcha']:
                return True
                
            # Try to solve any detected captchas
            if detection_results['has_captcha']:
                solved = await self.detect_and_solve_captchas(timeout=10)
                if solved:
                    # Wait a bit more to ensure resolution
                    await asyncio.sleep(2)
                    final_check = await self._detect_captcha_types()
                    if not final_check['has_captcha']:
                        return True
                        
            await asyncio.sleep(1)
            
        return False