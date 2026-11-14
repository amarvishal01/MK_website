import json
import os
from bs4 import BeautifulSoup

# 1. Setup Directories
OUTPUT_DIR = "services"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 2. Load the Template and Data
with open("index.html", "r", encoding="utf-8") as f:
    template_html = f.read()

with open("seo_targets.json", "r", encoding="utf-8") as f:
    targets = json.load(f)

# 3. Generate the Pages
for target in targets:
    soup = BeautifulSoup(template_html, "html.parser")
    
    # Inject SEO Data
    if soup.title:
        soup.title.string = target["page_title"]
        
    meta_desc = soup.find("meta", {"name": "description"})
    if meta_desc:
        meta_desc["content"] = target["meta_description"]
        
    # Overwrite the main Hero Title for relevance
    h1_tag = soup.find("h1", id="hero-title")
    if h1_tag:
        h1_tag.string = target["h1"]
        
    # Remove the Hero carousel to make the landing page faster and more focused
    carousel = soup.find("section", id="hero-carousel")
    if carousel:
        carousel.decompose()

    # 4. Save the new page
    output_path = os.path.join(OUTPUT_DIR, f"{target['slug']}.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(str(soup))
        
    print(f"Generated: {output_path}")
