import json
import os
import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pytrends.request import TrendReq

# 1. Configuration
GEO_REGION = 'DE-NW' 
SEED_KEYWORDS = ['aquafacial', 'wimpernlifting', 'nageldesign', 'brautmakeup']
JSON_FILE = 'seo_targets.json'

# Use the Google AI Studio Gemini API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# Using Gemini 1.5 Flash for high speed and strict JSON compliance
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# Setup robust network session with automatic retries for DNS/network blips
session = requests.Session()
retries = Retry(total=5, backoff_factor=2, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

def get_rising_trends():
    """Scrapes Google Trends with anti-rate-limit delays and custom User-Agent."""
    # Use a real browser User-Agent and built-in retries to bypass 429 errors
    pytrend = TrendReq(
        hl='de-DE', 
        tz=360, 
        retries=3, 
        backoff_factor=5,
        requests_args={'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}}
    )
    new_trends = []
    
    for keyword in SEED_KEYWORDS:
        try:
            pytrend.build_payload(kw_list=[keyword], geo=GEO_REGION, timeframe='today 3-m')
            related_queries = pytrend.related_queries()
            
            if related_queries and keyword in related_queries and related_queries[keyword]['rising'] is not None:
                rising_df = related_queries[keyword]['rising']
                
                for index, row in rising_df.iterrows():
                    val = row['value']
                    if val == 'Breakout':
                        new_trends.append(row['query'])
                    else:
                        try:
                            if int(val) >= 150:
                                new_trends.append(row['query'])
                        except ValueError:
                            pass
            
            # Randomized long sleep to mimic human behavior and avoid bans
            sleep_time = random.randint(10, 25)
            time.sleep(sleep_time)
            
        except Exception as e:
            print(f"Error fetching trends for {keyword}: {e}")
            time.sleep(30) # Heavy sleep penalty on error before trying the next keyword
            
    return list(set(new_trends))

def generate_seo_content(keyword):
    """Uses Gemini 1.5 Flash to generate structured JSON SEO copy with SOTA FAQs."""
    
    prompt = f"""You are an expert SEO copywriter for a premium beauty atelier in Düsseldorf.
A new trending local search term is: "{keyword}".
Generate a JSON object with strictly these keys:
- "slug": URL-friendly slug based on the keyword and "duesseldorf"
- "page_title": Premium SEO title (max 60 chars) including the keyword and "Düsseldorf"
- "meta_description": Professional German meta description (max 155 chars)
- "h1": A high-end H1 tag for the landing page.
- "faqs": An array of 3 highly relevant, localized FAQ objects (each with a 'question' and 'answer' in German) to build 2026-compliant SOTA content."""

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "response_mime_type": "application/json" # This forces Gemini to output flawless JSON without markdown blocks
        }
    }

    try:
        # Use the robust session instead of standard requests.post
        response = session.post(GEMINI_API_URL, json=payload, timeout=30)
        response.raise_for_status()
        output = response.json()
        
        # Extract the pure JSON string from Gemini's response
        json_text = output['candidates'][0]['content']['parts'][0]['text']
        return json.loads(json_text)
        
    except Exception as e:
        print(f"Failed to parse Gemini output for {keyword}. Error: {e}")
        return None

# 2. Execution
if __name__ == "__main__":
    print("Checking for new breakout and rising trends (>150%) in NRW...")
    rising_trends = get_rising_trends()
    
    if not rising_trends:
        print("No new rising trends today.")
        exit(0)
        
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        existing_data = json.load(f)
    
    existing_slugs = {item.get("slug") for item in existing_data}
    added_new = False
    
    for trend in rising_trends:
        # Prevent duplicates based on the first word of the trend
        if any(trend.split()[0] in slug for slug in existing_slugs):
            continue
            
        print(f"Found new rising trend: {trend}. Generating SEO copy via Gemini...")
        new_block = generate_seo_content(trend)
        
        if new_block and new_block.get("slug") and new_block["slug"] not in existing_slugs:
            existing_data.append(new_block)
            existing_slugs.add(new_block["slug"])
            added_new = True
            print(f"Added: {new_block['slug']}")
            
    if added_new:
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        print(f"Successfully updated {JSON_FILE}")
