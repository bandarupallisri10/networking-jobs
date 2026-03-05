"""
Configuration for Networking Jobs Search System
"""

# Job titles to search across all portals and company career pages
JOB_TITLES = [
    "Network Engineer",
    "Senior Network Engineer",
    "Network Security Engineer",
    "Senior Network Security Engineer",
]

# Search location
LOCATION = "United States"

# Notification times (24-hour format)
MORNING_NOTIFICATION_TIME = "08:00"
EVENING_NOTIFICATION_TIME = "18:00"

# Database file
DB_FILE = "networking_jobs.db"

# Path to your resume file (.txt or .pdf)
# Example: RESUME_PATH = "C:/Users/YourName/Documents/resume.pdf"
RESUME_PATH = "C:/Users/itssr/OneDrive/Desktop/srikanth Bandarupalli_updated resume.docx"

# Jooble API key (free, register at https://jooble.org/api/about)
# Leave empty to skip Jooble
JOOBLE_API_KEY = ""

# USAJobs API key (free, register at https://developer.usajobs.gov/APIRequest/)
# Leave empty to use web fallback
USAJOBS_API_KEY = ""
USAJOBS_EMAIL = ""

# Max jobs to show per source
MAX_JOBS_PER_SOURCE = 50

# Request delay (seconds) between requests per session (parallel scrapers use separate sessions)
REQUEST_DELAY = 0.5

# User agent rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
]

# ============================================================
# JOB PORTALS
# ============================================================
JOB_PORTALS = {
    "LinkedIn": {
        "url": "https://www.linkedin.com/jobs/search/",
        "enabled": True,
        "description": "World's largest professional network",
    },
    "Indeed": {
        "url": "https://www.indeed.com/jobs",
        "enabled": True,
        "description": "Leading job aggregator",
    },
    "Dice": {
        "url": "https://www.dice.com/jobs",
        "enabled": True,
        "description": "Tech-focused job board",
    },
    "Glassdoor": {
        "url": "https://www.glassdoor.com/Job/jobs.htm",
        "enabled": True,
        "description": "Jobs with company reviews",
    },
    "ZipRecruiter": {
        "url": "https://www.ziprecruiter.com/jobs-search",
        "enabled": True,
        "description": "AI-powered job marketplace",
    },
    "Monster": {
        "url": "https://www.monster.com/jobs/search/",
        "enabled": True,
        "description": "Global employment website",
    },
    "CareerBuilder": {
        "url": "https://www.careerbuilder.com/jobs",
        "enabled": True,
        "description": "Large job board with resume tools",
    },
    "SimplyHired": {
        "url": "https://www.simplyhired.com/search",
        "enabled": True,
        "description": "Job search engine",
    },
    "CyberCoders": {
        "url": "https://www.cybercoders.com/jobs/",
        "enabled": True,
        "description": "Specialized tech/engineering recruiter",
    },
    "USAJobs": {
        "url": "https://www.usajobs.gov/search/results/",
        "enabled": True,
        "description": "US Federal Government jobs",
    },
    "Hired": {
        "url": "https://hired.com/jobs",
        "enabled": True,
        "description": "Tech talent marketplace",
    },
    "Ladders": {
        "url": "https://www.theladders.com/jobs/search-jobs",
        "enabled": True,
        "description": "High-salary job board ($100k+)",
    },
    "ClearanceJobs": {
        "url": "https://www.clearancejobs.com/jobs",
        "enabled": True,
        "description": "Security clearance required jobs",
    },
    "Jooble": {
        "url": "https://us.jooble.org/",
        "enabled": True,
        "description": "International job search engine",
    },
    "Snagajob": {
        "url": "https://www.snagajob.com/jobs",
        "enabled": True,
        "description": "Flexible and full-time jobs",
    },
    "Networking Jobs": {
        "url": "https://www.networkingjobs.com/",
        "enabled": True,
        "description": "Specialized networking jobs",
    },
    "TechFetch": {
        "url": "https://www.techfetch.com/job/",
        "enabled": True,
        "description": "IT and tech jobs",
    },
    "HireNetworks": {
        "url": "https://www.hirenetworks.com/job-search/",
        "enabled": True,
        "description": "IT networking specialist recruiter",
    },
    "Nexxt": {
        "url": "https://www.nexxt.com/jobs/",
        "enabled": True,
        "description": "Job search and career network",
    },
    "Handshake": {
        "url": "https://app.joinhandshake.com/jobs",
        "enabled": True,
        "description": "Early career jobs platform",
    },
}

# ============================================================
# US STOCK LISTED COMPANIES - CAREER PAGES
# Organized by sector
# ============================================================
US_COMPANIES = {
    # ---- NETWORKING / TELECOM EQUIPMENT ----
    "Cisco Systems": {
        "careers_url": "https://jobs.cisco.com/jobs/SearchJobs/",
        "ticker": "CSCO",
        "sector": "Networking Equipment",
    },
    "Juniper Networks": {
        "careers_url": "https://boards.greenhouse.io/juniper",
        "ticker": "JNPR",
        "sector": "Networking Equipment",
    },
    "Arista Networks": {
        "careers_url": "https://www.arista.com/en/careers",
        "ticker": "ANET",
        "sector": "Networking Equipment",
    },
    "F5 Networks": {
        "careers_url": "https://www.f5.com/company/careers",
        "ticker": "FFIV",
        "sector": "Networking Equipment",
    },
    "Calix": {
        "careers_url": "https://www.calix.com/company/careers.html",
        "ticker": "CALX",
        "sector": "Networking Equipment",
    },
    "Ciena": {
        "careers_url": "https://careers.ciena.com/",
        "ticker": "CIEN",
        "sector": "Networking Equipment",
    },
    "Infinera": {
        "careers_url": "https://careers.infinera.com/",
        "ticker": "INFN",
        "sector": "Networking Equipment",
    },
    "Viavi Solutions": {
        "careers_url": "https://careers.viavisolutions.com/",
        "ticker": "VIAV",
        "sector": "Networking Equipment",
    },
    "NetScout Systems": {
        "careers_url": "https://www.netscout.com/company/careers",
        "ticker": "NTCT",
        "sector": "Networking Equipment",
    },
    "Ribbon Communications": {
        "careers_url": "https://ribboncommunications.com/company/careers",
        "ticker": "RBBN",
        "sector": "Networking Equipment",
    },
    "Extreme Networks": {
        "careers_url": "https://www.extremenetworks.com/company/careers/",
        "ticker": "EXTR",
        "sector": "Networking Equipment",
    },
    "CommScope": {
        "careers_url": "https://www.commscope.com/careers/",
        "ticker": "COMM",
        "sector": "Networking Equipment",
    },
    "Cambium Networks": {
        "careers_url": "https://www.cambiumnetworks.com/company/careers/",
        "ticker": "CMBM",
        "sector": "Networking Equipment",
    },

    # ---- CYBERSECURITY ----
    "Palo Alto Networks": {
        "careers_url": "https://jobs.paloaltonetworks.com/en/",
        "ticker": "PANW",
        "sector": "Cybersecurity",
    },
    "Fortinet": {
        "careers_url": "https://www.fortinet.com/corporate/careers",
        "ticker": "FTNT",
        "sector": "Cybersecurity",
    },
    "CrowdStrike": {
        "careers_url": "https://careers.crowdstrike.com/",
        "ticker": "CRWD",
        "sector": "Cybersecurity",
    },
    "Zscaler": {
        "careers_url": "https://www.zscaler.com/careers",
        "ticker": "ZS",
        "sector": "Cybersecurity",
    },
    "Cloudflare": {
        "careers_url": "https://www.cloudflare.com/careers/jobs/",
        "ticker": "NET",
        "sector": "Cybersecurity",
    },
    "Qualys": {
        "careers_url": "https://www.qualys.com/company/careers/",
        "ticker": "QLYS",
        "sector": "Cybersecurity",
    },
    "Tenable": {
        "careers_url": "https://careers.tenable.com/",
        "ticker": "TENB",
        "sector": "Cybersecurity",
    },
    "SentinelOne": {
        "careers_url": "https://www.sentinelone.com/jobs/",
        "ticker": "S",
        "sector": "Cybersecurity",
    },
    "Check Point Software": {
        "careers_url": "https://careers.checkpoint.com/",
        "ticker": "CHKP",
        "sector": "Cybersecurity",
    },
    "Varonis Systems": {
        "careers_url": "https://info.varonis.com/careers",
        "ticker": "VRNS",
        "sector": "Cybersecurity",
    },
    "Rapid7": {
        "careers_url": "https://www.rapid7.com/company/careers/",
        "ticker": "RPD",
        "sector": "Cybersecurity",
    },
    "Sailpoint Technologies": {
        "careers_url": "https://www.sailpoint.com/company/careers/",
        "ticker": "SAIL",
        "sector": "Cybersecurity",
    },
    "Okta": {
        "careers_url": "https://www.okta.com/company/careers/",
        "ticker": "OKTA",
        "sector": "Cybersecurity",
    },
    "Cyberark Software": {
        "careers_url": "https://www.cyberark.com/careers/",
        "ticker": "CYBR",
        "sector": "Cybersecurity",
    },
    "Proofpoint": {
        "careers_url": "https://www.proofpoint.com/us/company/careers",
        "ticker": "PFPT",
        "sector": "Cybersecurity",
    },
    "Ping Identity": {
        "careers_url": "https://www.pingidentity.com/en/company/careers.html",
        "ticker": "PING",
        "sector": "Cybersecurity",
    },
    "Telos Corporation": {
        "careers_url": "https://www.telos.com/company/careers/",
        "ticker": "TLS",
        "sector": "Cybersecurity",
    },

    # ---- CLOUD / HYPERSCALERS ----
    "Amazon Web Services": {
        "careers_url": "https://www.amazon.jobs/en/",
        "ticker": "AMZN",
        "sector": "Cloud",
    },
    "Microsoft": {
        "careers_url": "https://careers.microsoft.com/us/en/search-results",
        "ticker": "MSFT",
        "sector": "Cloud",
    },
    "Google / Alphabet": {
        "careers_url": "https://careers.google.com/jobs/results/",
        "ticker": "GOOGL",
        "sector": "Cloud",
    },
    "Meta Platforms": {
        "careers_url": "https://www.metacareers.com/jobs/",
        "ticker": "META",
        "sector": "Cloud",
    },
    "Oracle": {
        "careers_url": "https://careers.oracle.com/jobs/",
        "ticker": "ORCL",
        "sector": "Cloud",
    },
    "Salesforce": {
        "careers_url": "https://careers.salesforce.com/en/jobs/",
        "ticker": "CRM",
        "sector": "Cloud",
    },
    "ServiceNow": {
        "careers_url": "https://careers.servicenow.com/jobs/",
        "ticker": "NOW",
        "sector": "Cloud",
    },
    "Snowflake": {
        "careers_url": "https://careers.snowflake.com/us/en",
        "ticker": "SNOW",
        "sector": "Cloud",
    },
    "VMware": {
        "careers_url": "https://careers.vmware.com/main/jobs",
        "ticker": "VMW",
        "sector": "Cloud",
    },
    "Nutanix": {
        "careers_url": "https://jobs.jobvite.com/nutanix/",
        "ticker": "NTNX",
        "sector": "Cloud",
    },

    # ---- TELECOM / ISP ----
    "AT&T": {
        "careers_url": "https://www.att.jobs/search-jobs",
        "ticker": "T",
        "sector": "Telecom",
    },
    "Verizon": {
        "careers_url": "https://mycareer.verizon.com/jobs/",
        "ticker": "VZ",
        "sector": "Telecom",
    },
    "T-Mobile": {
        "careers_url": "https://careers.t-mobile.com/job-search-results/",
        "ticker": "TMUS",
        "sector": "Telecom",
    },
    "Comcast": {
        "careers_url": "https://jobs.comcast.com/search-jobs",
        "ticker": "CMCSA",
        "sector": "Telecom",
    },
    "Charter Communications": {
        "careers_url": "https://jobs.spectrum.com/search-jobs",
        "ticker": "CHTR",
        "sector": "Telecom",
    },
    "Lumen Technologies": {
        "careers_url": "https://jobs.lumen.com/global/en/search-results",
        "ticker": "LUMN",
        "sector": "Telecom",
    },
    "Dish Network": {
        "careers_url": "https://careers.dish.com/jobs/",
        "ticker": "DISH",
        "sector": "Telecom",
    },

    # ---- HARDWARE / SEMICONDUCTORS ----
    "Intel": {
        "careers_url": "https://jobs.intel.com/en/search#",
        "ticker": "INTC",
        "sector": "Hardware",
    },
    "NVIDIA": {
        "careers_url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite",
        "ticker": "NVDA",
        "sector": "Hardware",
    },
    "Broadcom": {
        "careers_url": "https://careers.broadcom.com/jobs/",
        "ticker": "AVGO",
        "sector": "Hardware",
    },
    "Qualcomm": {
        "careers_url": "https://careers.qualcomm.com/careers",
        "ticker": "QCOM",
        "sector": "Hardware",
    },
    "Marvell Technology": {
        "careers_url": "https://marvell.wd1.myworkdayjobs.com/MarvellCareers",
        "ticker": "MRVL",
        "sector": "Hardware",
    },
    "Dell Technologies": {
        "careers_url": "https://jobs.dell.com/search-jobs",
        "ticker": "DELL",
        "sector": "Hardware",
    },
    "HPE (Hewlett Packard Enterprise)": {
        "careers_url": "https://careers.hpe.com/us/en/search-results",
        "ticker": "HPE",
        "sector": "Hardware",
    },
    "NetApp": {
        "careers_url": "https://careers.netapp.com/jobs/",
        "ticker": "NTAP",
        "sector": "Hardware",
    },
    "Pure Storage": {
        "careers_url": "https://www.purestorage.com/company/careers.html",
        "ticker": "PSTG",
        "sector": "Hardware",
    },

    # ---- IT SERVICES / MANAGED SERVICES ----
    "IBM": {
        "careers_url": "https://www.ibm.com/employment/",
        "ticker": "IBM",
        "sector": "IT Services",
    },
    "Accenture": {
        "careers_url": "https://www.accenture.com/us-en/careers",
        "ticker": "ACN",
        "sector": "IT Services",
    },
    "Cognizant": {
        "careers_url": "https://careers.cognizant.com/us/en",
        "ticker": "CTSH",
        "sector": "IT Services",
    },
    "Infosys": {
        "careers_url": "https://career.infosys.com/",
        "ticker": "INFY",
        "sector": "IT Services",
    },
    "Wipro": {
        "careers_url": "https://careers.wipro.com/",
        "ticker": "WIT",
        "sector": "IT Services",
    },
    "HCL Technologies": {
        "careers_url": "https://www.hcltech.com/careers",
        "ticker": "HCLTECH",
        "sector": "IT Services",
    },
    "Leidos": {
        "careers_url": "https://careers.leidos.com/jobs",
        "ticker": "LDOS",
        "sector": "IT Services",
    },
    "SAIC": {
        "careers_url": "https://jobs.saic.com/jobs",
        "ticker": "SAIC",
        "sector": "IT Services",
    },
    "Booz Allen Hamilton": {
        "careers_url": "https://careers.boozallen.com/jobs",
        "ticker": "BAH",
        "sector": "IT Services",
    },
    "DXC Technology": {
        "careers_url": "https://careers.dxc.com/global/en/search-results",
        "ticker": "DXC",
        "sector": "IT Services",
    },
    "ManTech International": {
        "careers_url": "https://www.mantech.com/careers/find-jobs",
        "ticker": "MANT",
        "sector": "IT Services",
    },
    "CACI International": {
        "careers_url": "https://careers.caci.com/global/en",
        "ticker": "CACI",
        "sector": "IT Services",
    },

    # ---- NETWORK MONITORING / MANAGEMENT ----
    "SolarWinds": {
        "careers_url": "https://www.solarwinds.com/company/careers",
        "ticker": "SWI",
        "sector": "Network Management",
    },
    "LogicMonitor": {
        "careers_url": "https://www.logicmonitor.com/jobs",
        "ticker": "Private",
        "sector": "Network Management",
    },

    # ---- FINANCIAL SERVICES (large IT infrastructure teams) ----
    "JPMorgan Chase": {
        "careers_url": "https://jobs.jpmorganchase.com/",
        "ticker": "JPM",
        "sector": "Financial Services",
    },
    "Bank of America": {
        "careers_url": "https://careers.bankofamerica.com/en-us/jobs",
        "ticker": "BAC",
        "sector": "Financial Services",
    },
    "Goldman Sachs": {
        "careers_url": "https://www.goldmansachs.com/careers/",
        "ticker": "GS",
        "sector": "Financial Services",
    },
    "Citigroup": {
        "careers_url": "https://jobs.citi.com/",
        "ticker": "C",
        "sector": "Financial Services",
    },
    "Wells Fargo": {
        "careers_url": "https://www.wellsfargojobs.com/en/",
        "ticker": "WFC",
        "sector": "Financial Services",
    },
    "Morgan Stanley": {
        "careers_url": "https://morganstanley.tal.net/vx/lang-en-GB/mobile-0/brand-2/xf-3786f31f41a7/candidate/jobboard/vacancy/2/adv/",
        "ticker": "MS",
        "sector": "Financial Services",
    },

    # ---- HEALTHCARE IT ----
    "UnitedHealth Group": {
        "careers_url": "https://careers.unitedhealthgroup.com/",
        "ticker": "UNH",
        "sector": "Healthcare IT",
    },
    "Optum (UHG)": {
        "careers_url": "https://careers.optum.com/us/en/search-results",
        "ticker": "UNH",
        "sector": "Healthcare IT",
    },

    # ---- AEROSPACE / DEFENSE ----
    "Raytheon Technologies": {
        "careers_url": "https://careers.rtx.com/global/en/",
        "ticker": "RTX",
        "sector": "Defense",
    },
    "Northrop Grumman": {
        "careers_url": "https://www.northropgrumman.com/jobs/",
        "ticker": "NOC",
        "sector": "Defense",
    },
    "Lockheed Martin": {
        "careers_url": "https://www.lockheedmartinjobs.com/search-jobs",
        "ticker": "LMT",
        "sector": "Defense",
    },
    "General Dynamics": {
        "careers_url": "https://www.gd.com/careers",
        "ticker": "GD",
        "sector": "Defense",
    },
    "L3Harris Technologies": {
        "careers_url": "https://careers.l3harris.com/jobs",
        "ticker": "LHX",
        "sector": "Defense",
    },
}
