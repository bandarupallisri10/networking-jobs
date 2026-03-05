"""
Morning and Evening notification system for new networking job openings.
Sends desktop notifications and prints summary to terminal.
"""
import os
import sys
import subprocess
import platform
import logging
from datetime import datetime
from database import get_stats, get_jobs, log_notification

logger = logging.getLogger(__name__)


def send_desktop_notification(title: str, message: str, urgency: str = "normal"):
    """Send a desktop notification cross-platform."""
    system = platform.system()
    try:
        if system == "Linux":
            # Try notify-send (libnotify)
            subprocess.run(
                ["notify-send", "--urgency", urgency, "--icon", "dialog-information",
                 "--app-name", "NetworkingJobs", title, message],
                timeout=5, check=False
            )
        elif system == "Darwin":
            # macOS osascript
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", script], timeout=5, check=False)
        elif system == "Windows":
            # Windows toast via PowerShell
            ps_script = f"""
Add-Type -AssemblyName System.Windows.Forms
$notification = New-Object System.Windows.Forms.NotifyIcon
$notification.Icon = [System.Drawing.SystemIcons]::Information
$notification.BalloonTipTitle = "{title}"
$notification.BalloonTipText = "{message}"
$notification.Visible = $true
$notification.ShowBalloonTip(5000)
Start-Sleep -Seconds 6
$notification.Dispose()
"""
            subprocess.run(["powershell", "-Command", ps_script], timeout=10, check=False)
    except Exception as e:
        logger.warning(f"[Notifier] Desktop notification failed: {e}")

    # Always print to terminal as fallback
    _print_terminal_notification(title, message)


def _print_terminal_notification(title: str, message: str):
    """Print a styled notification banner in the terminal."""
    width = 70
    border = "=" * width
    print(f"\n\033[1;32m{border}\033[0m")
    print(f"\033[1;33m  {title}\033[0m")
    print(f"\033[0;37m  {message}\033[0m")
    print(f"\033[1;32m{border}\033[0m\n")


def build_notification_message(period: str) -> tuple[str, str]:
    """Build notification title and message with current job stats."""
    stats = get_stats()
    today_jobs = stats.get("today", 0)
    total_new = stats.get("new_jobs", 0)

    # Get latest 5 new jobs for preview
    recent = get_jobs(status="new", limit=5)
    preview_lines = []
    for j in recent:
        preview_lines.append(f"• {j['title']} @ {j['company']} ({j['source']})")

    emoji_map = {"morning": "☀️", "evening": "🌆"}
    emoji = emoji_map.get(period, "🔔")

    title = f"{emoji} Networking Jobs {period.capitalize()} Update"
    message = (
        f"Found {today_jobs} new job(s) today | {total_new} total pending\n"
        + "\n".join(preview_lines[:5])
        + f"\n\nRun 'python command_center.py' to view & apply"
    )
    return title, message


def send_morning_notification():
    """Send the 8 AM morning job update notification."""
    logger.info("[Notifier] Sending morning notification...")
    title, message = build_notification_message("morning")
    send_desktop_notification(title, message, urgency="normal")
    stats = get_stats()
    log_notification("morning", stats.get("today", 0), message)
    logger.info("[Notifier] Morning notification sent.")


def send_evening_notification():
    """Send the 6 PM evening job update notification."""
    logger.info("[Notifier] Sending evening notification...")
    title, message = build_notification_message("evening")
    send_desktop_notification(title, message, urgency="normal")
    stats = get_stats()
    log_notification("evening", stats.get("today", 0), message)
    logger.info("[Notifier] Evening notification sent.")


def send_new_jobs_alert(new_count: int, source: str = "All Sources"):
    """Alert when new jobs are found during a scrape run."""
    if new_count == 0:
        return
    title = f"🎯 {new_count} New Networking Jobs Found!"
    message = f"Source: {source}\nRun 'python command_center.py' to view & apply"
    send_desktop_notification(title, message, urgency="critical" if new_count > 10 else "normal")
