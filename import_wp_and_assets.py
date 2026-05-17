import os
import sys
import subprocess
import xml.etree.ElementTree as ET
import re
import urllib.request
from datetime import datetime

# Auto-install dependencies
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import markdownify
except ImportError:
    install("markdownify")
    import markdownify

try:
    import requests
except ImportError:
    install("requests")
    import requests

try:
    from bs4 import BeautifulSoup
except ImportError:
    install("beautifulsoup4")
    from bs4 import BeautifulSoup

ROOT_DIR = r"c:\恋愛ブログ"
XML_FILE = os.path.join(ROOT_DIR, "thescienceoflove.WordPress.2026-05-16.xml")
PAST_ARTICLES_DIR = os.path.join(ROOT_DIR, "past-articles")
WEBSITE_DIR = os.path.join(ROOT_DIR, "website")
IMAGES_DIR = os.path.join(WEBSITE_DIR, "assets", "images")

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(PAST_ARTICLES_DIR, exist_ok=True)

def download_image(url):
    filename = os.path.basename(urllib.parse.urlparse(url).path)
    # Some URLs might have query strings or bad characters, clean filename
    filename = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
    if not filename:
        filename = "image_" + str(hash(url)) + ".jpg"
    
    local_path = os.path.join(IMAGES_DIR, filename)
    relative_path = f"assets/images/{filename}"
    
    if not os.path.exists(local_path):
        try:
            print(f"Downloading {url} to {local_path}...")
            # Use requests to handle redirects and user-agent
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(url, headers=headers, stream=True)
            if r.status_code == 200:
                with open(local_path, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
            else:
                print(f"Failed to download {url}: {r.status_code}")
                return url # Return original if failed
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return url
    return relative_path

def strip_wp_comments(html):
    # Remove <!-- wp:... --> and <!-- /wp:... -->
    html = re.sub(r'<!--\s*/?wp:[^>]*-->', '', html)
    return html

def parse_xml():
    print("Parsing XML...")
    tree = ET.parse(XML_FILE)
    root = tree.getroot()
    
    # Namespaces
    ns = {
        'wp': 'http://wordpress.org/export/1.2/',
        'content': 'http://purl.org/rss/1.0/modules/content/',
        'dc': 'http://purl.org/dc/elements/1.1/'
    }
    
    for item in root.findall('.//item'):
        post_type_elem = item.find('wp:post_type', ns)
        status_elem = item.find('wp:status', ns)
        
        if post_type_elem is None or status_elem is None:
            continue
            
        post_type = post_type_elem.text
        status = status_elem.text
        
        if status == 'publish' and post_type in ['post', 'page']:
            title = item.find('title').text
            if not title:
                title = "Untitled"
            
            # Use slug for filename if available
            post_name_elem = item.find('wp:post_name', ns)
            slug = post_name_elem.text if post_name_elem is not None and post_name_elem.text else f"page_{title}"
            # Clean slug for filename
            slug = re.sub(r'[^a-zA-Z0-9_\-]', '', slug)
            if not slug:
                slug = "article_" + str(hash(title))
            
            filename = f"{slug}.md"
            filepath = os.path.join(PAST_ARTICLES_DIR, filename)
            
            content_elem = item.find('content:encoded', ns)
            raw_html = content_elem.text if content_elem is not None else ""
            
            pub_date_elem = item.find('wp:post_date', ns)
            pub_date = pub_date_elem.text if pub_date_elem is not None else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            categories = []
            for cat in item.findall('category[@domain="category"]'):
                categories.append(cat.text)
            
            if not categories:
                categories = ['コラム']
                
            print(f"Processing: {title} ({filename})")
            
            # Clean HTML
            clean_html = strip_wp_comments(raw_html)
            
            # Parse with BS4 to find images
            soup = BeautifulSoup(clean_html, 'html.parser')
            for img in soup.find_all('img'):
                src = img.get('src')
                if src and src.startswith('http'):
                    new_src = download_image(src)
                    img['src'] = new_src
            
            # Convert to Markdown
            md_content = markdownify.markdownify(str(soup), heading_style="ATX")
            
            # Create YAML Frontmatter
            frontmatter = f"---\ntitle: {title}\ndate: {pub_date}\ncategory: {categories[0]}\ndescription: {title}についての記事です。\n---\n\n"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(frontmatter + md_content)
                
            print(f"Saved: {filepath}")

if __name__ == "__main__":
    parse_xml()
    print("Extraction complete!")
