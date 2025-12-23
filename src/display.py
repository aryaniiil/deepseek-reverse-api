from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.live import Live
from rich.rule import Rule
import time

console = Console()

def print_status(message, style="white"):
    """print status messages with style"""
    console.print(f"[{style}][[DeepSeek]][/{style}] {message}", justify="left")

def print_response_start():
    """show when response starts"""
    console.print()
    console.print(Rule("[bold cyan]Response[/bold cyan]", style="cyan", align="left"))
    console.print()

def stream_live(content_generator):
    """stream content live as it comes in with markdown rendering"""
    full_content = ""
    
    # create a panel that updates live
    with Live(console=console, refresh_per_second=10) as live:
        for chunk in content_generator:
            if chunk:
                full_content += chunk
                
                # render current content as markdown
                md = Markdown(full_content, code_theme="monokai", justify="left")
                panel = Panel(
                    md,
                    border_style="bright_cyan",
                    padding=(1, 2),
                    title="[bold white]DeepSeek[/bold white]",
                    title_align="left"
                )
                live.update(panel)
    
    return full_content

def get_user_input(prompt_text="You"):
    """get input from user with nice prompt"""
    return Prompt.ask(f"\n[bold green]{prompt_text}[/bold green]")

def print_goodbye():
    """say goodbye when exiting"""
    console.print("\n[yellow]Goodbye![/yellow]\n", justify="left")