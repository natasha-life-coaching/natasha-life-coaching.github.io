#!/usr/bin/env python3
"""
Script to extract content from a Wix website using Playwright
"""
import asyncio
import json
from playwright.async_api import async_playwright

async def extract_wix_content(url: str) -> dict:
    """Extract all text content from a Wix site"""

    content = {
        'url': url,
        'sections': [],
        'all_text': [],
        'headings': [],
        'paragraphs': [],
        'images': [],
        'links': []
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print(f"Loading {url}...")
        await page.goto(url, wait_until='networkidle', timeout=60000)

        # Wait for content to load
        await page.wait_for_timeout(5000)

        # Scroll to load lazy content
        await page.evaluate('''async () => {
            await new Promise((resolve) => {
                let totalHeight = 0;
                const distance = 300;
                const timer = setInterval(() => {
                    const scrollHeight = document.body.scrollHeight;
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    if(totalHeight >= scrollHeight){
                        clearInterval(timer);
                        resolve();
                    }
                }, 100);
            });
        }''')

        await page.wait_for_timeout(2000)

        # Extract headings
        headings = await page.query_selector_all('h1, h2, h3, h4, h5, h6')
        for h in headings:
            text = await h.inner_text()
            tag = await h.evaluate('el => el.tagName')
            if text.strip():
                content['headings'].append({'tag': tag, 'text': text.strip()})

        # Extract paragraphs and spans with text
        text_elements = await page.query_selector_all('p, span, div')
        seen_text = set()
        for el in text_elements:
            text = await el.inner_text()
            text = text.strip()
            # Filter out very short text, duplicates, and common UI elements
            if text and len(text) > 20 and text not in seen_text:
                if not any(skip in text.lower() for skip in ['cookie', 'privacy policy', 'terms of', 'made with wix']):
                    content['paragraphs'].append(text)
                    seen_text.add(text)

        # Extract images
        images = await page.query_selector_all('img')
        for img in images:
            src = await img.get_attribute('src')
            alt = await img.get_attribute('alt')
            if src and 'wix' in src.lower():
                content['images'].append({'src': src, 'alt': alt})

        # Extract navigation links
        links = await page.query_selector_all('a[href]')
        for link in links:
            href = await link.get_attribute('href')
            text = await link.inner_text()
            if href and text.strip() and 'nylifecoach' in str(href):
                content['links'].append({'href': href, 'text': text.strip()})

        # Get all visible text content
        all_text = await page.inner_text('body')
        content['all_text'] = all_text

        await browser.close()

    return content

async def main():
    base_url = "https://nylifecoach4u.wixsite.com/nylifecoaching"

    pages_to_scrape = [
        base_url,
        base_url + "/about-me",
        base_url + "/testimonials",
        base_url + "/services",
        base_url + "/contact",
    ]

    all_content = {}

    for url in pages_to_scrape:
        try:
            print(f"\n{'='*60}")
            print(f"Scraping: {url}")
            print('='*60)
            content = await extract_wix_content(url)
            all_content[url] = content

            print(f"\nFound {len(content['headings'])} headings")
            print(f"Found {len(content['paragraphs'])} text blocks")
            print(f"Found {len(content['images'])} images")

            print("\n--- HEADINGS ---")
            for h in content['headings'][:20]:
                print(f"  [{h['tag']}] {h['text'][:100]}")

            print("\n--- TEXT CONTENT ---")
            for p in content['paragraphs'][:30]:
                print(f"  - {p[:150]}...")

        except Exception as e:
            print(f"Error scraping {url}: {e}")

    # Save to JSON
    with open('wix_content.json', 'w', encoding='utf-8') as f:
        json.dump(all_content, f, indent=2, ensure_ascii=False)

    print(f"\n\nContent saved to wix_content.json")

    return all_content

if __name__ == "__main__":
    asyncio.run(main())
