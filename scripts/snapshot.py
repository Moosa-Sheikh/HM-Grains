"""Archive the public pages and their same-origin static dependencies.

Run intentionally: upstream content changes should be reviewed before replacing local pages.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from html import unescape
from pathlib import Path
from urllib.parse import urlparse
import re
import subprocess

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://hmgrains.com'
PAGES = {
    '': ROOT / 'index.html',
    'about/': ROOT / 'about/index.html',
    'contact/': ROOT / 'contact/index.html',
    'hello-world/': ROOT / 'hello-world/index.html',
}


def fetch(url):
    return subprocess.check_output(['curl', '-fsSL', '--retry', '2', url], timeout=90)


def resource_paths(text):
    text = unescape(text.replace('\\/', '/'))
    matches = re.findall(r'(?:https?:)?//(?:hmgrains\.com|blue-eel-593949\.hostingersite\.com)/((?:wp-content|wp-includes)/[^\s"\'<>\\)]+)', text)
    return {urlparse('/' + item).path.lstrip('/') for item in matches}


def save_asset(path):
    dest = ROOT / path
    if dest.exists():
        return path, dest.read_bytes() if dest.suffix == '.css' else b''
    try:
        data = fetch(SITE + '/' + path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return path, data if dest.suffix == '.css' else b''
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print('Skipped', path, exc)
        return path, b''


def main():
    paths = set()
    for slug, dest in PAGES.items():
        html = fetch(SITE + '/' + slug).decode('utf-8')
        paths |= resource_paths(html)
        # The old HTML references are converted to local paths. The content and
        # Elementor classes are retained for visual fidelity.
        html = html.replace(SITE + '/', '/').replace('//hmgrains.com/', '/')
        html = html.replace('https:\\/\\/hmgrains.com\\/', '\\/')
        html = re.sub(r'<meta name="generator"[^>]*>', '', html)
        html = re.sub(r'(<link rel="canonical" href=")/([^"]*)', lambda m: m.group(1) + SITE + '/' + m.group(2), html)
        # Cloudflare obfuscated mailto links cannot work without its server.
        html = re.sub(r'href="/cdn-cgi/l/email-protection#[^"]*"', 'href="mailto:contact@hmgrains.com"', html)
        html = re.sub(r'<span class="__cf_email__"[^>]*>.*?</span>', 'contact@hmgrains.com', html)
        html = re.sub(r'<a href="/cdn-cgi/l/email-protection" class="__cf_email__"[^>]*>.*?</a>', '<a href="mailto:contact@hmgrains.com">contact@hmgrains.com</a>', html)
        html = re.sub(r'<script[^>]+src=["\']/cdn-cgi/scripts/[^>]*></script>', '', html)
        html = re.sub(r'<link[^>]+(?:/wp-json/|/feed/|/comments/feed/|xmlrpc\.php)[^>]*>', '', html)
        if slug == 'contact/':
            html = re.sub(r'<form id="wpforms-form-16".*?</form>', '''<form id="wpforms-form-16" class="wpforms-form" method="post" action="/contact/submit.php">
<div class="wpforms-field-container">
<div class="wpforms-field" style="position:absolute;left:-9999px" aria-hidden="true"><label for="website">Website</label><input id="website" name="website" tabindex="-1" autocomplete="off"></div>
<div class="wpforms-field"><label class="wpforms-field-label" for="contact-name">Name <span class="wpforms-required-label">*</span></label><input class="wpforms-field-large" id="contact-name" name="name" required maxlength="120" autocomplete="name"></div>
<div class="wpforms-field"><label class="wpforms-field-label" for="contact-email">Email <span class="wpforms-required-label">*</span></label><input class="wpforms-field-large" id="contact-email" name="email" type="email" required maxlength="254" autocomplete="email"></div>
<div class="wpforms-field"><label class="wpforms-field-label" for="contact-phone">Phone <span class="wpforms-required-label">*</span></label><input class="wpforms-field-large" id="contact-phone" name="phone" type="tel" required maxlength="50" autocomplete="tel"></div>
<div class="wpforms-field"><label class="wpforms-field-label" for="contact-message">Message</label><textarea class="wpforms-field-medium" id="contact-message" name="message" maxlength="10000"></textarea></div>
</div><div class="wpforms-submit-container"><button type="submit" class="wpforms-submit">Submit</button></div></form>''', html, count=1, flags=re.S)
            # WordPress Forms' AJAX handler expects wp-admin; use normal PHP form submission.
            html = re.sub(r'<script[^>]+src=["\'][^"\']*wpforms[^>]*></script>', '', html)
            html = re.sub(r'<script[^>]*id=["\'][^"\']*wpforms[^>]*>.*?</script>', '', html, flags=re.S)
            html = re.sub(r'<script type=["\']text/javascript["\']>\s*/\* <!...*?var wpforms_settings.*?</script>', '', html, flags=re.S)
        html = html.replace('</head>', '<link rel="stylesheet" href="/assets/site.css">\n</head>', 1)
        html = html.replace('</body>', '<script defer src="/assets/site.js"></script>\n</body>', 1)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding='utf-8')
        print('Saved', slug or '/')

    # Elementor loads these widget modules dynamically rather than via HTML tags.
    paths |= {
        'wp-content/plugins/elementor/assets/js/chunks/' + name + '.min.js'
        for name in ('background-slideshow', 'background-video', 'text-editor',
                     'section-stretched-section', 'counter', 'toggle')
    }
    for css in (ROOT / 'wp-content').rglob('*.css'):
        paths |= resource_paths(css.read_text(encoding='utf-8', errors='replace'))

    # CSS refers to font files and background images using relative URLs.
    # Download those alongside the stylesheets at the same paths.
    while paths:
        batch = list(paths)
        paths.clear()
        with ThreadPoolExecutor(max_workers=12) as pool:
            futures = {pool.submit(save_asset, p): p for p in batch if not (ROOT / p).exists()}
            for future in as_completed(futures):
                path, css = future.result()
                if not css:
                    continue
                text = css.decode('utf-8', errors='replace')
                paths |= resource_paths(text)
                base = (ROOT / path).parent
                for item in re.findall(r'url\(\s*["\']?([^\)"\']+)', text):
                    item = unescape(item.strip())
                    if item.startswith(('data:', '#')):
                        continue
                    if item.startswith(('http:', 'https:', '//')):
                        continue
                    dest = (base / urlparse(item).path).resolve()
                    if dest.is_relative_to(ROOT) and not dest.exists():
                        paths.add(str(dest.relative_to(ROOT)))
    for css in (ROOT / 'wp-content').rglob('*.css'):
        text = css.read_text(encoding='utf-8', errors='replace')
        updated = (text.replace(SITE + '/', '/').replace('//hmgrains.com/', '/')
                   .replace('https://blue-eel-593949.hostingersite.com/', '/'))
        if updated != text:
            css.write_text(updated, encoding='utf-8')
    print('Snapshot complete')


if __name__ == '__main__':
    main()
