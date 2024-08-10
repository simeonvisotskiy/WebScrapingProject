import sys
import time
import uuid
from playwright.sync_api import sync_playwright
import os

def take_screenshots(page, url, unique_id, screenshots_dir, part_prefix):
    total_height = page.evaluate("document.body.scrollHeight")
    viewport_height = page.evaluate("window.innerHeight")

    num_screenshots = total_height // viewport_height + 1
    screenshots = []
    for i in range(num_screenshots):
        screenshot_id = str(uuid.uuid4())
        file_path = os.path.join(screenshots_dir, f"{unique_id}_{screenshot_id}_{part_prefix}{i + 1}.png")
        page.screenshot(path=file_path)
        screenshots.append((url, part_prefix, file_path))
        print(f"Screenshot:|{screenshot_id}|{url}|{part_prefix}|{file_path}|{i + 1}")

        if i < num_screenshots - 1:
            page.evaluate(f"window.scrollBy(0, {viewport_height})")
            time.sleep(0.5)
    return screenshots

def crawl_and_screenshot(url, num_links, unique_id, screenshots_dir):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        all_screenshots = []

        all_screenshots.extend(take_screenshots(page, url, unique_id, screenshots_dir, "part"))

        links = page.eval_on_selector_all('a', 'elements => elements.map(e => e.href)')
        visited_links = set([url])
        count = 0

        for link in links:
            if link not in visited_links and count < int(num_links):
                page.goto(link)
                all_screenshots.extend(take_screenshots(page, link, unique_id, screenshots_dir, "link"))
                visited_links.add(link)
                count += 1

        browser.close()
        return all_screenshots

if __name__ == "__main__":
    crawl_and_screenshot(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
