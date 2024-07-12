import sys
import time
import uuid
from playwright.sync_api import sync_playwright
import os

def main(url, num_links, unique_id, screenshots_dir):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        try:
            # Get the total height of the page
            total_height = page.evaluate("document.body.scrollHeight")
            viewport_height = page.evaluate("window.innerHeight")

            num_screenshots = total_height // viewport_height + 1
            for i in range(num_screenshots):
                screenshot_id = str(uuid.uuid4())
                file_path = os.path.join(screenshots_dir, f"{unique_id}_{screenshot_id}_part{i + 1}.png")
                page.screenshot(path=file_path)
                print(f"Screenshot:|{screenshot_id}|{url}|part|{file_path}|{i + 1}")

                if i < num_screenshots - 1:
                    page.evaluate(f"window.scrollBy(0, {viewport_height})")
                    time.sleep(0.5)  # Allow time for the scroll action

            # Crawling and taking screenshots of first num_links links
            links = page.eval_on_selector_all('a', 'elements => elements.map(e => e.href)')
            visited_links = set()
            visited_links.add(url)

            count = 0
            for link in links:
                if link not in visited_links:
                    link_screenshot_id = str(uuid.uuid4())
                    page.goto(link)

                    total_height = page.evaluate("document.body.scrollHeight")
                    viewport_height = page.evaluate("window.innerHeight")

                    num_screenshots = total_height // viewport_height + 1
                    for i in range(num_screenshots):
                        link_file_path = os.path.join(screenshots_dir, f"{unique_id}_{link_screenshot_id}_part{i + 1}.png")
                        page.screenshot(path=link_file_path)
                        print(f"Screenshot:|{link_screenshot_id}|{link}|link|{link_file_path}|{i + 1}")

                        if i < num_screenshots - 1:
                            page.evaluate(f"window.scrollBy(0, {viewport_height})")
                            time.sleep(0.5)

                    visited_links.add(link)
                    count += 1
                    if count >= int(num_links):
                        break
        except Exception as e:
            print(f"Error: {e}")
            print("Not scrapable")
        finally:
            browser.close()

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
