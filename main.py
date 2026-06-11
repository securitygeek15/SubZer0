import argparse
import csv
import json
import time
import sys
from pathlib import Path

from scanner import scan, stop_event
from banner import get_banner
from resolver import check_wildcard_dns

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TimeRemainingColumn
from rich.align import Align
from rich.console import Group


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="SubZer0 - Terminal-based subdomain reconnaissance tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py -d example.com
  python main.py -d example.com -w wordlists/common.txt -t 50 -f 200,403
  python main.py -d example.com --https --json --csv
        """,
    )
    parser.add_argument("-d", "--domain", help="Target domain to scan")
    parser.add_argument(
        "-w",
        "--wordlist",
        default="wordlists/common.txt",
        help="Path to subdomain wordlist (default: wordlists/common.txt)",
    )
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=30,
        help="Number of concurrent threads (default: 30)",
    )
    parser.add_argument(
        "-f",
        "--filter",
        help="Comma-separated status codes to display (e.g. 200,403)",
    )
    parser.add_argument(
        "--https",
        action="store_true",
        help="Prefer HTTPS over HTTP for status checking",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Export results in JSON format",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Export results in CSV format",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file basename (without extension) -- defaults to <domain>_subdomains",
    )
    return parser.parse_args()


def parse_status_filter(user_input: str | None) -> set[int] | None:
    if not user_input or not user_input.strip():
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


def build_stats_panel(
    domain: str,
    displayed: int,
    threads: int,
    speed: float,
    status_filter: set[int] | None,
    wildcard_ip: str | None,
) -> Panel:
    wildcard_line = (
        "[bold red]⚠ Wildcard DNS Detected![/bold red]"
        if wildcard_ip
        else "[green]None[/green]"
    )
    return Panel(
        f"[bold yellow]Target:[/bold yellow] {domain}\n"
        f"[bold green]Displayed:[/bold green] {displayed}\n"
        f"[bold cyan]Threads:[/bold cyan] {threads}\n"
        f"[bold magenta]Speed:[/bold magenta] {speed:.2f} req/sec\n"
        f"[bold white]Filter:[/bold white] {', '.join(str(c) for c in sorted(status_filter)) if status_filter else 'All'}\n"
        f"[bold white]Wildcard:[/bold white] {wildcard_line}",
        title="[bold white]❄ Scan Stats ❄[/bold white]",
        border_style="bright_blue",
    )


def save_results_txt(domain: str, results: list[dict]) -> str:
    filename = f"{domain}_subdomains.txt"
    with open(filename, "w") as f:
        for r in results:
            status_str = str(r["status"]) if r["status"] is not None else "No Response"
            ip_str = r["ip"] or "N/A"
            f.write(f"{r['subdomain']} [{ip_str}] - {status_str}\n")
    return filename


def save_results_json(results: list[dict], path: str) -> str:
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    return path


def save_results_csv(results: list[dict], path: str) -> str:
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["subdomain", "ip", "status"])
        for r in results:
            writer.writerow([r["subdomain"], r["ip"] or "", r["status"] or ""])
    return path


def main():
    args = parse_args()
    console = Console()
    domain = args.domain
    wordlist_path = args.wordlist
    threads = args.threads
    prefer_https = args.https
    status_filter = parse_status_filter(args.filter)

    console.clear()
    banner = get_banner()
    console.print(banner)

    if not domain:
        domain = input("\n❄ Enter Target Domain: ").strip()
        while not domain:
            domain = input("❄ Domain cannot be empty. Enter Target Domain: ").strip()

    if args.filter is None:
        status_input = input(
            "Enter Status Codes to Display (e.g. 200,403) or press Enter for all: "
        )
        status_filter = parse_status_filter(status_input)

    wildcard_ip = check_wildcard_dns(domain)
    if wildcard_ip:
        console.print(
            f"[bold yellow]⚠ Wildcard DNS detected! Random subdomain resolved to {wildcard_ip}[/bold yellow]"
        )
        console.print(
            "[yellow]Results may include false positives. Consider using a wildcard-aware wordlist.[/yellow]"
        )

    wl_path = Path(wordlist_path)
    if not wl_path.exists():
        console.print(f"[bold red]✖ Wordlist not found: {wordlist_path}[/bold red]")
        sys.exit(1)

    with open(wordlist_path, "r") as f:
        total_words = sum(1 for _ in f)

    if total_words == 0:
        console.print("[bold red]✖ Wordlist is empty![/bold red]")
        sys.exit(1)

    table = Table(title=f"❄ SubZer0 Scanner — {domain}")
    table.add_column("Subdomain", style="cyan", no_wrap=True)
    table.add_column("IP Address", style="white", no_wrap=True)
    table.add_column("Status", justify="center")

    progress = Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeRemainingColumn(),
    )
    task = progress.add_task("[bright_blue]Scanning...", total=total_words)

    displayed_count = 0
    saved_results: list[dict] = []
    start_time = time.time()

    try:
        with Live(refresh_per_second=8, console=console) as live:
            for sub, status, ip in scan(domain, wordlist_path, threads=threads, prefer_https=prefer_https):
                progress.update(task, advance=1)

                if status_filter is not None and status not in status_filter:
                    continue

                displayed_count += 1
                table.add_row(sub, ip or "N/A", color_status(status))
                saved_results.append(
                    {"subdomain": sub, "ip": ip, "status": status}
                )

                elapsed = time.time() - start_time
                completed = progress.tasks[0].completed
                speed = completed / elapsed if elapsed > 0 else 0.0

                stats = build_stats_panel(
                    domain, displayed_count, threads, speed, status_filter, wildcard_ip
                )

                live.update(
                    Group(banner, Align.center(stats), progress, table),
                )

    except KeyboardInterrupt:
        stop_event.set()
        console.print("\n[bold red]⚠ Scan interrupted by user![/bold red]")

    finally:
        if saved_results:
            base = args.output or f"{domain}_subdomains"
            txt_path = save_results_txt(domain, saved_results)
            console.print(f"\n[bold green]✔ Results saved to {txt_path}[/bold green]")

            if args.json:
                json_path = save_results_json(saved_results, f"{base}.json")
                console.print(f"[bold green]✔ Results saved to {json_path}[/bold green]")

            if args.csv:
                csv_path = save_results_csv(saved_results, f"{base}.csv")
                console.print(f"[bold green]✔ Results saved to {csv_path}[/bold green]")
        else:
            console.print("\n[bold yellow]No results to save.[/bold yellow]")

        console.print(f"[bold cyan]Total Displayed:[/bold cyan] {displayed_count}")
        console.print("[bold green]Exiting SubZer0... ❄[/bold green]")
        sys.exit()


if __name__ == "__main__":
    main()
