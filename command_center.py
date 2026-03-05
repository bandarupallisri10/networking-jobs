"""
Networking Jobs Command Center
Interactive terminal UI to view, filter, and directly apply to jobs.
"""
import os
import sys
import subprocess
import webbrowser
import platform
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.text import Text
from rich.columns import Columns
from rich import box
from rich.live import Live
import database as db

console = Console()


# ── helpers ─────────────────────────────────────────────────────────────────

def open_url(url: str):
    """Open a URL in the default browser."""
    try:
        if platform.system() == "Linux":
            subprocess.run(["xdg-open", url], check=False)
        elif platform.system() == "Darwin":
            subprocess.run(["open", url], check=False)
        else:
            webbrowser.open(url)
        console.print(f"[green]Opened browser:[/green] {url}")
    except Exception as e:
        console.print(f"[red]Could not open browser:[/red] {e}")
        console.print(f"[yellow]Please visit:[/yellow] {url}")


def clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")


# ── dashboard ────────────────────────────────────────────────────────────────

def show_dashboard():
    clear_screen()
    stats = db.get_stats()
    sources = db.get_sources_summary()

    console.print(Panel.fit(
        "[bold cyan]NETWORKING JOBS COMMAND CENTER[/bold cyan]\n"
        "[dim]Network Engineer | Sr. Network Engineer | Network Security Engineer | Sr. Network Security Engineer[/dim]",
        border_style="cyan",
    ))

    # Stats row
    stat_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    stat_table.add_column("Label", style="dim")
    stat_table.add_column("Value", style="bold")
    stat_table.add_row("Total Jobs", str(stats.get("total", 0)))
    stat_table.add_row("New (Unread)", f"[green]{stats.get('new_jobs', 0)}[/green]")
    stat_table.add_row("Applied", f"[blue]{stats.get('applied', 0)}[/blue]")
    stat_table.add_row("Saved", f"[yellow]{stats.get('saved', 0)}[/yellow]")
    stat_table.add_row("Rejected", f"[red]{stats.get('rejected', 0)}[/red]")
    stat_table.add_row("Found Today", f"[cyan]{stats.get('today', 0)}[/cyan]")

    src_table = Table(show_header=True, box=box.SIMPLE, padding=(0, 1))
    src_table.add_column("Source", style="bold")
    src_table.add_column("Count", justify="right")
    for s in sources[:10]:
        src_table.add_row(s["source"][:35], str(s["count"]))

    console.print(Columns([stat_table, src_table]))


def show_menu():
    console.print("\n[bold]MAIN MENU[/bold]")
    console.print("  [1] View New Jobs")
    console.print("  [2] View All Jobs")
    console.print("  [3] Search Jobs")
    console.print("  [4] View Saved Jobs")
    console.print("  [5] View Applied Jobs")
    console.print("  [6] Run Job Scraper Now")
    console.print("  [7] View Jobs by Source")
    console.print("  [8] View Jobs by Company Sector")
    console.print("  [9] Notification Settings")
    console.print("  [0] Exit")
    return Prompt.ask("\nSelect option", choices=["0","1","2","3","4","5","6","7","8","9"])


# ── job list view ─────────────────────────────────────────────────────────────

def display_jobs(jobs: list, title: str = "Jobs"):
    if not jobs:
        console.print("[yellow]No jobs found.[/yellow]")
        return

    table = Table(
        title=f"{title} ({len(jobs)} listings)",
        box=box.ROUNDED,
        show_lines=False,
        highlight=True,
    )
    table.add_column("#", style="dim", width=4, no_wrap=True)
    table.add_column("Title", style="bold white", min_width=30)
    table.add_column("Company", style="cyan", min_width=20)
    table.add_column("Location", style="green", min_width=15)
    table.add_column("Salary", style="yellow", min_width=12)
    table.add_column("Source", style="magenta", min_width=12)
    table.add_column("Status", min_width=8)
    table.add_column("Date", style="dim", min_width=10)

    status_colors = {
        "new": "[green]NEW[/green]",
        "saved": "[yellow]SAVED[/yellow]",
        "applied": "[blue]APPLIED[/blue]",
        "rejected": "[red]REJECTED[/red]",
        "interviewing": "[cyan]INTERVIEW[/cyan]",
    }

    for i, job in enumerate(jobs, 1):
        status_display = status_colors.get(job.get("status", "new"), job.get("status", "new").upper())
        found = job.get("found_date", "")[:10] if job.get("found_date") else ""
        table.add_row(
            str(i),
            job.get("title", "")[:50],
            job.get("company", "")[:25],
            job.get("location", "")[:20],
            job.get("salary", "Not listed")[:15],
            job.get("source", "")[:15],
            status_display,
            found,
        )

    console.print(table)


def job_detail_menu(jobs: list):
    """Show jobs and let user pick one to interact with."""
    while True:
        try:
            choice = Prompt.ask(
                "\nEnter job # to manage (or [bold]b[/bold] to go back)",
                default="b"
            )
            if choice.lower() == "b":
                break
            idx = int(choice) - 1
            if 0 <= idx < len(jobs):
                manage_job(jobs[idx])
            else:
                console.print("[red]Invalid number.[/red]")
        except (ValueError, KeyboardInterrupt):
            break


def manage_job(job: dict):
    """Show detail panel for a single job with action options."""
    console.print(Panel(
        f"[bold]{job['title']}[/bold]\n"
        f"Company:  [cyan]{job['company']}[/cyan]\n"
        f"Location: [green]{job['location']}[/green]\n"
        f"Salary:   [yellow]{job.get('salary', 'Not listed')}[/yellow]\n"
        f"Source:   [magenta]{job['source']}[/magenta]\n"
        f"Status:   {job.get('status','new').upper()}\n"
        f"Posted:   {job.get('posted_date', 'Unknown')}\n"
        f"Found:    {job.get('found_date','')[:19]}\n\n"
        f"URL: [link={job['url']}]{job['url'][:80]}[/link]",
        title="Job Detail",
        border_style="cyan",
    ))

    console.print("\n[bold]Actions:[/bold]")
    console.print("  [A] Apply Now (opens application page)")
    console.print("  [S] Save for later")
    console.print("  [M] Mark as Applied")
    console.print("  [R] Reject / Not interested")
    console.print("  [N] Add Notes")
    console.print("  [B] Back")

    action = Prompt.ask("Action", choices=["a","s","m","r","n","b","A","S","M","R","N","B"]).lower()

    if action == "a":
        _apply_now(job)
    elif action == "s":
        db.update_job_status(job["id"], "saved")
        console.print("[yellow]Job saved for later.[/yellow]")
    elif action == "m":
        db.update_job_status(job["id"], "applied")
        console.print("[blue]Marked as Applied![/blue]")
    elif action == "r":
        db.update_job_status(job["id"], "rejected")
        console.print("[red]Marked as rejected.[/red]")
    elif action == "n":
        notes = Prompt.ask("Enter notes")
        db.update_job_status(job["id"], job.get("status", "new"), notes=notes)
        console.print("[green]Notes saved.[/green]")


def _apply_now(job: dict):
    """Direct Apply: opens the job application URL in browser."""
    console.print(Panel(
        f"[bold green]DIRECT APPLY[/bold green]\n\n"
        f"Job:     [bold]{job['title']}[/bold]\n"
        f"Company: [cyan]{job['company']}[/cyan]\n"
        f"Source:  [magenta]{job['source']}[/magenta]\n\n"
        f"Opening application page...\n"
        f"[dim]{job['url']}[/dim]",
        border_style="green",
    ))
    open_url(job["url"])
    if Confirm.ask("Did you submit your application?"):
        notes = Prompt.ask("Any notes about this application?", default="")
        db.update_job_status(job["id"], "applied", notes=notes)
        console.print("[bold blue]Application tracked! Good luck![/bold blue]")


# ── scraper runner ─────────────────────────────────────────────────────────────

def run_scraper_now():
    """Run the full job scraping job from the command center."""
    from scrapers import PORTAL_SCRAPERS, scrape_all_portals, scrape_all_companies
    from config import JOB_TITLES, US_COMPANIES
    import threading

    console.print(Panel("[bold cyan]Running Job Scraper...[/bold cyan]", border_style="cyan"))

    console.print("\n[bold]What to scrape?[/bold]")
    console.print("  [1] Job Portals only (faster)")
    console.print("  [2] Company Career Pages only")
    console.print("  [3] Both Portals + Company Pages (comprehensive)")
    scope = Prompt.ask("Select scope", choices=["1","2","3"])

    titles = JOB_TITLES
    total_new = 0
    lock = threading.Lock()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for title in titles:
            if scope in ["1", "3"]:
                task = progress.add_task(f"[cyan]Scraping portals for: {title} (parallel)...", total=None)
                found_counts = []

                def portal_cb(name, count, t=title):
                    found_counts.append(count)
                    progress.update(task, description=f"[cyan]Portals [{title}]: {len(found_counts)}/{len(PORTAL_SCRAPERS)} done, {sum(found_counts)} found")

                jobs = scrape_all_portals(title, progress_callback=portal_cb)
                with lock:
                    new_count = sum(db.upsert_job(j) for j in jobs)
                    total_new += new_count
                progress.update(task, description=f"[green]Portals [{title}]: {len(jobs)} found, {new_count} new")
                progress.remove_task(task)

            if scope in ["2", "3"]:
                task = progress.add_task(f"[magenta]Checking company pages for: {title} (parallel)...", total=None)
                done_companies = []

                def company_cb(name, count, t=title):
                    done_companies.append(name)
                    progress.update(task, description=f"[magenta]Companies [{title}]: {len(done_companies)}/{len(US_COMPANIES)} done")

                jobs = scrape_all_companies(title, US_COMPANIES, progress_callback=company_cb)
                with lock:
                    new_count = sum(db.upsert_job(j) for j in jobs)
                    total_new += new_count
                progress.update(task, description=f"[green]Companies [{title}]: {len(jobs)} found, {new_count} new")
                progress.remove_task(task)

    from notifier import send_new_jobs_alert
    send_new_jobs_alert(total_new)
    console.print(f"\n[bold green]Scraping complete! {total_new} new jobs added.[/bold green]")
    Prompt.ask("\nPress Enter to continue")


# ── main loop ─────────────────────────────────────────────────────────────────

def main():
    db.init_db()

    while True:
        show_dashboard()
        choice = show_menu()

        if choice == "0":
            console.print("[dim]Goodbye! Run the scheduler to keep jobs updated automatically.[/dim]")
            break

        elif choice == "1":
            jobs = db.get_jobs(status="new", limit=100)
            display_jobs(jobs, "New Jobs")
            job_detail_menu(jobs)

        elif choice == "2":
            jobs = db.get_jobs(limit=100)
            display_jobs(jobs, "All Jobs")
            job_detail_menu(jobs)

        elif choice == "3":
            query = Prompt.ask("Search keyword (title / company / location)")
            jobs = db.get_jobs(search=query, limit=100)
            display_jobs(jobs, f"Search: {query}")
            job_detail_menu(jobs)

        elif choice == "4":
            jobs = db.get_jobs(status="saved", limit=100)
            display_jobs(jobs, "Saved Jobs")
            job_detail_menu(jobs)

        elif choice == "5":
            jobs = db.get_jobs(status="applied", limit=100)
            display_jobs(jobs, "Applied Jobs")
            job_detail_menu(jobs)

        elif choice == "6":
            run_scraper_now()

        elif choice == "7":
            sources = db.get_sources_summary()
            console.print("\n[bold]Available Sources:[/bold]")
            for i, s in enumerate(sources, 1):
                console.print(f"  [{i}] {s['source']} ({s['count']} jobs)")
            src_name = Prompt.ask("\nEnter exact source name (or b to go back)", default="b")
            if src_name.lower() != "b":
                jobs = db.get_jobs(source=src_name, limit=100)
                display_jobs(jobs, f"Source: {src_name}")
                job_detail_menu(jobs)

        elif choice == "8":
            from config import US_COMPANIES
            sectors = {}
            for name, info in US_COMPANIES.items():
                sector = info.get("sector", "Other")
                sectors.setdefault(sector, []).append(name)

            console.print("\n[bold]Company Sectors:[/bold]")
            sector_list = list(sectors.keys())
            for i, s in enumerate(sector_list, 1):
                console.print(f"  [{i}] {s} ({len(sectors[s])} companies)")

            try:
                sec_choice = int(Prompt.ask("Select sector number")) - 1
                if 0 <= sec_choice < len(sector_list):
                    sector_name = sector_list[sec_choice]
                    companies = sectors[sector_name]
                    all_jobs = []
                    for c in companies:
                        jobs = db.get_jobs(source=f"Company: {c}", limit=50)
                        all_jobs.extend(jobs)
                    display_jobs(all_jobs, f"Sector: {sector_name}")
                    job_detail_menu(all_jobs)
            except (ValueError, KeyboardInterrupt):
                pass

        elif choice == "9":
            console.print(Panel(
                "[bold]Notification Schedule[/bold]\n\n"
                f"Morning: 08:00 AM daily\n"
                f"Evening: 06:00 PM daily\n\n"
                "[dim]To change times, edit MORNING_NOTIFICATION_TIME and\n"
                "EVENING_NOTIFICATION_TIME in config.py[/dim]\n\n"
                "Run [bold]python scheduler.py[/bold] to start the notification daemon.",
                title="Notification Settings",
                border_style="yellow",
            ))
            Prompt.ask("\nPress Enter to continue")

        # Pause before re-rendering dashboard
        if choice not in ["6", "9"]:
            try:
                Prompt.ask("\nPress Enter to return to main menu")
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[dim]Exited Command Center.[/dim]")
