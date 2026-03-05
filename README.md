# Networking Jobs Search System

A comprehensive job search system for **Network Engineer**, **Senior Network Engineer**, **Network Security Engineer**, and **Senior Network Security Engineer** roles across the United States.

## Features

- **12 Job Portals**: Indeed, LinkedIn, Dice, Glassdoor, ZipRecruiter, Monster, CareerBuilder, SimplyHired, CyberCoders, ClearanceJobs, USAJobs, Jooble
- **80+ US Stock-Listed Company Career Pages**: Cisco, Palo Alto Networks, CrowdStrike, AWS, Microsoft, Google, AT&T, Verizon, JPMorgan, and more
- **Morning & Evening Notifications** at 8:00 AM and 6:00 PM daily
- **Interactive Command Center** with Direct Apply, Save, Track applications
- **SQLite job database** with deduplication

## Quick Start

```bash
# 1. Setup (run once)
chmod +x setup.sh && ./setup.sh

# 2. Activate environment
source venv/bin/activate

# 3. Open Command Center (interactive UI)
python command_center.py

# 4. Start scheduler daemon (notifications + auto-scraping)
python scheduler.py
```

## Job Portals Covered

| Portal | Type |
|--------|------|
| LinkedIn | Professional network |
| Indeed | Job aggregator |
| Dice | Tech jobs |
| Glassdoor | Jobs + reviews |
| ZipRecruiter | AI-powered marketplace |
| Monster | Global job board |
| CareerBuilder | Resume + jobs |
| SimplyHired | Job search engine |
| CyberCoders | Tech recruiter |
| ClearanceJobs | Security clearance |
| USAJobs | US Federal Government |
| Jooble | International search |

## Company Career Pages (by Sector)

### Networking Equipment
Cisco, Juniper, Arista, F5, Calix, Ciena, Infinera, Viavi, NetScout, Extreme Networks, CommScope, Cambium

### Cybersecurity
Palo Alto Networks, Fortinet, CrowdStrike, Zscaler, Cloudflare, Qualys, Tenable, SentinelOne, Check Point, Varonis, Rapid7, Okta, CyberArk, Proofpoint, Ping Identity

### Cloud / Hyperscalers
AWS, Microsoft, Google, Meta, Oracle, Salesforce, ServiceNow, Snowflake, VMware, Nutanix

### Telecom / ISP
AT&T, Verizon, T-Mobile, Comcast, Charter, Lumen, Dish Network

### Hardware / Semiconductors
Intel, NVIDIA, Broadcom, Qualcomm, Marvell, Dell, HPE, NetApp, Pure Storage

### IT Services
IBM, Accenture, Cognizant, Infosys, Wipro, HCL, Leidos, SAIC, Booz Allen Hamilton, DXC, ManTech, CACI

### Defense
Raytheon, Northrop Grumman, Lockheed Martin, General Dynamics, L3Harris

### Financial Services
JPMorgan Chase, Bank of America, Goldman Sachs, Citigroup, Wells Fargo, Morgan Stanley

## Command Center Options

| Option | Description |
|--------|-------------|
| View New Jobs | Browse unread/new job listings |
| Apply Now | Opens application page in browser + tracks status |
| Save | Save a job for later review |
| Mark Applied | Track submitted applications |
| Add Notes | Personal notes per job |
| Search | Filter by keyword/company/location |
| By Source | Filter by portal or company |
| By Sector | Browse by company sector |

## Notification Schedule

| Time | Action |
|------|--------|
| 7:00 AM | Morning scrape (background) |
| 8:00 AM | Morning notification |
| 12:00 PM | Midday scrape |
| 5:30 PM | Afternoon scrape |
| 6:00 PM | Evening notification |

## Cron Setup (Optional)

```bash
crontab -e

# Add:
0 7  * * * cd /path/to/networking-jobs && source venv/bin/activate && python scheduler.py --once
0 8  * * * cd /path/to/networking-jobs && source venv/bin/activate && python scheduler.py morning
0 18 * * * cd /path/to/networking-jobs && source venv/bin/activate && python scheduler.py evening
```

## Configuration

Edit `config.py` to customize:
- `JOB_TITLES` — job roles to search
- `MORNING_NOTIFICATION_TIME` / `EVENING_NOTIFICATION_TIME`
- `US_COMPANIES` — add/remove company career pages
- `JOB_PORTALS` — enable/disable portals
