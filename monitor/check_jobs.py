#!/usr/bin/env python3
"""
Internship & Analyst Application Monitor
Checks career pages daily for new postings and files GitHub issues.

Methods:
  greenhouse  - Greenhouse public JSON API (exact job titles)
  lever       - Lever public JSON API (exact job titles)
  workday     - Workday standard POST search API (exact job titles)
  page_hash   - SHA-256 hash comparison (detects any page change)
"""

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

SCRIPT_DIR    = Path(__file__).parent
STATE_FILE    = SCRIPT_DIR / "state.json"
FINDINGS_FILE = SCRIPT_DIR / "new_findings.json"

KEYWORDS = [
    "intern", "internship", "summer analyst", "summer associate",
    "analyst program", "2027", "analyst intern",
]
EXCLUDE = [
    "senior", "director", "managing director", " md ", "vp ",
    "vice president", "partner", "principal", "head of",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

COMPANIES = [
    # ── TRACK 4: Big 4 Consulting ─────────────────────────────────────────
    {
        "name": "McKinsey & Company", "track": 4, "method": "page_hash",
        "url": "https://www.mckinsey.com/careers/search-jobs",
    },
    {
        "name": "BCG", "track": 4, "method": "page_hash",
        "url": "https://careers.bcg.com/students",
    },
    {
        "name": "Bain & Company", "track": 4, "method": "page_hash",
        "url": "https://www.bain.com/careers/find-a-role/?type=Internship",
    },
    {
        "name": "Deloitte", "track": 4, "method": "page_hash",
        "url": "https://apply.deloitte.com/careers/SearchJobs/intern",
    },
    {
        "name": "PwC Strategy&", "track": 4, "method": "page_hash",
        "url": "https://www.pwc.com/us/en/careers/campus.html",
    },
    {
        "name": "KPMG Advisory", "track": 4, "method": "page_hash",
        "url": "https://www.kpmg.com/us/en/careers/students-and-recent-grads/internships.html",
    },
    {
        "name": "EY-Parthenon", "track": 4, "method": "page_hash",
        "url": "https://careers.ey.com/ey/search/#/?query=intern",
    },
    {
        "name": "Oliver Wyman", "track": 4, "method": "page_hash",
        "url": "https://www.oliverwyman.com/careers/entry-level.html",
    },
    {
        "name": "LEK Consulting", "track": 4, "method": "page_hash",
        "url": "https://www.lek.com/join-lek/apply/internships",
    },
    {
        "name": "Accenture Strategy", "track": 4, "method": "page_hash",
        "url": "https://www.accenture.com/us-en/careers/local/students",
    },

    # ── TRACK 5: Finance & Investment Banking ─────────────────────────────
    {
        "name": "Goldman Sachs", "track": 5, "method": "page_hash",
        "url": "https://higher.gs.com/roles",
    },
    {
        "name": "JPMorgan", "track": 5, "method": "page_hash",
        "url": "https://jpmorgan.wd1.myworkdayjobs.com/JPMorgan",
    },
    {
        "name": "Morgan Stanley", "track": 5, "method": "page_hash",
        "url": "https://www.morganstanley.com/people-opportunities/students-graduates",
    },
    {
        "name": "Bank of America", "track": 5, "method": "page_hash",
        "url": "https://campus.bankofamerica.com/opportunities.html",
    },
    {
        "name": "Citigroup", "track": 5, "method": "workday",
        "tenant": "citi", "host": "citi.wd5.myworkdayjobs.com", "site": "2",
    },
    {
        "name": "Barclays", "track": 5, "method": "page_hash",
        "url": "https://search.jobs.barclays/search-jobs/internship/United-States/22160/1/5/6252001/39x76/-98x5/50/2",
    },
    {
        "name": "Deutsche Bank", "track": 5, "method": "page_hash",
        "url": "https://careers.db.com/professionals/search-roles/#/internship/United%20States",
    },
    {
        "name": "UBS", "track": 5, "method": "page_hash",
        "url": "https://ubs.wd3.myworkdayjobs.com/UBS_Global",
    },
    {
        "name": "BlackRock", "track": 5, "method": "page_hash",
        "url": "https://blackrock.wd1.myworkdayjobs.com/BlackRock_Global",
    },
    {
        "name": "Blackstone", "track": 5, "method": "page_hash",
        "url": "https://www.blackstone.com/careers/students/",
    },
    {
        "name": "KKR", "track": 5, "method": "page_hash",
        "url": "https://www.kkr.com/careers",
    },
    {
        "name": "Citadel", "track": 5, "method": "page_hash",
        "url": "https://www.citadel.com/careers/open-positions/",
    },
    {
        "name": "Point72", "track": 5, "method": "page_hash",
        "url": "https://careers.point72.com/?experience=Early+Career%3BInternships",
    },
    {
        "name": "Jane Street", "track": 5, "method": "page_hash",
        "url": "https://www.janestreet.com/join-jane-street/open-roles/",
    },
    {
        "name": "Bridgewater", "track": 5, "method": "page_hash",
        "url": "https://www.bridgewater.com/working-at-bridgewater/students",
    },
    {
        "name": "Fidelity", "track": 5, "method": "page_hash",
        "url": "https://jobs.fidelity.com/en/students/internships/",
    },

    # ── TRACK 1: CE / AI SE (key fall openers) ───────────────────────────
    {
        "name": "Google (BOLD / gTech)", "track": 1, "method": "page_hash",
        "url": "https://www.google.com/about/careers/applications/jobs/results/?employment_type=INTERN&q=bold",
    },
    {
        "name": "Salesforce", "track": 1, "method": "page_hash",
        "url": "https://salesforce.wd12.myworkdayjobs.com/Futureforce_Internships",
    },
    {
        "name": "Databricks", "track": 1, "method": "greenhouse",
        "slug": "databricks",
    },
    {
        "name": "Cohere", "track": 1, "method": "page_hash",
        "url": "https://cohere.com/careers",
    },
    {
        "name": "AWS (Amazon)", "track": 1, "method": "page_hash",
        "url": "https://www.amazon.jobs/en/search?offset=0&result_limit=10&sort=relevant&category%5B%5D=software-development&business_category%5B%5D=amazon-web-services&job_type%5B%5D=intern",
    },
]


# ── Helpers ───────────────────────────────────────────────────────────────

def is_relevant(title: str) -> bool:
    t = title.lower()
    if not any(kw in t for kw in KEYWORDS):
        return False
    if any(ex in t for ex in EXCLUDE):
        return False
    return True


def check_greenhouse(slug: str) -> tuple[list[dict], str | None]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 404:
            return [], f"Greenhouse slug '{slug}' not found — update in check_jobs.py"
        if r.status_code != 200:
            return [], f"HTTP {r.status_code}"
        return [
            {
                "id":       str(j["id"]),
                "title":    j.get("title", ""),
                "url":      j.get("absolute_url", ""),
                "location": j.get("location", {}).get("name", ""),
            }
            for j in r.json().get("jobs", [])
            if is_relevant(j.get("title", ""))
        ], None
    except Exception as e:
        return [], str(e)


def check_lever(slug: str) -> tuple[list[dict], str | None]:
    url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return [], f"HTTP {r.status_code}"
        return [
            {
                "id":       j["id"],
                "title":    j.get("text", ""),
                "url":      j.get("hostedUrl", ""),
                "location": j.get("categories", {}).get("location", ""),
            }
            for j in r.json()
            if is_relevant(j.get("text", ""))
        ], None
    except Exception as e:
        return [], str(e)


def check_workday(tenant: str, host: str, site: str) -> tuple[list[dict], str | None]:
    url     = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
    payload = {"limit": 20, "offset": 0, "searchText": "intern analyst 2027"}
    try:
        r = requests.post(
            url,
            json=payload,
            headers={**HEADERS, "Content-Type": "application/json"},
            timeout=15,
        )
        if r.status_code != 200:
            return [], f"HTTP {r.status_code}"
        postings = r.json().get("jobPostings", [])
        return [
            {
                "id":       j.get("externalPath", j.get("title", "")),
                "title":    j.get("title", ""),
                "url":      f"https://{host}{j.get('externalPath', '')}",
                "location": j.get("locationsText", ""),
            }
            for j in postings
            if is_relevant(j.get("title", ""))
        ], None
    except Exception as e:
        return [], str(e)


def check_page_hash(url: str) -> tuple[str | None, str | None]:
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            return None, f"HTTP {r.status_code}"
        return hashlib.sha256(r.text.encode()).hexdigest(), None
    except Exception as e:
        return None, str(e)


# ── State persistence ─────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"last_run": None, "companies": {}}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ── GitHub issue creation ─────────────────────────────────────────────────

def create_github_issue(title: str, body: str):
    token = os.environ.get("GITHUB_TOKEN")
    repo  = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        print("\n[DRY RUN] Would create issue:")
        print(f"  Title: {title}")
        print(f"  Body preview: {body[:300]}...")
        return
    resp = requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers={
            "Authorization":        f"Bearer {token}",
            "Accept":               "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        json={"title": title, "body": body},
        timeout=10,
    )
    if resp.status_code == 201:
        print(f"  Issue created: {resp.json().get('html_url', '')}")
    else:
        print(f"  Failed to create issue: {resp.status_code} {resp.text[:200]}")


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    state  = load_state()
    now    = datetime.now(timezone.utc).isoformat()
    alerts: list[dict] = []

    print(f"Job monitor starting — {now}\n{'─'*60}")

    for co in COMPANIES:
        name   = co["name"]
        method = co["method"]
        co_st  = state["companies"].setdefault(name, {"seen_ids": [], "hash": None})

        print(f"  {name:35s} [{method:10s}] ", end="", flush=True)
        time.sleep(1.5)  # be polite to external servers

        # ── page_hash ──────────────────────────────────────────────────
        if method == "page_hash":
            new_hash, err = check_page_hash(co["url"])
            if err:
                print(f"error: {err}")
                continue
            old_hash = co_st.get("hash")
            if old_hash is None:
                co_st["hash"] = new_hash
                print("baseline set")
            elif new_hash != old_hash:
                co_st["hash"] = new_hash
                print("CHANGED ← careers page updated")
                alerts.append({
                    "company": name, "track": co["track"], "method": "page_hash",
                    "url": co["url"], "jobs": [],
                    "detail": "Careers page content changed — new postings may be live.",
                })
            else:
                print("unchanged")
            continue

        # ── API methods (greenhouse / lever / workday) ─────────────────
        if method == "greenhouse":
            jobs, err = check_greenhouse(co["slug"])
        elif method == "lever":
            jobs, err = check_lever(co["slug"])
        elif method == "workday":
            jobs, err = check_workday(co["tenant"], co["host"], co["site"])
        else:
            print(f"unknown method: {method}")
            continue

        if err:
            print(f"error: {err}")
            continue

        seen     = set(co_st.get("seen_ids", []))
        new_jobs = [j for j in jobs if j["id"] not in seen]

        if new_jobs:
            co_st["seen_ids"] = list(seen | {j["id"] for j in new_jobs})
            print(f"NEW — {len(new_jobs)} posting(s) found")
            alerts.append({
                "company": name, "track": co["track"], "method": method,
                "url": "", "jobs": new_jobs,
                "detail": f"{len(new_jobs)} new posting(s) match internship/analyst keywords.",
            })
        else:
            print(f"ok ({len(jobs)} matching)")
            # Still update seen_ids so any future new ones are caught
            co_st["seen_ids"] = list(seen | {j["id"] for j in jobs})

    state["last_run"] = now
    save_state(state)

    # ── Write API findings to new_findings.json ────────────────────────
    try:
        findings_data = json.loads(FINDINGS_FILE.read_text()) if FINDINGS_FILE.exists() else {"last_updated": None, "findings": []}
    except Exception:
        findings_data = {"last_updated": None, "findings": []}

    existing_ids = {f["id"] for f in findings_data.get("findings", [])}
    for a in alerts:
        for j in a.get("jobs", []):
            fid = f"{a['company']}::{j['id']}"
            if fid not in existing_ids:
                findings_data["findings"].append({
                    "id": fid,
                    "company": a["company"],
                    "role": j["title"],
                    "track": a["track"],
                    "url": j.get("url", ""),
                    "location": j.get("location", ""),
                    "detected": now,
                    "source": a["method"],
                })
                existing_ids.add(fid)

    findings_data["last_updated"] = now
    FINDINGS_FILE.write_text(json.dumps(findings_data, indent=2))

    print(f"\n{'─'*60}")
    if not alerts:
        print("No new postings detected. State saved.")
        return

    # ── Build GitHub issue ─────────────────────────────────────────────
    track_emoji = {1: "🔵", 2: "🟣", 3: "🟠", 4: "🟢", 5: "🟡"}
    date_str    = datetime.now().strftime("%B %d, %Y")

    body_lines = [
        f"# 🚨 Job Alert — {date_str}\n",
        f"The daily monitor found activity on **{len(alerts)}** career page(s).\n",
        f"> Check each listing and add to tracker if relevant.\n",
    ]

    for a in alerts:
        emoji = track_emoji.get(a["track"], "⚪")
        body_lines.append(f"\n---\n## {emoji} {a['company']} &nbsp;·&nbsp; Track {a['track']}")
        body_lines.append(f"_{a['detail']}_\n")

        if a["jobs"]:
            body_lines.append("| Role | Location | Link |")
            body_lines.append("|------|----------|------|")
            for j in a["jobs"][:15]:
                link = f"[Apply →]({j['url']})" if j.get("url") else "—"
                body_lines.append(f"| {j['title']} | {j.get('location', '—')} | {link} |")
        else:
            body_lines.append(f"🔗 **[Open careers page]({a['url']})**")
            body_lines.append(
                "\n> This company's page uses heavy JavaScript so exact job titles "
                "can't be extracted automatically. Click the link above to check for new internship/analyst postings."
            )

    body_lines.append(f"\n\n---\n*Auto-generated by `monitor/check_jobs.py` · {now}*")
    issue_body = "\n".join(body_lines)

    names_preview = ", ".join(a["company"] for a in alerts[:3])
    if len(alerts) > 3:
        names_preview += f" +{len(alerts) - 3} more"

    print(f"Creating GitHub issue for: {names_preview}")
    create_github_issue(f"🚨 Job Alert: {names_preview} — {date_str}", issue_body)


if __name__ == "__main__":
    main()
