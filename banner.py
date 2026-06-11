from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from pyfiglet import figlet_format


def get_banner() -> Panel:
    banner_text = figlet_format("SUBZER0", font="slant")
    styled_banner = Text(banner_text, style="bold cyan")
    return Panel.fit(
        styled_banner,
        border_style="bright_blue",
        title="[bold white]❄ SubZero Recon Framework ❄[/bold white]",
        subtitle="[bold green]Built by SecurityGeek[/bold green]",
    )


def show_banner():
    Console().print(get_banner())
