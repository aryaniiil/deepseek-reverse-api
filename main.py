import sys
import asyncio
from src.config import Config
from src.auth import AuthExtractor
from src.client import DeepSeekClient
from src.display import get_user_input, print_goodbye
from rich.console import Console

console = Console()

async def ensure_auth():
    """make sure we're logged in and ready to go"""
    if Config.needs_reauth():
        Config.print_status("Session expired, logging in...", "yellow")
        
        if not Config.DEEPSEEK_EMAIL or not Config.DEEPSEEK_PASSWORD:
            Config.print_status("No email/password in .env file!", "red")
            return False
        
        extractor = AuthExtractor()
        cookies, token = await extractor.extract_credentials()
        
        if not cookies or not token:
            Config.print_status("Login failed!", "red")
            return False
        
        Config.print_status("Login successful!", "green")
    else:
        Config.print_status("Using existing session", "green")
    
    return True

def interactive_mode():
    """run in interactive chat mode"""
    # make sure we're logged in first
    if not asyncio.run(ensure_auth()):
        sys.exit(1)
    
    client = DeepSeekClient()
    
    console.print("\n[bold cyan]Interactive Chat Mode[/bold cyan]")
    console.print("[dim]Commands: /think, /search, /exit[/dim]\n")
    
    # track current settings
    thinking = False
    search = False
    
    while True:
        try:
            prompt = get_user_input()
            
            if not prompt:
                continue
            
            # handle commands
            if prompt.strip().lower() in ['/exit', '/quit', '/q']:
                print_goodbye()
                break
            elif prompt.strip().lower() == '/think':
                thinking = not thinking
                console.print(f"[yellow]Deep thinking: {'ON' if thinking else 'OFF'}[/yellow]")
                continue
            elif prompt.strip().lower() == '/search':
                search = not search
                console.print(f"[yellow]Web search: {'ON' if search else 'OFF'}[/yellow]")
                continue
            
            # send message with current settings
            client.chat(prompt, thinking=thinking, search=search)
            
            
        except KeyboardInterrupt:
            print_goodbye()
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

def single_prompt_mode(prompt):
    """run a single prompt and exit"""
    if not asyncio.run(ensure_auth()):
        sys.exit(1)
    
    client = DeepSeekClient()
    client.chat(prompt)

def main():
    if len(sys.argv) < 2:
        # no args = interactive mode
        interactive_mode()
    else:
        # has args = single prompt mode
        prompt = " ".join(sys.argv[1:])
        single_prompt_mode(prompt)

if __name__ == "__main__":
    main()