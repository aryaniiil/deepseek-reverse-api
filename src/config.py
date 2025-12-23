import os
import time
import warnings
from dotenv import load_dotenv
from rich.console import Console

# shut up those annoying warnings
warnings.filterwarnings("ignore")

# load our secret stuff from data folder
load_dotenv("data/.env")

console = Console()

class Config:
    DEEPSEEK_EMAIL = os.getenv('DEEPSEEK_EMAIL')
    DEEPSEEK_PASSWORD = os.getenv('DEEPSEEK_PASSWORD')
    
    # browser stuff that usually works
    HEADLESS = True
    AUTH_WAIT_TIME = 10
    
    # where we keep our files now
    COOKIES_FILE = "data/deepseek_cookies.json"
    TOKEN_FILE = "data/auth_token.txt"
    LAST_LOGIN_FILE = "data/last_login.txt"
    WASM_FILE = "data/sha3_wasm_bg.7b9ca65ddd.wasm"
    
    # session expires after 1 hour (probably)
    SESSION_TIMEOUT = 3600
    
    # api settings that deepseek expects
    BASE_URL = "https://chat.deepseek.com"
    BASE_HEADERS = {
        "Host": "chat.deepseek.com",
        "User-Agent": "DeepSeek/1.0.13 Android/35",
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/json",
    }
    
    @staticmethod
    def print_status(message, style="white"):
        """print stuff with colors because it looks nice"""
        console.print(f"[{style}][DeepSeek][/{style}] {message}")
    
    @staticmethod
    def needs_reauth():
        """check if we need to login again"""
        try:
            with open(Config.LAST_LOGIN_FILE, 'r') as f:
                last_login = float(f.read().strip())
            return (time.time() - last_login) > Config.SESSION_TIMEOUT
        except:
            return True
    
    @staticmethod
    def update_login_time():
        """remember when we logged in"""
        with open(Config.LAST_LOGIN_FILE, 'w') as f:
            f.write(str(time.time()))