import xml.etree.ElementTree as ET
import sys

def main():
    try:
        tree = ET.parse('c:\\恋愛ブログ\\thescienceoflove.WordPress.2026-05-16.xml')
        root = tree.getroot()
        ns = {'wp': 'http://wordpress.org/export/1.2/'}
        for item in root.findall('.//item'):
            title = item.find('title').text
            post_type_elem = item.find('wp:post_type', ns)
            post_type = post_type_elem.text if post_type_elem is not None else 'unknown'
            status_elem = item.find('wp:status', ns)
            status = status_elem.text if status_elem is not None else 'unknown'
            print(f"Title: {title}, Type: {post_type}, Status: {status}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
