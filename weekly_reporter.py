import os
import json
import smtplib
import re 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

# 1. Configuration
SITE_URL = "sc-domain:mobinashahri.de" 
GA4_PROPERTY_ID = "240417284" # <-- Paste your numeric GA4 Property ID here
RECIPIENT_EMAIL = "amarvishal01@gmail.com"
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD")

# 2. Authenticate
creds_json = json.loads(os.environ.get("GCP_CREDENTIALS"))
gsc_credentials = service_account.Credentials.from_service_account_info(
    creds_json, scopes=['https://www.googleapis.com/auth/webmasters.readonly']
)
ga4_credentials = service_account.Credentials.from_service_account_info(creds_json)

gsc_service = build('searchconsole', 'v1', credentials=gsc_credentials)
ga4_client = BetaAnalyticsDataClient(credentials=ga4_credentials)

# 3. Calculate Dates
today = datetime.today()
end_date = (today - timedelta(days=3)).strftime('%Y-%m-%d') 
start_date = (today - timedelta(days=10)).strftime('%Y-%m-%d')

# 4. Pull Google Search Console Data
gsc_request = {
    'startDate': start_date,
    'endDate': end_date,
    'dimensions': ['page'],
    'rowLimit': 50
}
try:
    gsc_response = gsc_service.searchanalytics().query(siteUrl=SITE_URL, body=gsc_request).execute()
    gsc_rows = gsc_response.get('rows', [])
except Exception as e:
    print(f"GSC API Error: {e}")
    gsc_rows = []


combined_data = {}
for row in gsc_rows:
    # These lines MUST be indented by 4 spaces
    page = re.sub(r'^https?://(www\.)?mobinashahri\.de', '', row['keys'][0])
    if not page.startswith('/'): page = '/' + page
    
    combined_data[page] = {
        'clicks': row['clicks'],
        'impressions': row['impressions'],
        'position': f"{row['position']:.1f}",
        'views': '0', 'bounce_rate': 'N/A', 'avg_time': 'N/A'
    }

# 5. Pull Google Analytics 4 Data
try:
    ga4_request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[Dimension(name="pagePath")],
        metrics=[
            Metric(name="screenPageViews"),
            Metric(name="bounceRate"),
            Metric(name="averageSessionDuration")
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
    )
    ga4_response = ga4_client.run_report(ga4_request)
    
    for row in ga4_response.rows:
        page = row.dimension_values[0].value
        if page in combined_data:
            combined_data[page]['views'] = row.metric_values[0].value
            combined_data[page]['bounce_rate'] = f"{float(row.metric_values[1].value) * 100:.1f}%"
            combined_data[page]['avg_time'] = f"{float(row.metric_values[2].value):.1f}s"
except Exception as e:
    print(f"GA4 API Error: {e}")

# 6. Build HTML Email
html_content = f"""
<div style="font-family: Arial, sans-serif; color: #333;">
    <h2 style="color: #B4A284;">Weekly SEO & Traffic Report</h2>
    <p>Performance from <b>{start_date}</b> to <b>{end_date}</b>.</p>
    <table border="1" cellpadding="8" style="border-collapse: collapse; width: 100%; text-align: left; font-size: 13px;">
      <tr style="background-color: #f8f8f8;">
        <th>Landing Page</th><th>GSC Clicks</th><th>GSC Impr.</th><th>GSC Pos.</th><th>GA4 Views</th><th>Bounce Rate</th><th>Avg Time</th>
      </tr>
"""

for page, data in combined_data.items():
    html_content += f"<tr><td>{page}</td><td>{data['clicks']}</td><td>{data['impressions']}</td><td>{data['position']}</td><td>{data['views']}</td><td>{data['bounce_rate']}</td><td>{data['avg_time']}</td></tr>"

html_content += """
    </table>
    <p style="margin-top:20px; font-size: 12px; color: #777;">Automated via GitHub Actions (GSC + GA4 API)</p>
</div>
"""

# 7. Send the Email
msg = MIMEMultipart()
msg['From'] = f"SEO Bot <{SENDER_EMAIL}>"
msg['To'] = RECIPIENT_EMAIL
msg['Subject'] = "📈 MS Cosmetics: Weekly SEO & Traffic Report"
msg.attach(MIMEText(html_content, 'html'))

try:
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
    print("Weekly GSC + GA4 report sent successfully!")
except Exception as e:
    print(f"Email failed to send: {e}")
