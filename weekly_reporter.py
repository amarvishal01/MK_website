import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 1. Configuration
SITE_URL = "sc-domain:mobinashahri.de"  # Use "https://mobinashahri.de/" if you verified via URL prefix
RECIPIENT_EMAIL = "Mobina.shahri@web.de"
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD")

# 2. Authenticate Headless Bot
creds_json = json.loads(os.environ.get("GCP_CREDENTIALS"))
credentials = service_account.Credentials.from_service_account_info(
    creds_json, scopes=['https://www.googleapis.com/auth/webmasters.readonly']
)
service = build('searchconsole', 'v1', credentials=credentials)

# 3. Calculate Date Range (Last 7 Days)
# GSC data has a standard 3-day processing lag, so we offset the window
today = datetime.today()
end_date = (today - timedelta(days=3)).strftime('%Y-%m-%d') 
start_date = (today - timedelta(days=10)).strftime('%Y-%m-%d')

# 4. Query Search Console API
request = {
    'startDate': start_date,
    'endDate': end_date,
    'dimensions': ['page'],
    'rowLimit': 25 # Top 25 pages
}

try:
    response = service.searchanalytics().query(siteUrl=SITE_URL, body=request).execute()
    rows = response.get('rows', [])
except Exception as e:
    print(f"API Error: {e}")
    rows = []

# 5. Build the HTML Email
html_content = f"""
<div style="font-family: Arial, sans-serif; color: #333;">
    <h2 style="color: #B4A284;">Weekly SEO Traffic Report</h2>
    <p>Performance from <b>{start_date}</b> to <b>{end_date}</b>.</p>
    <table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%; text-align: left;">
      <tr style="background-color: #f8f8f8;">
        <th>Landing Page</th><th>Clicks</th><th>Impressions</th><th>CTR</th><th>Position</th>
      </tr>
"""

for row in rows:
    page = row['keys'][0].replace('https://mobinashahri.de', '')
    clicks = row['clicks']
    impressions = row['impressions']
    ctr = f"{row['ctr'] * 100:.1f}%"
    position = f"{row['position']:.1f}"
    html_content += f"<tr><td>{page}</td><td>{clicks}</td><td>{impressions}</td><td>{ctr}</td><td>{position}</td></tr>"

html_content += """
    </table>
    <p style="margin-top:20px; font-size: 12px; color: #777;">Automated via GitHub Actions & Google Search Console API</p>
</div>
"""

# 6. Send the Email
msg = MIMEMultipart()
msg['From'] = f"SEO Bot <{SENDER_EMAIL}>"
msg['To'] = RECIPIENT_EMAIL
msg['Subject'] = "📈 MS Cosmetics: Weekly SEO Performance Report"
msg.attach(MIMEText(html_content, 'html'))

try:
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
    print("Weekly report sent successfully!")
except Exception as e:
    print(f"Email failed to send: {e}")
