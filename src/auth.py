import asyncio
import nodriver as uc
import json
from .config import Config

class AuthExtractor:
    def __init__(self):
        self.config = Config()
    
    async def extract_credentials(self):
        """login and grab our cookies and token"""
        
        self.config.print_status("Starting browser (this might take a sec)...", "yellow")
        browser = await uc.start(headless=self.config.HEADLESS)
        
        try:
            page = await browser.get(f"{self.config.BASE_URL}/")
            
            self.config.print_status("Waiting for page to load...", "cyan")
            await page.sleep(5)
            
            self.config.print_status("Filling in login details...", "cyan")
            email_input = await page.find('input[placeholder*="email"]', timeout=10)
            await email_input.send_keys(self.config.DEEPSEEK_EMAIL)
            await page.sleep(1)
            
            password_input = await page.find('input[type="password"]', timeout=10)
            await password_input.send_keys(self.config.DEEPSEEK_PASSWORD)
            await page.sleep(1)
            
            self.config.print_status("Clicking login button...", "cyan")
            login_btn = await page.find('div[role="button"].ds-sign-up-form__register-button', timeout=10)
            await login_btn.click()
            
            self.config.print_status(f"Waiting {self.config.AUTH_WAIT_TIME} seconds for login...", "yellow")
            await page.sleep(self.config.AUTH_WAIT_TIME)
            
            # get cookies from browser
            self.config.print_status("Grabbing cookies...", "cyan")
            cookies_raw = await page.send(uc.cdp.network.get_cookies())
            
            cookie_dict = {}
            for cookie in cookies_raw:
                cookie_dict[cookie.name] = cookie.value
            
            # get auth token from browser storage
            self.config.print_status("Getting auth token...", "cyan")
            try:
                token = await page.evaluate('JSON.parse(localStorage.getItem("userToken")).value')
                
                if token:
                    self.config.print_status(f"Got token: {token[:20]}...", "green")
                    
                    with open(self.config.TOKEN_FILE, "w") as f:
                        f.write(token)
                else:
                    self.config.print_status("Couldn't find token", "red")
                    token = None
            except Exception as e:
                self.config.print_status(f"Token extraction failed: {e}", "red")
                token = None
            
            # save cookies to file
            with open(self.config.COOKIES_FILE, "w") as f:
                json.dump(cookie_dict, f, indent=2)
            
            # remember when we logged in
            self.config.update_login_time()
            
            self.config.print_status(f"Success! Got {len(cookie_dict)} cookies", "green")
            
            # check if we got the important stuff
            ds_session = cookie_dict.get('ds_session_id', 'NOT FOUND')
            if ds_session != 'NOT FOUND':
                self.config.print_status(f"Session ID: {ds_session[:20]}...", "green")
            else:
                self.config.print_status("No session ID found", "red")
            
            return cookie_dict, token
            
        except Exception as e:
            self.config.print_status(f"Login failed: {e}", "red")
            return None, None
        
        finally:
            # close browser quietly
            if browser:
                try:
                    await browser.stop()
                except:
                    pass  # ignore cleanup errors

async def main():
    """test the auth stuff"""
    if not Config.DEEPSEEK_EMAIL or not Config.DEEPSEEK_PASSWORD:
        Config.print_status("No email/password in .env file!", "red")
        return
    
    extractor = AuthExtractor()
    cookies, token = await extractor.extract_credentials()
    
    if cookies and token:
        Config.print_status("Authentication successful!", "green")
    else:
        Config.print_status("Authentication failed!", "red")

if __name__ == "__main__":
    asyncio.run(main())