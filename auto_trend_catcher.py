import json
import os
import time
import requests
from pytrends.request import TrendReq

# 1. Configuration
GEO_REGION = 'DE-NW' 
SEED_KEYWORDS = ['aquafacial', 'wimpernlifting', 'nageldesign', 'brautmakeup']
JSON_FILE = 'seo_targets.json'
HF_TOKEN = os.environ.get("HF_TOKEN")
# Using Zephyr-7b as it is exceptionally fast and reliable on the free tier for JSON formatting
HF_API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"

def get_breakout_trends():
    """Scrapes Google Trends for breakout queries related to seed keywords."""
    pytrend = TrendReq(hl='de-DE', tz=360)
    new_trends = []
    
    for keyword in SEED_KEYWORDS:
        try:
            pytrend.build_payload(kw_list=[keyword], geo=GEO_REGION, timeframe='today 3-m')
            related_queries = pytrend.related_queries()
            
            if related_queries and keyword in related_queries and related_queries[keyword]['rising'] is not None:
                rising_df = related_queries[keyword]['rising']
                breakouts = rising_df[rising_df['value'] == 'Breakout']['query'].tolist()
                new_trends.extend(breakouts)
            time.sleep(2) 
        except Exception as e:
            print(f"Error fetching trends for {keyword}: {e}")
            
    return list(set(new_trends))

def generate_seo_content(keyword):
    """Uses Hugging Face open-source LLM to generate German SEO copy."""
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    prompt = f"""<|system|>
You are an expert SEO copywriter for a premium beauty atelier in Düsseldorf. Output ONLY valid JSON. No markdown, no explanations.</s>
<|user|>
A new trending local search term is: "{keyword}".
Generate a JSON object with strictly these keys:
- "slug": URL-friendly slug based on the keyword and "duesseldorf"
- "page_title": Premium SEO title (max 60 chars) including the keyword and "Düsseldorf"
- "meta_description": Professional German meta description (max 155 chars)
- "h1": A high-end H1 tag for the landing page.</s>
<|assistant|>
{{"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 250,
            "temperature": 0.1,
            "return_full_text": False
        }
    }

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        output_text = response.json()[0]['generated_text']
        
        # Re-attach the opening brace stripped by the prompt priming
        clean_json = "{" + output_text.strip().removeprefix('```json').removesuffix('```').strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"Failed to parse AI output for {keyword}. Error: {e}")
        return None

# 2. Execution
if __name__ == "__main__":
    print("Checking for new local beauty trends in NRW...")
    breakouts = get_breakout_trends()
    
    if not breakouts:
        print("No new breakouts today.")
        exit(0)
        
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        existing_data = json.load(f)
    
    existing_slugs = {item.get("slug") for item in existing_data}
    added_new = False
    
    for trend in breakouts:
        if any(trend.split()[0] in slug for slug in existing_slugs):
            continue
            
        print(f"Found new breakout trend: {trend}. Generating SEO copy via Hugging Face...")
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
