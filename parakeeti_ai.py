"""
Parakeeti AI — Senior Network Engineer AI Assistant
Powered by Claude (Anthropic API), integrated into the Networking Jobs system.

Parakeeti AI acts as a seasoned Senior Network Engineer with 15+ years of experience,
helping you with job analysis, interview preparation, resume optimization, and
technical networking questions.
"""

import os
import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.rule import Rule
from rich import box

console = Console()

PARAKEETI_SYSTEM_PROMPT = """You are Parakeeti AI — a Senior Network Engineer AI Assistant with 15+ years of hands-on experience in enterprise networking, data centers, and network security. You are integrated into a job search platform designed for network engineering professionals.

Your expertise includes:
- Routing protocols: BGP, OSPF, EIGRP, IS-IS, MPLS, Segment Routing
- Switching: VLANs, VxLAN, STP/RSTP, 802.1Q, 802.1X, port-channels
- Network security: Firewalls (Palo Alto, Fortinet, Check Point), ACLs, IPsec VPN, DMVPN, SD-WAN, Zero Trust
- Vendors: Cisco (IOS, IOS-XE, NX-OS, ASA), Juniper (JunOS, SRX, MX), Arista EOS, F5, Meraki
- Cloud networking: AWS VPC, Transit Gateway, Direct Connect; Azure VNet, ExpressRoute; GCP networking
- Automation: Python, Ansible, Terraform, NETCONF/YANG, RESTCONF, Git
- Monitoring & management: SolarWinds, NetBox, Grafana, Prometheus, SNMP, NetFlow, Wireshark
- Certifications: CCIE, CCNP, CCNA, PCNSE, JNCIE, NSE, CISSP
- Data center networking: spine-leaf, ECMP, BGP EVPN/VxLAN fabrics
- High availability: HSRP, VRRP, BFD, link aggregation, redundant designs

As Parakeeti AI, you:
1. Analyze job descriptions and highlight key requirements, salary insights, and fit gaps
2. Give targeted interview prep advice — including common technical questions for the role
3. Review and optimize resumes for networking engineering roles
4. Explain complex networking concepts clearly with real-world examples
5. Advise on certifications and career progression
6. Help craft cover letters and outreach messages for specific companies
7. Identify red flags or green flags in job postings

Always be practical, direct, and grounded in real-world networking experience. When discussing technical topics, use accurate terminology. When analyzing jobs, be honest about salary expectations, workload signals, and company reputation when relevant.
"""


class ParakeetiAI:
    """Multi-turn AI assistant acting as a Senior Network Engineer."""

    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY environment variable is not set.\n"
                "Get your API key at https://console.anthropic.com/"
            )
        self.client = anthropic.Anthropic(api_key=api_key)
        self.conversation: list[dict] = []

    def reset(self):
        """Clear conversation history to start a new session."""
        self.conversation = []

    def _stream_response(self, user_message: str) -> str:
        """Send a message, stream the response, and return the full text."""
        self.conversation.append({"role": "user", "content": user_message})

        full_response = ""
        console.print()

        try:
            with self.client.messages.stream(
                model="claude-opus-4-6",
                max_tokens=4096,
                system=PARAKEETI_SYSTEM_PROMPT,
                thinking={"type": "adaptive"},
                messages=self.conversation,
            ) as stream:
                for text in stream.text_stream:
                    print(text, end="", flush=True)
                    full_response += text

            final = stream.get_final_message()

        except anthropic.AuthenticationError:
            console.print("\n[red]Authentication failed. Check your ANTHROPIC_API_KEY.[/red]")
            self.conversation.pop()
            return ""
        except anthropic.RateLimitError:
            console.print("\n[yellow]Rate limit hit. Please wait a moment and try again.[/yellow]")
            self.conversation.pop()
            return ""
        except anthropic.APIConnectionError:
            console.print("\n[red]Network error. Check your internet connection.[/red]")
            self.conversation.pop()
            return ""
        except anthropic.APIStatusError as e:
            console.print(f"\n[red]API error ({e.status_code}): {e.message}[/red]")
            self.conversation.pop()
            return ""

        print()  # newline after streaming
        self.conversation.append({"role": "assistant", "content": full_response})
        return full_response

    # ── Contextual helpers ────────────────────────────────────────────────────

    def analyze_job(self, job: dict) -> str:
        """Analyze a specific job from the database."""
        job_details = (
            f"**Job Title:** {job.get('title', 'N/A')}\n"
            f"**Company:** {job.get('company', 'N/A')}\n"
            f"**Location:** {job.get('location', 'N/A')}\n"
            f"**Salary:** {job.get('salary', 'Not listed')}\n"
            f"**Source:** {job.get('source', 'N/A')}\n"
            f"**Description:**\n{job.get('description', 'No description available.')}"
        )
        prompt = (
            f"Please analyze this job posting for me:\n\n{job_details}\n\n"
            "Tell me:\n"
            "1. Key technical skills required and which are must-haves vs nice-to-haves\n"
            "2. Seniority level signals (is this truly senior, or just labeled that way?)\n"
            "3. Salary assessment — is the listed range fair for the role and location?\n"
            "4. Red flags or green flags in this posting\n"
            "5. Top 3 technical interview topics I should prepare for\n"
            "6. How to tailor my networking resume for this specific role"
        )
        return self._stream_response(prompt)

    def interview_prep(self, job_title: str = "", company: str = "") -> str:
        """Generate targeted interview prep guidance."""
        context = f"for a **{job_title}** role" if job_title else "for a senior network engineer role"
        if company:
            context += f" at **{company}**"
        prompt = (
            f"Give me a comprehensive interview preparation guide {context}.\n\n"
            "Include:\n"
            "1. Top 10 technical questions likely to be asked (with brief answer guidance)\n"
            "2. Hands-on/scenario-based questions (e.g., 'troubleshoot this network issue')\n"
            "3. Behavioral/situational questions specific to networking roles\n"
            "4. Questions I should ask the interviewer to assess the team and environment\n"
            "5. Any vendor-specific or certification topics I should brush up on"
        )
        return self._stream_response(prompt)

    def resume_review(self, resume_text: str) -> str:
        """Review and optimize a resume for network engineering roles."""
        prompt = (
            "Please review my network engineering resume and give me actionable feedback:\n\n"
            f"```\n{resume_text[:4000]}\n```\n\n"
            "Focus on:\n"
            "1. Missing keywords/skills that appear frequently in senior networking job posts\n"
            "2. How to strengthen the technical skills section\n"
            "3. Metrics and accomplishments — what's missing, what could be quantified\n"
            "4. ATS (Applicant Tracking System) optimization tips\n"
            "5. Overall structure and formatting suggestions for networking roles"
        )
        return self._stream_response(prompt)


# ── Interactive Chat UI ───────────────────────────────────────────────────────

def _print_header():
    console.print(Panel.fit(
        "[bold cyan]PARAKEETI AI[/bold cyan] — [dim]Senior Network Engineer Assistant[/dim]\n"
        "[dim]Powered by Claude · Ask anything about networking jobs, interviews, or tech[/dim]",
        border_style="cyan",
    ))


def _print_help():
    console.print(Panel(
        "[bold]Quick Commands:[/bold]\n"
        "  [cyan]/analyze[/cyan]       Analyze a specific job from your database\n"
        "  [cyan]/interview[/cyan]     Get interview prep for a role/company\n"
        "  [cyan]/resume[/cyan]        Review your resume\n"
        "  [cyan]/new[/cyan]           Start a new conversation (clear history)\n"
        "  [cyan]/help[/cyan]          Show this help\n"
        "  [cyan]/back[/cyan] or [cyan]exit[/cyan]   Return to Command Center\n\n"
        "[dim]Or just type any networking question to chat with Parakeeti AI.[/dim]",
        border_style="dim",
        box=box.SIMPLE,
    ))


def _handle_analyze_command(ai: "ParakeetiAI"):
    """Let the user pick a job from the DB and analyze it."""
    try:
        import database as db
        jobs = db.get_jobs(limit=20)
        if not jobs:
            console.print("[yellow]No jobs in database yet. Run the scraper first.[/yellow]")
            return

        console.print("\n[bold]Recent jobs:[/bold]")
        for i, job in enumerate(jobs[:15], 1):
            console.print(f"  [{i}] {job['title'][:45]} — {job['company'][:25]}")

        choice = Prompt.ask("Pick job # to analyze", default="1")
        idx = int(choice) - 1
        if 0 <= idx < len(jobs):
            # Fetch description if missing
            job = jobs[idx]
            if not job.get("description"):
                try:
                    from scrapers import fetch_job_description
                    with console.status("[cyan]Fetching job description..."):
                        desc = fetch_job_description(job["url"])
                    if desc:
                        db.update_job_description(job["id"], desc)
                        job["description"] = desc
                except Exception:
                    pass
            console.print(Rule(f"[cyan]Analyzing: {job['title']} @ {job['company']}"))
            ai.analyze_job(job)
        else:
            console.print("[red]Invalid selection.[/red]")
    except (ValueError, ImportError) as e:
        console.print(f"[red]Error: {e}[/red]")


def _handle_interview_command(ai: "ParakeetiAI"):
    title = Prompt.ask("Job title (press Enter to skip)", default="Senior Network Engineer")
    company = Prompt.ask("Company name (press Enter to skip)", default="")
    console.print(Rule(f"[cyan]Interview Prep: {title}" + (f" @ {company}" if company else "")))
    ai.interview_prep(job_title=title, company=company)


def _handle_resume_command(ai: "ParakeetiAI"):
    """Review the configured resume."""
    try:
        from config import RESUME_PATH
        from resume_matcher import load_resume
        if not RESUME_PATH:
            console.print("[yellow]No RESUME_PATH set in config.py[/yellow]")
            return
        resume_text = load_resume(RESUME_PATH)
        if not resume_text:
            console.print(f"[red]Could not read resume from: {RESUME_PATH}[/red]")
            return
        console.print(Rule("[cyan]Resume Review"))
        ai.resume_review(resume_text)
    except ImportError as e:
        console.print(f"[red]Import error: {e}[/red]")


def run_chat(ai: "ParakeetiAI | None" = None):
    """
    Launch the interactive Parakeeti AI chat interface.
    Optionally accepts an existing ParakeetiAI instance to preserve conversation history.
    """
    try:
        if ai is None:
            ai = ParakeetiAI()
    except EnvironmentError as e:
        console.print(Panel(
            f"[red]{e}[/red]\n\n"
            "Set your API key:\n"
            "[dim]export ANTHROPIC_API_KEY='your-key-here'[/dim]\n\n"
            "Or add it to your shell profile (.bashrc / .zshrc).",
            title="[red]API Key Missing[/red]",
            border_style="red",
        ))
        Prompt.ask("\nPress Enter to go back")
        return

    _print_header()
    _print_help()

    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        if cmd in ("/back", "exit", "/exit", "quit", "/quit"):
            break
        elif cmd == "/help":
            _print_help()
        elif cmd == "/new":
            ai.reset()
            console.print("[green]Conversation cleared. Starting fresh.[/green]")
        elif cmd == "/analyze":
            _handle_analyze_command(ai)
        elif cmd == "/interview":
            _handle_interview_command(ai)
        elif cmd == "/resume":
            _handle_resume_command(ai)
        else:
            console.print(Rule("[dim]Parakeeti AI"))
            ai._stream_response(user_input)

    console.print("[dim]Returning to Command Center...[/dim]")


# ── Standalone entry point ────────────────────────────────────────────────────

if __name__ == "__main__":
    run_chat()
