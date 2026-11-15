import json
import os
import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pytrends.request import TrendReq

# 1. Core Configuration
GEO_REGION = 'DE-NW' 
SEED_KEYWORDS = ['aquafacial', 'wimpernlifting', 'nageldesign', 'brautmakeup']
JSON_FILE = 'seo_targets.json'
MAX_DAILY_PAGES = 3 # Selective Scaling: Prevent crawl budget drain

# 2. SOTA Data Layer (Differentiates every page)
LOCAL_DATA = {
    "business": "MS Cosmetics",
    "owner": "Mobina Shahri",
    "neighborhoods": ["Stadtmitte", "Pempelfort", "Oberkassel", "Carlstadt", "Flingern", "Medienhafen", "Golzheim"],
    "usps": ["Höchste Hygienestandards", "Premium-Produkte", "Individuelle Typberatung"]
}

# 3. Gemini API Setup
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"

session = requests.Session()
retries = Retry(total=5, backoff_factor=2, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

def get_rising_trends():
    """Scrapes Google Trends with manual retries to bypass urllib3 method_whitelist errors."""
    
    # Removed 'retries' and 'backoff_factor' to prevent the pytrends library crash
    pytrend = TrendReq(
        hl='de-DE', 
        tz=360, 
        requests_args={'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}}
    )
    new_trends = []
    
    for keyword in SEED_KEYWORDS:
        success = False
        attempts = 0
        
        # Manual retry loop replaces the broken pytrends internal retry
        while not success and attempts < 3:
            try:
                pytrend.build_payload(kw_list=[keyword], geo=GEO_REGION, timeframe='today 3-m')
                related_queries = pytrend.related_queries()
                
                if related_queries and keyword in related_queries and related_queries[keyword]['rising'] is not None:
                    rising_df = related_queries[keyword]['rising']
                    for index, row in rising_df.iterrows():
                        val = row['value']
                        if val == 'Breakout' or (str(val).isdigit() and int(val) >= 150):
                            new_trends.append(row['query'])
                            
                success = True # Mark as successful to break the retry loop
                time.sleep(random.randint(5, 15))
                
            except Exception as e:
                attempts += 1
                print(f"Trend fetch error for {keyword} (Attempt {attempts}/3): {e}")
                time.sleep(20) # Heavy sleep penalty before retrying
                
    return list(set(new_trends))

def generate_sota_content(keyword):
    """Uses Gemini to generate deep content, JSON-LD Schema, and clustering metadata."""
    
    neighborhood = random.choice(LOCAL_DATA["neighborhoods"])
    usp = random.choice(LOCAL_DATA["usps"])
    
    prompt = f"""You are an elite SEO copywriter for {LOCAL_DATA['business']} (owned by {LOCAL_DATA['owner']}) in Düsseldorf.
A new trending search term is: "{keyword}".

Generate a comprehensive, 2026-compliant SOTA SEO data object in German. 
Integrate this local data naturally: Neighborhood "{neighborhood}" and USP "{usp}".

Output ONLY a JSON object with these exact keys:
- "slug": URL-friendly slug (e.g., keyword-duesseldorf-neighborhood)
- "category": Categorize as ONE of: "skin", "lashes", "nails", "makeup" (for Topic Clustering)
- "page_title": Click-optimized SEO title (max 60 chars)
- "meta_description": Conversion-focused meta description (max 155 chars)
- "h1": High-end H1 tag
- "intro_text": A 2-paragraph highly engaging, locally relevant introduction.
- "faqs": Array of 3 FAQ objects (keys: "question", "answer").
- "schema_markup": A nested valid JSON-LD object for 'FAQPage' schema containing the 3 FAQs to trigger Google AI Overviews.
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3, # Slightly higher for creative variation across local neighborhoods
            "response_mime_type": "application/json"
        }
    }

    try:
        response = session.post(GEMINI_API_URL, json=payload, timeout=40)
        response.raise_for_status()
        output = response.json()
        json_text = output['candidates'][0]['content']['parts'][0]['text']
        return json.loads(json_text)
    except Exception as e:
        print(f"Gemini generation failed for {keyword}: {e}")
        return None

def build_topic_clusters(existing_data):
    """Automates internal linking by grouping pages by category."""
    clusters = {"skin": [], "lashes": [], "nails": [], "makeup": []}
    
    # Group by category
    for page in existing_data:
        cat = page.get("category", "skin")
        if cat in clusters:
            clusters[cat].append({"slug": page["slug"], "title": page["page_title"]})
            
    # Inject related links back into the data
    for page in existing_data:
        cat = page.get("category", "skin")
        related = [p for p in clusters[cat] if p["slug"] != page["slug"]]
        # Keep top 3 related links to avoid spammy footer blocks
        page["internal_links"] = related[:3] 
        
    return existing_data

# 4. Execution Pipeline
if __name__ == "__main__":
    print("Initializing SOTA Trend Hunter (Gemini 3.8 Flash)...")
    
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    else:
        existing_data = []
        
    existing_slugs = {item.get("slug") for item in existing_data}
    rising_trends = get_rising_trends()
    
    pages_generated_today = 0
    added_new = False
    
    for trend in rising_trends:
        if pages_generated_today >= MAX_DAILY_PAGES:
            print(f"Daily generation cap ({MAX_DAILY_PAGES}) reached. Selective scaling enforced.")
            break
            
        if any(trend.split()[0] in slug for slug in existing_slugs):
            continue
            
        print(f"Generating SOTA page for trend: '{trend}'...")
        new_page = generate_sota_content(trend)
        
        if new_page and new_page.get("slug") and new_page["slug"] not in existing_slugs:
            existing_data.append(new_page)
            existing_slugs.add(new_page["slug"])
            pages_generated_today += 1
            added_new = True
            print(f"Success: Added {new_page['slug']} (Category: {new_page.get('category')})")
            
    if added_new:
        # Re-build internal linking structure before saving
        print("Re-calculating Topic Clusters for internal linking...")
        existing_data = build_topic_clusters(existing_data)
        
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        print(f"Pipeline complete. {pages_generated_today} new pages injected into {JSON_FILE}.")
    else:
        print("No new actionable trends found today. Pipeline sleeping.")
