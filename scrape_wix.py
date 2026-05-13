#!/usr/bin/env python3
"""
Improved Wix Scraper - waits for JS to load and extracts all visible text
"""
import asyncio
import json
import re
from playwright.async_api import async_playwright

async def scrape_page(page, url, page_name):
    """Scrape a single page and return its content"""
    print(f"\n{'='*60}")
    print(f"Scraping: {page_name} ({url})")
    print('='*60)

    try:
        # Navigate and wait for network to be idle
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)

        # Wait extra time for Wix JS to render
        await page.wait_for_timeout(5000)

        # Scroll down to trigger lazy loading
        for i in range(5):
            await page.evaluate(f'window.scrollTo(0, {i * 500})')
            await page.wait_for_timeout(500)

        # Scroll back to top
        await page.evaluate('window.scrollTo(0, 0)')
        await page.wait_for_timeout(1000)

        # Check if it's a 404 page
        page_content = await page.content()
        if '404' in page_content and 'PAGE NOT FOUND' in page_content:
            print(f"  [SKIP] Page not found: {url}")
            return None

        # Get the page title
        title = await page.title()
        print(f"  Title: {title}")

        # Extract all visible text from the main content area
        all_text = await page.evaluate('''() => {
            // Get all text content, excluding scripts and styles
            const walker = document.createTreeWalker(
                document.body,
                NodeFilter.SHOW_TEXT,
                {
                    acceptNode: function(node) {
                        const parent = node.parentElement;
                        if (!parent) return NodeFilter.FILTER_REJECT;
                        const tag = parent.tagName.toLowerCase();
                        if (['script', 'style', 'noscript'].includes(tag)) {
                            return NodeFilter.FILTER_REJECT;
                        }
                        const text = node.textContent.trim();
                        if (text.length < 3) return NodeFilter.FILTER_REJECT;
                        return NodeFilter.FILTER_ACCEPT;
                    }
                }
            );

            const texts = [];
            while (walker.nextNode()) {
                const text = walker.currentNode.textContent.trim();
                if (text && !texts.includes(text)) {
                    texts.push(text);
                }
            }
            return texts;
        }''')

        # Get headings
        headings = await page.evaluate('''() => {
            const headings = [];
            document.querySelectorAll('h1, h2, h3, h4').forEach(h => {
                const text = h.innerText.trim();
                if (text && text.length > 2) {
                    headings.push({tag: h.tagName, text: text});
                }
            });
            return headings;
        }''')

        # Get paragraphs
        paragraphs = await page.evaluate('''() => {
            const paras = [];
            document.querySelectorAll('p, [data-testid*="richText"], [class*="font_8"], [class*="font_7"]').forEach(p => {
                const text = p.innerText.trim();
                if (text && text.length > 20) {
                    paras.push(text);
                }
            });
            return [...new Set(paras)];
        }''')

        # Get images
        images = await page.evaluate('''() => {
            const imgs = [];
            document.querySelectorAll('img').forEach(img => {
                if (img.src && img.src.includes('wix')) {
                    imgs.push({
                        src: img.src,
                        alt: img.alt || ''
                    });
                }
            });
            return imgs;
        }''')

        # Get links to other pages on the site
        links = await page.evaluate('''() => {
            const links = [];
            document.querySelectorAll('a[href]').forEach(a => {
                const href = a.href;
                const text = a.innerText.trim();
                if (href && href.includes('nylifecoach') && text) {
                    links.push({href, text});
                }
            });
            return links;
        }''')

        result = {
            'url': url,
            'page_name': page_name,
            'title': title,
            'headings': headings,
            'paragraphs': paragraphs,
            'all_text': all_text,
            'images': images,
            'links': links
        }

        print(f"  Found {len(headings)} headings, {len(paragraphs)} paragraphs, {len(images)} images")

        # Print key content
        print("\n  --- HEADINGS ---")
        for h in headings[:10]:
            print(f"    [{h['tag']}] {h['text'][:80]}")

        print("\n  --- PARAGRAPHS ---")
        for p in paragraphs[:10]:
            clean = p.replace('\n', ' ')[:100]
            print(f"    - {clean}...")

        return result

    except Exception as e:
        print(f"  [ERROR] {e}")
        return None

async def main():
    base_url = "https://nylifecoach4u.wixsite.com/nylifecoaching"

    all_content = {}

    async with async_playwright() as p:
        # Launch browser with larger viewport
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()

        # First, scrape the home page to find all navigation links
        print("\n" + "="*60)
        print("STEP 1: Finding all pages on the site")
        print("="*60)

        await page.goto(base_url, wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(5000)

        # Find all navigation links
        nav_links = await page.evaluate('''() => {
            const links = new Set();
            document.querySelectorAll('nav a, [data-testid*="linkElement"], a[href*="nylifecoach"]').forEach(a => {
                const href = a.href;
                if (href && href.includes('nylifecoach') && !href.includes('#')) {
                    links.add(href);
                }
            });
            return Array.from(links);
        }''')

        print(f"Found {len(nav_links)} pages to scrape:")
        for link in nav_links:
            print(f"  - {link}")

        # Scrape each page
        print("\n" + "="*60)
        print("STEP 2: Scraping all pages")
        print("="*60)

        # Always include base URL
        pages_to_scrape = [base_url] + [l for l in nav_links if l != base_url]

        for url in pages_to_scrape:
            # Determine page name from URL
            if url == base_url or url.endswith('/nylifecoaching'):
                page_name = 'home'
            else:
                page_name = url.split('/')[-1] or 'home'

            content = await scrape_page(page, url, page_name)
            if content:
                all_content[page_name] = content

        await browser.close()

    # Save to JSON
    with open('wix_content.json', 'w', encoding='utf-8') as f:
        json.dump(all_content, f, indent=2, ensure_ascii=False)

    print("\n" + "="*60)
    print("EXTRACTION COMPLETE")
    print("="*60)
    print(f"Scraped {len(all_content)} pages")
    print("Content saved to wix_content.json")

    # Print summary of all extracted content
    print("\n" + "="*60)
    print("CONTENT SUMMARY")
    print("="*60)

    for page_name, content in all_content.items():
        print(f"\n[{page_name.upper()}]")
        print(f"  Headings: {len(content['headings'])}")
        print(f"  Paragraphs: {len(content['paragraphs'])}")
        print(f"  Images: {len(content['images'])}")

        # Print actual content
        if content['paragraphs']:
            print("  Content preview:")
            for p in content['paragraphs'][:3]:
                clean = p.replace('\n', ' ')[:80]
                print(f"    \"{clean}...\"")

    return all_content

if __name__ == "__main__":
    asyncio.run(main())
