from scanner import scan
from banner import show_banner

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TimeRemainingColumn
from rich.align import Align

import time
import sys


def parse_status_filter(user_input: str):
    if not user_input.strip():
        return None

    codes = set()
    for code in user_input.split(","):
        code = code.strip()
        if code.isdigit():
            codes.add(int(code))
    return codes if codes else None


def color_status(status: int | None) -> str:
    if status is None:
        return "[red]No Response[/red]"
    if 200 <= status < 300:
        return f"[green]{status}[/green]"
    if 300 <= status < 400:
        return f"[cyan]{status}[/cyan]"
    if 400 <= status < 500:
        return f"[yellow]{status}[/yellow]"
    if 500 <= status:
        return f"[red]{status}[/red]"
    return str(status)


def save_results(domain, results):
    filename = f"{domain}_subdomains.txt"
    with open(filename, "w") as f:
        f.write("\n".join(results))
    return filename


def main():
    console = Console()
    console.clear()

    show_banner()

    domain = input("\n❄ Enter Target Domain: ").strip()

    status_input = input(
        "Enter Status Codes to Display (e.g. 200,403) or press Enter for all: "
    )
    status_filter = parse_status_filter(status_input)

    wordlist = "wordlists/common.txt"
    threads = 30

    with open(wordlist, "r") as f:
        total_words = sum(1 for _ in f)

    table = Table(title=f"❄ SubZero Scanner — {domain}")
    table.add_column("Subdomain", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")

    displayed_count = 0
    saved_results = []
    start_time = time.time()

    progress = Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeRemainingColumn(),
    )

    task = progress.add_task("[bright_blue]Scanning...", total=total_words)

    try:
        with Live(refresh_per_second=8, console=console):
            with progress:
                for result in scan(domain, wordlist, threads=threads):
                    sub, status = result
                    progress.update(task, advance=1)

                
                    if status_filter and status not in status_filter:
                        continue

                    displayed_count += 1

                    table.add_row(sub, color_status(status))
                    saved_results.append(f"{sub} - {status}")

                    elapsed = round(time.time() - start_time, 2)
                    speed = round(progress.tasks[0].completed / elapsed, 2) if elapsed > 0 else 0

                    stats_panel = Panel(
                        f"[bold yellow]Target:[/bold yellow] {domain}\n"
                        f"[bold green]Displayed:[/bold green] {displayed_count}\n"
                        f"[bold cyan]Threads:[/bold cyan] {threads}\n"
                        f"[bold magenta]Speed:[/bold magenta] {speed} req/sec\n"
                        f"[bold white]Filter:[/bold white] {status_filter if status_filter else 'All'}",
                        title="[bold white]❄ Scan Stats ❄[/bold white]",
                        border_style="bright_blue"
                    )

                    console.clear()
                    show_banner()
                    console.print(Align.center(stats_panel))
                    console.print(progress)
                    console.print(table)

    except KeyboardInterrupt:
        console.print("\n[bold red]⚠ Scan interrupted by user![/bold red]")

    finally:
        if saved_results:
            filename = save_results(domain, saved_results)
            console.print(f"\n[bold green]✔ Results saved to {filename}[/bold green]")
        else:
            console.print("\n[bold yellow]No results to save.[/bold yellow]")

        console.print(f"[bold cyan]Total Displayed:[/bold cyan] {displayed_count}")
        console.print("[bold green]Exiting SubZero... ❄[/bold green]")
        sys.exit()


if __name__ == "__main__":
    main()