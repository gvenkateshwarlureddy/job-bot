# FULL JOB AUTOMATION SYSTEM (Advanced Version)
# Features:
# 1. Multi-country job scraping (Ireland, UAE, Poland)
# 2. Visa sponsorship filtering
# 3. Auto email sending to recruiters
# 4. Excel storage
# 5. Daily automation ready

import requests
from bs4 import BeautifulSoup
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials


HEADERS = {"User-Agent": "Mozilla/5.0"}

KEYWORDS = ["visa sponsorship", "work permit", "relocation"]

URLS = [
    "https://ie.indeed.com/jobs?q=logistics+operations&l=Ireland",
    "https://ae.indeed.com/jobs?q=retail+operations&l=UAE",
    "https://pl.indeed.com/jobs?q=warehouse&l=Poland"
]

EMAIL = "gvenkateshwarlureddy@gmail.com"
PASSWORD = "dxbbamkryizoxpen"

RECRUITERS = [
    "contact@hollilander.com",
]


def fetch_jobs():
    all_jobs = []

    for url in URLS:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")

        for job in soup.select(".job_seen_beacon"):
            title = job.select_one("h2")
            company = job.select_one(".companyName")
            location = job.select_one(".companyLocation")
            summary = job.select_one(".job-snippet")
            link_tag = job.select_one("a")

            title = title.text.strip() if title else ""
            company = company.text.strip() if company else ""
            location = location.text.strip() if location else ""
            summary = summary.text.strip() if summary else ""
            link = "https://indeed.com" + link_tag.get("href") if link_tag else ""

            if any(k in summary.lower() for k in KEYWORDS):
                all_jobs.append({
                    "Title": title,
                    "Company": company,
                    "Location": location,
                    "Summary": summary,
                    "Link": link
                })

    return all_jobs


def save_jobs(jobs):
    df = pd.DataFrame(jobs)
    df.to_excel("jobs_output.xlsx", index=False)


def send_email(jobs):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL, PASSWORD)

    for recruiter in RECRUITERS:
        msg = MIMEMultipart()
        msg['From'] = EMAIL
        msg['To'] = recruiter
        msg['Subject'] = "Application for Operations Role with Visa Sponsorship"

        body = f"""
Dear Hiring Manager,

I am interested in opportunities in operations/logistics with visa sponsorship.

Attached are relevant job matches:
{jobs[:3]}

Regards,
Venkateshwarlu
"""

        msg.attach(MIMEText(body, 'plain'))
        server.send_message(msg)

    server.quit()

# ---------------------------
# SETUP:
# 1. Enable Gmail App Password
# 2. Replace EMAIL & PASSWORD
# 3. Add more recruiter emails

# ---------------------------
# NEXT UPGRADE (OPTION B READY):
# - Convert to mobile app
# - Add WhatsApp alerts
# - Auto apply using Selenium
# - Cloud deployment (run 24/7)


def upload_to_sheets(jobs):
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope)

    client = gspread.authorize(creds)

    sheet = client.open("Job Automation").sheet1

    for job in jobs:
        sheet.append_row([
            time.strftime("%Y-%m-%d"),
            job["Title"],
            job["Company"],
            job["Location"],
            job["Link"],
            "Yes",
            "New",
            ""
        ])

while True:
    jobs = fetch_jobs()
    save_jobs(jobs)
    send_email(jobs)

    print("Cycle completed. Sleeping...")
    time.sleep(21600)  # runs every 6 hours

if __name__ == "__main__":
    print("Fetching jobs...")
    jobs = fetch_jobs()
    print(f"Found {len(jobs)} jobs")

    save_jobs(jobs)
    print("Saved to Excel")

    send_email(jobs)
    print("Emails sent")
