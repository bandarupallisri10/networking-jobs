"""
Job scrapers for multiple portals and company career pages.
Each scraper returns a list of job dicts with standardized fields.
"""
import time
import random
import logging
import requests
from urllib.parse import urlencode, quote_plus
from bs4 import BeautifulSoup
from config import USER_AGENTS, REQUEST_DELAY, JOB_TITLES, LOCATION, JOOBLE_API_KEY, USAJOBS_API_KEY, USAJOBS_EMAIL

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def make_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    })
    return s


def safe_get(session, url, timeout=8):
    try:
        time.sleep(REQUEST_DELAY)
        resp = session.get(url, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        return resp
    except Exception as e:
        logger.warning(f"[HTTP] Failed {url}: {e}")
        return None


def fetch_job_description(url: str) -> str:
    """Fetch and extract the description text from a job posting URL."""
    session = make_session()
    resp = safe_get(session, url, timeout=8)
    if not resp:
        return ""
    soup = BeautifulSoup(resp.text, "html.parser")
    # Remove nav/header/footer noise
    for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
        tag.decompose()
    # Try known job description containers first
    for selector in [
        "div[class*='description']", "div[class*='job-detail']",
        "div[class*='jobDetail']", "section[class*='description']",
        "div#job-description", "div.job_description", "div.jobsearch-jobDescriptionText",
    ]:
        el = soup.select_one(selector)
        if el:
            return el.get_text(" ", strip=True)[:3000]
    # Fallback: main content
    main = soup.select_one("main") or soup.select_one("article") or soup.body
    return main.get_text(" ", strip=True)[:3000] if main else ""


def _empty_job(title, company, url, source, location="United States"):
    return {
        "title": title,
        "company": company,
        "location": location,
        "salary": "Not listed",
        "job_type": "Full-time",
        "source": source,
        "url": url,
        "description": "",
        "posted_date": "",
    }


# ============================================================
# INDEED SCRAPER
# ============================================================
def scrape_indeed(title: str) -> list:
    jobs = []
    session = make_session()
    params = {
        "q": title,
        "l": "United States",
        "fromage": "7",
        "sort": "date",
    }
    url = f"https://www.indeed.com/jobs?{urlencode(params)}"
    resp = safe_get(session, url)
    if not resp:
        return jobs
    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.select("div.job_seen_beacon, div.jobsearch-SerpJobCard, div[data-jk]")
    for card in cards[:20]:
        try:
            t = card.select_one("h2.jobTitle span, a.jobtitle")
            c = card.select_one("span.companyName, span[data-testid='company-name']")
            loc = card.select_one("div.companyLocation, div[data-testid='text-location']")
            sal = card.select_one("div.salary-snippet-container, div.metadata.salary-snippet-container")
            link_tag = card.select_one("a[href*='/rc/clk'], a[href*='viewjob']")
            if not t or not c:
                continue
            job_url = ""
            if link_tag and link_tag.get("href"):
                href = link_tag["href"]
                job_url = href if href.startswith("http") else f"https://www.indeed.com{href}"
            job = _empty_job(
                title=t.get_text(strip=True),
                company=c.get_text(strip=True),
                url=job_url or url,
                source="Indeed",
                location=loc.get_text(strip=True) if loc else "United States",
            )
            if sal:
                job["salary"] = sal.get_text(strip=True)
            jobs.append(job)
        except Exception:
            continue
    logger.info(f"[Indeed] Found {len(jobs)} jobs for '{title}'")
    return jobs


# ============================================================
# DICE SCRAPER
# ============================================================
def scrape_dice(title: str) -> list:
    jobs = []
    session = make_session()
    params = {
        "q": title,
        "location": "United States",
        "radius": "30",
        "radiusUnit": "mi",
        "page": "1",
        "pageSize": "20",
        "filters.postedDate": "ONE_WEEK",
        "language": "en",
    }
    url = f"https://job-search-api.svc.dhigroupinc.com/v1/dice/jobs/search?{urlencode(params)}"
    session.headers.update({"Accept": "application/json", "x-api-key": "1YAt0R9wBg4WfsF9VB2778F5CHLAPMVW3WAZcKd8"})
    resp = safe_get(session, url)
    if not resp:
        return jobs
    try:
        data = resp.json()
        for item in data.get("data", [])[:20]:
            job = _empty_job(
                title=item.get("title", title),
                company=item.get("advertiserName", "Unknown"),
                url=item.get("applyUrl") or item.get("jobDetailUrl") or "https://dice.com",
                source="Dice",
                location=item.get("location", "United States"),
            )
            job["posted_date"] = item.get("postedDate", "")
            jobs.append(job)
    except Exception as e:
        logger.warning(f"[Dice] JSON parse error: {e}")
    logger.info(f"[Dice] Found {len(jobs)} jobs for '{title}'")
    return jobs


# ============================================================
# LINKEDIN SCRAPER (guest API endpoint - no login required)
# ============================================================
def scrape_linkedin(title: str) -> list:
    jobs = []
    session = make_session()
    session.headers.update({
        "Referer": "https://www.linkedin.com/",
        "X-Li-Lang": "en_US",
    })
    # Use the guest jobs API which returns job card HTML without login
    params = {
        "keywords": title,
        "location": "United States",
        "geoId": "103644278",
        "f_TPR": "r604800",  # past week
        "position": "1",
        "pageNum": "0",
        "start": "0",
    }
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?{urlencode(params)}"
    resp = safe_get(session, url)
    if not resp:
        return jobs
    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.select("li, div.base-card")
    for card in cards[:20]:
        try:
            t = card.select_one("h3.base-search-card__title, span.sr-only, h3")
            c = card.select_one("h4.base-search-card__subtitle, h4, a[class*='company']")
            loc = card.select_one("span.job-search-card__location, span[class*='location']")
            link_tag = card.select_one("a.base-card__full-link, a[href*='/jobs/view/']")
            if not t or not link_tag:
                continue
            job_url = link_tag["href"].split("?")[0]  # strip tracking params
            job = _empty_job(
                title=t.get_text(strip=True),
                company=c.get_text(strip=True) if c else "Unknown",
                url=job_url,
                source="LinkedIn",
                location=loc.get_text(strip=True) if loc else "United States",
            )
            jobs.append(job)
        except Exception:
            continue
    logger.info(f"[LinkedIn] Found {len(jobs)} jobs for '{title}'")
    return jobs


# ============================================================
# ZIPRECRUITER SCRAPER
# ============================================================
def scrape_ziprecruiter(title: str) -> list:
    jobs = []
    session = make_session()
    params = {
        "search": title,
        "location": "United States",
        "days": "7",
        "radius": "25",
    }
    url = f"https://www.ziprecruiter.com/jobs-search?{urlencode(params)}"
    resp = safe_get(session, url)
    if not resp:
        return jobs
    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.select("article.job_result, div[data-testid='job-card']")
    for card in cards[:20]:
        try:
            t = card.select_one("h2[class*='title'], a[class*='job_link']")
            c = card.select_one("a[class*='company'], span[class*='company']")
            loc = card.select_one("span[class*='location']")
            sal = card.select_one("span[class*='salary']")
            link_tag = card.select_one("a[href*='/jobs/']")
            if not t:
                continue
            job_url = link_tag["href"] if link_tag and link_tag.get("href") else url
            if job_url and not job_url.startswith("http"):
                job_url = f"https://www.ziprecruiter.com{job_url}"
            job = _empty_job(
                title=t.get_text(strip=True),
                company=c.get_text(strip=True) if c else "Unknown",
                url=job_url,
                source="ZipRecruiter",
                location=loc.get_text(strip=True) if loc else "United States",
            )
            if sal:
                job["salary"] = sal.get_text(strip=True)
            jobs.append(job)
        except Exception:
            continue
    logger.info(f"[ZipRecruiter] Found {len(jobs)} jobs for '{title}'")
    return jobs


# ============================================================
# GLASSDOOR SCRAPER
# ============================================================
def scrape_glassdoor(title: str) -> list:
    jobs = []
    session = make_session()
    params = {
        "keyword": title,
        "locT": "N",
        "locId": "1",
        "fromAge": "7",
    }
    url = f"https://www.glassdoor.com/Job/jobs.htm?{urlencode(params)}"
    resp = safe_get(session, url)
    if not resp:
        return jobs
    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.select("li[data-test='jobListing'], div.react-job-listing")
    for card in cards[:20]:
        try:
            t = card.select_one("a[data-test='job-title'], div[data-test='job-title']")
            c = card.select_one("div[data-test='employer-name'], span[class*='employer']")
            loc = card.select_one("span[data-test='emp-location']")
            sal = card.select_one("span[data-test='detailSalary']")
            link_tag = card.select_one("a[href*='/job-listing/']")
            if not t:
                continue
            job_url = link_tag["href"] if link_tag and link_tag.get("href") else url
            if job_url and not job_url.startswith("http"):
                job_url = f"https://www.glassdoor.com{job_url}"
            job = _empty_job(
                title=t.get_text(strip=True),
                company=c.get_text(strip=True) if c else "Unknown",
                url=job_url,
                source="Glassdoor",
                location=loc.get_text(strip=True) if loc else "United States",
            )
            if sal:
                job["salary"] = sal.get_text(strip=True)
            jobs.append(job)
        except Exception:
            continue
    logger.info(f"[Glassdoor] Found {len(jobs)} jobs for '{title}'")
    return jobs


# ============================================================
# MONSTER SCRAPER
# ============================================================
def scrape_monster(title: str) -> list:
    jobs = []
    session = make_session()
    params = {
        "q": title,
        "where": "United States",
        "tm": "7",
    }
    url = f"https://www.monster.com/jobs/search?{urlencode(params)}"
    resp = safe_get(session, url)
    if not resp:
        return jobs
    soup = BeautifulSoup(resp.text, "html.parser")
    # Updated selectors for Monster's current layout
    cards = soup.select(
        "section.card-content, div[data-jobid], "
        "div[class*='job-search-card'], figure[class*='card']"
    )
    for card in cards[:20]:
        try:
            t = card.select_one(
                "h2.title, a[class*='job-title'], "
                "h3[class*='title'], a[data-bypass]"
            )
            c = card.select_one(
                "div.company, span[class*='company'], "
                "div[class*='company'], p[class*='name']"
            )
            loc = card.select_one(
                "div.location, span[class*='location'], "
                "div[class*='location'], p[class*='location']"
            )
            link_tag = card.select_one("a[href*='/jobs/'], a[href*='monster.com']")
            if not t:
                continue
            job_url = link_tag["href"] if link_tag and link_tag.get("href") else url
            job = _empty_job(
                title=t.get_text(strip=True),
                company=c.get_text(strip=True) if c else "Unknown",
                url=job_url,
                source="Monster",
                location=loc.get_text(strip=True) if loc else "United States",
            )
            jobs.append(job)
        except Exception:
            continue
    logger.info(f"[Monster] Found {len(jobs)} jobs for '{title}'")
    return jobs


# ============================================================
# CAREERBUILDER SCRAPER
# ============================================================
def scrape_careerbuilder(title: str) -> list:
    jobs = []
    session = make_session()
    params = {
        "keywords": title,
        "location": "United States",
        "date_from": "7",
    }
    url = f"https://www.careerbuilder.com/jobs?{urlencode(params)}"
    resp = safe_get(session, url)
    if not resp:
        return jobs
    soup = BeautifulSoup(resp.text, "html.parser")
    # Updated selectors for CareerBuilder's current layout
    cards = soup.select(
        "li[data-job-did], div.data-results-content, "
        "div[class*='job-listing'], article[class*='job']"
    )
    for card in cards[:20]:
        try:
            t = card.select_one(
                "h2.title, span[itemprop='title'], "
                "a[class*='job-title'], h3[class*='title']"
            )
            c = card.select_one(
                "div.subtitle, span[itemprop='name'], "
                "span[class*='company'], div[class*='company']"
            )
            loc = card.select_one(
                "span[itemprop='addressLocality'], div.location, "
                "span[class*='location']"
            )
            link_tag = card.select_one("a[href*='/job/'], a[href*='careerbuilder.com']")
            if not t:
                continue
            job_url = link_tag["href"] if link_tag and link_tag.get("href") else url
            if job_url and not job_url.startswith("http"):
                job_url = f"https://www.careerbuilder.com{job_url}"
            job = _empty_job(
                title=t.get_text(strip=True),
                company=c.get_text(strip=True) if c else "Unknown",
                url=job_url,
                source="CareerBuilder",
                location=loc.get_text(strip=True) if loc else "United States",
            )
            jobs.append(job)
        except Exception:
            continue
    logger.info(f"[CareerBuilder] Found {len(jobs)} jobs for '{title}'")
    return jobs


# ============================================================
# SIMPLYHIRED SCRAPER
# ============================================================
def scrape_simplyhired(title: str) -> list:
    jobs = []
    session = make_session()
    params = {
        "q": title,
        "l": "United States",
        "t": "7",
    }
    url = f"https://www.simplyhired.com/search?{urlencode(params)}"
    resp = safe_get(session, url)
    if not resp:
        return jobs
    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.select("div[data-jobkey], article.SerpJob")
    for card in cards[:20]:
        try:
            t = card.select_one("h2.jobposting-title, a[data-mdref='jobTitle']")
            c = card.select_one("span[data-mdref='jobEmployerName'], span.jobposting-company")
            loc = card.select_one("span[data-mdref='jobLocation']")
            sal = card.select_one("p[data-mdref='salaryEstimate']")
            link_tag = card.select_one("a[href*='/job/']")
            if not t:
                continue
            job_url = link_tag["href"] if link_tag and link_tag.get("href") else url
            if job_url and not job_url.startswith("http"):
                job_url = f"https://www.simplyhired.com{job_url}"
            job = _empty_job(
                title=t.get_text(strip=True),
                company=c.get_text(strip=True) if c else "Unknown",
                url=job_url,
                source="SimplyHired",
                location=loc.get_text(strip=True) if loc else "United States",
            )
            if sal:
                job["salary"] = sal.get_text(strip=True)
            jobs.append(job)
        except Exception:
            continue
    logger.info(f"[SimplyHired] Found {len(jobs)} jobs for '{title}'")
    return jobs


# ============================================================
# CYBERCODERS SCRAPER
# ============================================================
def scrape_cybercoders(title: str) -> list:
    jobs = []
    session = make_session()
    params = {
        "q": title,
        "location": "United States",
    }
    url = f"https://www.cybercoders.com/search/?{urlencode(params)}"
    resp = safe_get(session, url)
    if not resp:
        return jobs
    soup = BeautifulSoup(resp.text, "html.parser")
    # CyberCoders updated their markup — try multiple selectors
    cards = soup.select(
        "div.job-listing-item, div[class*='job-listing'], "
        "li[class*='job'], div[class*='JobCard']"
    )
    for card in cards[:20]:
        try:
            t = card.select_one(
                "div.job-title a, a[class*='job-title'], "
                "h2 a, h3 a, a[class*='title']"
            )
            c = card.select_one(
                "div.company-name, span[class*='company'], "
                "div[class*='company']"
            )
            loc = card.select_one(
                "div.location, span[class*='location'], "
                "div[class*='location']"
            )
            sal = card.select_one("div.wage, span[class*='salary'], div[class*='salary']")
            link_tag = t if t and t.name == "a" else card.select_one("a[href*='/jobs/'], a[href*='cybercoders']")
            if not t:
                continue
            job_url = link_tag["href"] if link_tag and link_tag.get("href") else url
            if job_url and not job_url.startswith("http"):
                job_url = f"https://www.cybercoders.com{job_url}"
            job = _empty_job(
                title=t.get_text(strip=True),
                company=c.get_text(strip=True) if c else "CyberCoders Client",
                url=job_url,
                source="CyberCoders",
                location=loc.get_text(strip=True) if loc else "United States",
            )
            if sal:
                job["salary"] = sal.get_text(strip=True)
            jobs.append(job)
        except Exception:
            continue
    logger.info(f"[CyberCoders] Found {len(jobs)} jobs for '{title}'")
    return jobs


# ============================================================
# CLEARANCEJOBS SCRAPER
# ============================================================
def scrape_clearancejobs(title: str) -> list:
    jobs = []
    session = make_session()
    params = {
        "q": title,
        "radius": "0",
        "location": "United States",
    }
    url = f"https://www.clearancejobs.com/jobs?{urlencode(params)}"
    resp = safe_get(session, url)
    if not resp:
        return jobs
    soup = BeautifulSoup(resp.text, "html.parser")
    # Try multiple selectors for ClearanceJobs layout
    cards = soup.select(
        "div[class*='job-card'], article[class*='job'], "
        "li[class*='job'], div[class*='JobCard'], "
        "div[data-id], section[class*='result']"
    )
    for card in cards[:15]:
        try:
            t = card.select_one(
                "h2, h3, a[class*='title'], "
                "span[class*='title'], div[class*='title'] a"
            )
            c = card.select_one(
                "span[class*='company'], div[class*='company'], "
                "p[class*='company']"
            )
            loc = card.select_one(
                "span[class*='location'], div[class*='location'], "
                "p[class*='location']"
            )
            link_tag = card.select_one("a[href*='/jobs/'], a[href*='clearancejobs.com']")
            if not t:
                continue
            job_url = link_tag["href"] if link_tag and link_tag.get("href") else url
            if job_url and not job_url.startswith("http"):
                job_url = f"https://www.clearancejobs.com{job_url}"
            job = _empty_job(
                title=t.get_text(strip=True),
                company=c.get_text(strip=True) if c else "Unknown",
                url=job_url,
                source="ClearanceJobs",
                location=loc.get_text(strip=True) if loc else "United States",
            )
            jobs.append(job)
        except Exception:
            continue
    logger.info(f"[ClearanceJobs] Found {len(jobs)} jobs for '{title}'")
    return jobs


# ============================================================
# USAJOBS SCRAPER (Government API)
# ============================================================
def scrape_usajobs(title: str) -> list:
    jobs = []

    # Use official API if credentials are configured
    if USAJOBS_API_KEY and USAJOBS_EMAIL:
        session = make_session()
        session.headers.update({
            "Authorization-Key": USAJOBS_API_KEY,
            "User-Agent": USAJOBS_EMAIL,
            "Host": "data.usajobs.gov",
        })
        params = {
            "Keyword": title,
            "LocationName": "United States",
            "ResultsPerPage": "25",
            "SortField": "OpenDate",
            "SortDirection": "Desc",
        }
        url = f"https://data.usajobs.gov/api/search?{urlencode(params)}"
        resp = safe_get(session, url)
        if resp:
            try:
                data = resp.json()
                results = data.get("SearchResult", {}).get("SearchResultItems", [])
                for item in results[:20]:
                    pos = item.get("MatchedObjectDescriptor", {})
                    job = _empty_job(
                        title=pos.get("PositionTitle", title),
                        company=pos.get("OrganizationName", "US Federal Government"),
                        url=pos.get("PositionURI", "https://www.usajobs.gov"),
                        source="USAJobs",
                        location=", ".join([loc.get("LocationName", "") for loc in pos.get("PositionLocation", [])]),
                    )
                    remun = pos.get("PositionRemuneration", [])
                    if remun:
                        r = remun[0]
                        job["salary"] = f"${r.get('MinimumRange','')}-${r.get('MaximumRange','')} {r.get('RateIntervalCode','')}"
                    jobs.append(job)
                logger.info(f"[USAJobs] Found {len(jobs)} jobs for '{title}' (API)")
                return jobs
            except Exception as e:
                logger.warning(f"[USAJobs] API error: {e}")

    # Web fallback (no API key needed)
    web_url = f"https://www.usajobs.gov/search/results/?k={quote_plus(title)}&l=United+States"
    resp = safe_get(make_session(), web_url)
    if resp:
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select("div.usajobs-search-result--core")
        for card in cards[:15]:
            try:
                t = card.select_one("h2.usajobs-search-result--core__title a")
                c = card.select_one("span[class*='dept']")
                loc = card.select_one("span[class*='location']")
                if not t:
                    continue
                job_url = t["href"] if t.get("href") else web_url
                if job_url and not job_url.startswith("http"):
                    job_url = f"https://www.usajobs.gov{job_url}"
                job = _empty_job(
                    title=t.get_text(strip=True),
                    company=c.get_text(strip=True) if c else "US Federal Government",
                    url=job_url,
                    source="USAJobs",
                    location=loc.get_text(strip=True) if loc else "United States",
                )
                jobs.append(job)
            except Exception:
                continue

    logger.info(f"[USAJobs] Found {len(jobs)} jobs for '{title}'")
    return jobs


# ============================================================
# JOOBLE SCRAPER (requires free API key from jooble.org/api/about)
# ============================================================
def scrape_jooble(title: str) -> list:
    jobs = []
    if not JOOBLE_API_KEY:
        logger.info(f"[Jooble] Skipping — no API key set (add JOOBLE_API_KEY to config.py)")
        return jobs
    session = make_session()
    session.headers.update({"Content-Type": "application/json"})
    payload = {
        "keywords": title,
        "location": "United States",
        "radius": "",
        "page": "1",
    }
    url = f"https://jooble.org/api/{JOOBLE_API_KEY}"
    try:
        resp = session.post(url, json=payload, timeout=15)
        data = resp.json()
        for item in data.get("jobs", [])[:20]:
            job = _empty_job(
                title=item.get("title", title),
                company=item.get("company", "Unknown"),
                url=item.get("link", "https://jooble.org"),
                source="Jooble",
                location=item.get("location", "United States"),
            )
            job["salary"] = item.get("salary", "Not listed")
            job["posted_date"] = item.get("updated", "")
            jobs.append(job)
    except Exception as e:
        logger.warning(f"[Jooble] Error: {e}")
    logger.info(f"[Jooble] Found {len(jobs)} jobs for '{title}'")
    return jobs


# ============================================================
# REMOTEOK SCRAPER (free public API, no auth needed)
# ============================================================
def scrape_remoteok(title: str) -> list:
    jobs = []
    session = make_session()
    session.headers.update({"Accept": "application/json"})
    # Map title to RemoteOK tags
    tag = title.lower().replace(" ", "-")
    url = f"https://remoteok.com/api?tags={quote_plus(tag)}&limit=20"
    resp = safe_get(session, url)
    if not resp:
        return jobs
    try:
        data = resp.json()
        # First item is metadata, skip it
        for item in data[1:21]:
            if not isinstance(item, dict):
                continue
            job = _empty_job(
                title=item.get("position", title),
                company=item.get("company", "Unknown"),
                url=item.get("url") or f"https://remoteok.com/remote-jobs/{item.get('id','')}",
                source="RemoteOK",
                location="Remote / United States",
            )
            tags = item.get("tags", [])
            job["salary"] = item.get("salary", "Not listed") or "Not listed"
            job["posted_date"] = item.get("date", "")
            jobs.append(job)
    except Exception as e:
        logger.warning(f"[RemoteOK] Error: {e}")
    logger.info(f"[RemoteOK] Found {len(jobs)} jobs for '{title}'")
    return jobs


# ============================================================
# THE MUSE SCRAPER (free public API, no auth needed)
# ============================================================
def scrape_themuse(title: str) -> list:
    jobs = []
    session = make_session()
    session.headers.update({"Accept": "application/json"})
    params = {
        "category": "IT & Engineering",
        "location": "United States",
        "page": "0",
        "count": "20",
        "descending": "true",
    }
    url = f"https://www.themuse.com/api/public/jobs?{urlencode(params)}"
    resp = safe_get(session, url)
    if not resp:
        return jobs
    try:
        data = resp.json()
        title_lower = title.lower()
        keywords = set(title_lower.split())
        for item in data.get("results", []):
            job_name = item.get("name", "").lower()
            # Filter by relevance to title keywords
            if not any(kw in job_name for kw in keywords):
                continue
            company = item.get("company", {}).get("name", "Unknown")
            locations = item.get("locations", [])
            loc_str = locations[0].get("name", "United States") if locations else "United States"
            levels = item.get("levels", [])
            job = _empty_job(
                title=item.get("name", title),
                company=company,
                url=item.get("refs", {}).get("landing_page", "https://www.themuse.com"),
                source="The Muse",
                location=loc_str,
            )
            job["posted_date"] = item.get("publication_date", "")
            jobs.append(job)
    except Exception as e:
        logger.warning(f"[The Muse] Error: {e}")
    logger.info(f"[The Muse] Found {len(jobs)} jobs for '{title}'")
    return jobs


# ============================================================
# GENERIC COMPANY CAREER PAGE SCRAPER
# ============================================================
def scrape_company_careers(company_name: str, careers_url: str, title: str) -> list:
    """
    Generic scraper for company career pages.
    Tries to find job listings matching the title.
    """
    jobs = []
    session = make_session()

    # Build search URLs for common ATS platforms
    search_urls = _build_ats_urls(careers_url, title)

    for search_url in search_urls:
        resp = safe_get(session, search_url)
        if not resp:
            continue
        soup = BeautifulSoup(resp.text, "html.parser")

        # Try to find job cards with various selectors
        cards = (
            soup.select("tr.data-row")
            or soup.select("li[class*='job']")
            or soup.select("div[class*='job-card']")
            or soup.select("div[class*='position']")
            or soup.select("div[class*='opening']")
            or soup.select("article")
            or soup.select("div[class*='result']")
        )

        for card in cards[:15]:
            text = card.get_text(" ", strip=True).lower()
            # Filter: must mention a network-related keyword
            if not any(kw in text for kw in ["network", "security", "cisco", "firewall", "routing", "switching"]):
                continue
            link_tag = card.select_one("a[href]")
            t_tag = card.select_one("h1, h2, h3, h4, a")
            if not t_tag:
                continue
            job_url = link_tag["href"] if link_tag else search_url
            if job_url and not job_url.startswith("http"):
                from urllib.parse import urlparse, urljoin
                job_url = urljoin(search_url, job_url)
            job = _empty_job(
                title=t_tag.get_text(strip=True)[:120],
                company=company_name,
                url=job_url,
                source=f"Company: {company_name}",
                location="United States",
            )
            jobs.append(job)

        if jobs:
            break  # Found results, stop trying other URLs

    logger.info(f"[{company_name}] Found {len(jobs)} jobs for '{title}'")
    return jobs


def _build_ats_urls(base_url: str, title: str) -> list:
    """Generate search URLs for known ATS platforms."""
    q = quote_plus(title)
    urls = []

    # Workday
    if "myworkdayjobs.com" in base_url or "wd5.myworkdayjobs" in base_url:
        urls.append(f"{base_url}?q={q}&locationCountry=bc33aa3152ec42d4995f4791a106ed09")
    # Greenhouse
    elif "greenhouse.io" in base_url:
        urls.append(f"{base_url}?q={q}")
    # Lever
    elif "lever.co" in base_url:
        urls.append(f"{base_url}?search={q}&team=Engineering")
    # Taleo
    elif "taleo.net" in base_url:
        urls.append(f"{base_url}?q={q}&l=United+States")
    # iCIMS
    elif "icims.com" in base_url:
        urls.append(f"{base_url}?searchKeyword={q}&searchLocation=")
    # SmartRecruiters
    elif "smartrecruiters.com" in base_url:
        urls.append(f"{base_url}?keyword={q}")
    # Default: append common search params
    else:
        from urllib.parse import urljoin
        urls.append(f"{base_url}?q={q}&location=United+States")
        urls.append(f"{base_url}?keyword={q}")
        urls.append(f"{base_url}?keywords={q}&location=United+States")
        urls.append(base_url)

    return urls


# ============================================================
# MASTER SCRAPE FUNCTION
# ============================================================
PORTAL_SCRAPERS = {
    "Indeed": scrape_indeed,
    "Dice": scrape_dice,
    "LinkedIn": scrape_linkedin,
    "ZipRecruiter": scrape_ziprecruiter,
    "Glassdoor": scrape_glassdoor,
    "Monster": scrape_monster,
    "CareerBuilder": scrape_careerbuilder,
    "SimplyHired": scrape_simplyhired,
    "CyberCoders": scrape_cybercoders,
    "ClearanceJobs": scrape_clearancejobs,
    "USAJobs": scrape_usajobs,
    "Jooble": scrape_jooble,
    "RemoteOK": scrape_remoteok,
    "The Muse": scrape_themuse,
}


def scrape_all_portals(title: str, progress_callback=None) -> list:
    """Scrape all job portals for a given title in parallel."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    all_jobs = []

    def _scrape(portal_name, scraper_fn):
        try:
            jobs = scraper_fn(title)
            if progress_callback:
                progress_callback(portal_name, len(jobs))
            return jobs
        except Exception as e:
            logger.error(f"[{portal_name}] Scraper error: {e}")
            return []

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(_scrape, name, fn): name
            for name, fn in PORTAL_SCRAPERS.items()
        }
        for future in as_completed(futures):
            all_jobs.extend(future.result())

    return all_jobs


def scrape_all_companies(title: str, companies: dict, progress_callback=None) -> list:
    """Scrape all company career pages for a given title in parallel."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from config import US_COMPANIES

    target = companies if companies else US_COMPANIES
    all_jobs = []

    def _scrape(company_name, info):
        try:
            jobs = scrape_company_careers(company_name, info["careers_url"], title)
            if progress_callback:
                progress_callback(company_name, len(jobs))
            return jobs
        except Exception as e:
            logger.error(f"[{company_name}] Career page error: {e}")
            return []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(_scrape, name, info): name
            for name, info in target.items()
        }
        for future in as_completed(futures):
            all_jobs.extend(future.result())

    return all_jobs
