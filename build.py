import os
import glob
import re
import subprocess
import sys

# Ensure markdown library is installed
try:
    import markdown
except ImportError:
    print("Installing markdown library...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown"])
    import markdown

# Directories
ROOT_DIR = r"c:\恋愛ブログ"
WEBSITE_DIR = os.path.join(ROOT_DIR, "website")
PAST_ARTICLES_DIR = os.path.join(ROOT_DIR, "past-articles")
DRAFTS_DIR = os.path.join(ROOT_DIR, "drafts")

# Ensure website directory exists
os.makedirs(WEBSITE_DIR, exist_ok=True)

# HTML Templates
HEADER_HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | The Science of Love</title>
    <meta name="description" content="科学と心理学に基づく恋愛戦略。上級心理カウンセラー如月が解説します。">
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
    <header>
        <div class="nav-container">
            <a href="index.html" class="logo">The Science of <span>Love</span></a>
            <ul class="nav-links">
                <li><a href="index.html">ホーム</a></li>
                <li><a href="about.html">プロフィール</a></li>
                <li><a href="contact.html">お問い合わせ</a></li>
            </ul>
        </div>
    </header>
"""

FOOTER_HTML = """
    <footer>
        <div class="footer-links">
            <a href="privacy.html">プライバシーポリシー・免責事項</a>
            <a href="contact.html">お問い合わせ</a>
        </div>
        <p class="copyright">&copy; 2026 The Science of Love. All Rights Reserved.</p>
    </footer>
</body>
</html>
"""

INDEX_HERO = """
    <section class="hero">
        <h1>恋愛を「科学」する</h1>
        <p>上級心理カウンセラー如月が、進化心理学とデータに基づく再現性の高い恋愛戦略をお届けします。</p>
    </section>
    <main class="container">
        <h2 style="margin-bottom: 2rem; color: var(--accent-gold);">最新の記事</h2>
        <div class="grid">
"""

def extract_title(content, filename):
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return filename.replace('.md', '')

def build_site():
    print("Building static site...")
    
    # Collect markdown files
    md_files = glob.glob(os.path.join(PAST_ARTICLES_DIR, "*.md")) + glob.glob(os.path.join(DRAFTS_DIR, "*.md"))
    
    articles = []
    
    # Convert markdown files to HTML
    for filepath in md_files:
        filename = os.path.basename(filepath)
        html_filename = filename.replace('.md', '.html')
        out_path = os.path.join(WEBSITE_DIR, html_filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        title = extract_title(content, filename)
        
        # Simple Markdown parsing including tables
        html_content = markdown.markdown(content, extensions=['tables', 'fenced_code', 'sane_lists'])
        
        full_html = f"{HEADER_HTML.format(title=title)}\n<main class='container'><article class='article-content'>\n<div class='article-header'><h1>{title}</h1></div>\n{html_content}\n</article></main>\n{FOOTER_HTML}"
        
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
            
        print(f"Generated: {html_filename}")
        
        articles.append({
            'title': title,
            'url': html_filename,
            'category': '恋愛心理学' # Default category for now
        })
        
    # Build index.html
    index_path = os.path.join(WEBSITE_DIR, "index.html")
    index_html = HEADER_HTML.format(title="ホーム") + INDEX_HERO
    
    for article in articles:
        card = f"""
            <div class="card">
                <div class="card-content">
                    <div class="card-category">{article['category']}</div>
                    <h2>{article['title']}</h2>
                    <p>心理学と科学的根拠に基づき、交際経験ゼロから抜け出すための戦略を解説します。</p>
                    <a href="{article['url']}" class="btn">記事を読む</a>
                </div>
            </div>
        """
        index_html += card
        
    index_html += "\n        </div>\n    </main>" + FOOTER_HTML
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)
    print("Generated: index.html")
    
    # Build About page
    about_html = HEADER_HTML.format(title="プロフィール") + """
    <main class="container">
        <article class="article-content">
            <div class="article-header"><h1>プロフィール</h1></div>
            <h2>上級心理カウンセラー 如月</h2>
            <p>はじめまして。上級心理カウンセラーの如月です。</p>
            <p>かつては私自身も「ノウハウコレクター」として様々な恋愛商材を試しては挫折を繰り返していました。しかし、心理学や進化心理学という「科学的根拠」に出会ってから人生が大きく変わりました。</p>
            <p>このブログでは、一部の生まれ持ったイケメンやコミュニケーション達人しか使えないようなテクニックではなく、データと研究に基づいた「再現性の高い戦略」を、30代男性を中心にお届けします。</p>
        </article>
    </main>
    """ + FOOTER_HTML
    with open(os.path.join(WEBSITE_DIR, "about.html"), 'w', encoding='utf-8') as f:
        f.write(about_html)
    print("Generated: about.html")
    
    # Build Contact page
    contact_html = HEADER_HTML.format(title="お問い合わせ") + """
    <main class="container">
        <article class="article-content">
            <div class="article-header"><h1>お問い合わせ</h1></div>
            <p>恋愛に関するご相談、お仕事のご依頼などは以下のフォーム（準備中）よりお願いいたします。</p>
            <p>※現在はメールでのみ受け付けております：contact@example.com</p>
        </article>
    </main>
    """ + FOOTER_HTML
    with open(os.path.join(WEBSITE_DIR, "contact.html"), 'w', encoding='utf-8') as f:
        f.write(contact_html)
    print("Generated: contact.html")
    
    # Build Privacy page
    privacy_html = HEADER_HTML.format(title="プライバシーポリシー") + """
    <main class="container">
        <article class="article-content">
            <div class="article-header"><h1>プライバシーポリシー・免責事項</h1></div>
            <h2>免責事項</h2>
            <p>当サイトに掲載されている情報の正確性には万全を期していますが、利用者が当サイトの情報を用いて行う一切の行為に関して、一切の責任を負わないものとします。</p>
            <p>当サイトはアフィリエイトプログラムにより商品をご紹介致しております。紹介している商品やサービスに関するお問い合わせは、各販売店へ直接お願いいたします。</p>
        </article>
    </main>
    """ + FOOTER_HTML
    with open(os.path.join(WEBSITE_DIR, "privacy.html"), 'w', encoding='utf-8') as f:
        f.write(privacy_html)
    print("Generated: privacy.html")
    
    print("Build complete!")

if __name__ == "__main__":
    build_site()
