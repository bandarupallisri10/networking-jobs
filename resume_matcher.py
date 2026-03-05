"""
Resume matcher — scores how well your resume matches a job description.
Uses keyword-based matching focused on networking/security skills.
No external AI API needed; runs fully offline.
"""
import re
from pathlib import Path

# Networking/security keywords with importance weights
KEYWORDS = {
    # Routing protocols
    "bgp": 3, "ospf": 3, "eigrp": 3, "rip": 1, "isis": 2, "is-is": 2,
    "mpls": 3, "segment routing": 3,
    # VPN / tunneling
    "vpn": 2, "ipsec": 3, "ssl vpn": 2, "gre": 2, "dmvpn": 3, "sdwan": 3, "sd-wan": 3,
    # Switching
    "vlan": 2, "vxlan": 3, "stp": 2, "rstp": 2, "spanning tree": 2,
    "802.1q": 2, "802.1x": 2, "dot1q": 2,
    # Security
    "firewall": 3, "acl": 2, "ids": 2, "ips": 2, "siem": 2,
    "zero trust": 3, "zero-trust": 3, "microsegmentation": 2,
    "nat": 1, "pat": 1, "dmz": 2,
    # Vendors
    "cisco": 3, "juniper": 3, "arista": 3, "palo alto": 3, "fortinet": 3,
    "checkpoint": 2, "f5": 2, "meraki": 2, "extreme": 1,
    "catalyst": 2, "nexus": 2, "asr": 2, "isr": 2, "srx": 2, "mx series": 2,
    # Cloud networking
    "aws": 2, "azure": 2, "gcp": 2, "vpc": 2, "transit gateway": 2,
    "direct connect": 2, "expressroute": 2, "cloud": 1,
    # Automation / tools
    "python": 3, "ansible": 3, "terraform": 2, "bash": 2, "powershell": 1,
    "netconf": 3, "yang": 3, "restconf": 2, "api": 1,
    "git": 1, "linux": 2, "wireshark": 2, "tcpdump": 2,
    "netbox": 2, "servicenow": 1, "grafana": 1, "prometheus": 1,
    # Certifications
    "ccna": 3, "ccnp": 3, "ccie": 3,
    "security+": 2, "cissp": 3, "ceh": 2, "network+": 2,
    "pcnse": 3, "nse": 2, "jncia": 2, "jncip": 3, "jncie": 3,
    # General networking
    "routing": 2, "switching": 2, "wan": 1, "lan": 1, "wlan": 1,
    "data center": 2, "dhcp": 1, "dns": 1, "snmp": 2, "netflow": 2,
    "qos": 2, "voip": 1, "sip": 1, "sdh": 1, "sonet": 1,
    "load balancer": 2, "load balancing": 2, "ha": 1, "high availability": 2,
    "troubleshoot": 1, "network monitoring": 2, "nms": 1,
    "infrastructure": 1, "network engineer": 2, "network security": 2,
}


def load_resume(path: str) -> str:
    """Load resume text from .txt or .pdf file."""
    p = Path(path)
    if not p.exists():
        return ""
    if p.suffix.lower() == ".pdf":
        try:
            import pdfplumber
            with pdfplumber.open(str(p)) as pdf:
                return " ".join(page.extract_text() or "" for page in pdf.pages)
        except ImportError:
            pass
        try:
            import PyPDF2
            with open(str(p), "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return " ".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            return "[PDF not readable — install pdfplumber: pip install pdfplumber]"
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def score_resume(resume_text: str, job_text: str) -> dict:
    """
    Score how well a resume matches a job description.
    Returns dict: score (0-100), matched keywords, missing keywords.
    """
    if not resume_text or not job_text:
        return {"score": 0, "matched": [], "missing": [], "total_kw": 0}

    resume_lower = resume_text.lower()
    job_lower = job_text.lower()

    # Find which keywords appear in the job description
    job_kw = {kw: w for kw, w in KEYWORDS.items() if kw in job_lower}

    if not job_kw:
        # Fallback: simple word overlap for unusual job descriptions
        job_words = set(re.findall(r'\b[a-z]{4,}\b', job_lower))
        resume_words = set(re.findall(r'\b[a-z]{4,}\b', resume_lower))
        overlap = job_words & resume_words
        score = min(100, int(len(overlap) / max(len(job_words), 1) * 200))
        return {"score": score, "matched": sorted(overlap)[:10], "missing": [], "total_kw": len(job_words)}

    matched, missing, matched_weight = [], [], 0
    total_weight = sum(job_kw.values())

    for kw, weight in sorted(job_kw.items(), key=lambda x: -x[1]):
        if kw in resume_lower:
            matched.append(kw)
            matched_weight += weight
        else:
            missing.append(kw)

    score = min(100, int(matched_weight / total_weight * 100)) if total_weight else 0

    return {
        "score": score,
        "matched": matched,
        "missing": missing[:12],   # top missing keywords to add to resume
        "total_kw": len(job_kw),
    }


def score_color(score: int) -> str:
    """Return rich color string for a score value."""
    if score >= 75:
        return "bold green"
    if score >= 50:
        return "yellow"
    if score >= 25:
        return "orange3"
    return "red"
