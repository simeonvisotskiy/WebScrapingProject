import asyncio
from playwright.async_api import async_playwright
import uuid
import os

async def take_screenshot(url, num_links):
    screenshot_id = str(uuid.uuid4())
    file_path = f"screenshots/{screenshot_id}.png"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        total_height = await page.evaluate("document.body.scrollHeight")
        viewport_height = await page.evaluate("window.innerHeight")

        num_screenshots = total_height // viewport_height + 1
        for i in range(num_screenshots):
            file_path = f"screenshots/{screenshot_id}_part{i+1}.png"
            await page.screenshot(path=file_path)
            print(f"Screenshot part{i+1} of (url) saved to {file_path}")
            if i <num_screenshots - 1:
                await page.evaluate(f"window.scrollBy(0, {viewport_height})")
                await asyncio.sleep(0.5)


        links = await page.locator('a').evaluate_all('elements => elements.map(e => e.href)')
        visited_links = set()
        visited_links.add(url)

        count = 0
        for link in links:
            if link not in visited_links:
                link_screenshot_id = str(uuid.uuid4())
                link_file_path = f"screenshots/{link_screenshot_id}_part1.png"
                await page.goto(link)

                total_height = await page.evaluate("document.body.scrollHeight")
                viewport_height = await page.evaluate("window.innerHeight")

                num_screenshots = total_height // viewport_height + 1
                for i in range(num_screenshots):
                    link_file_path = f"screenshots/{link_screenshot_id}_part{i+1}.png"
                    await page.screenshot(path=link_file_path)
                    print(f"Screenshot part{i+1} of (link) saved to {link_file_path}")
                    if i <num_screenshots - 1:
                        await page.evaluate(f"window.scrollBy(0, {viewport_height})")
                        await asyncio.sleep(0.5)

                visited_links.add(link)
                count += 1
                if count >= num_links:
                    break

        await browser.close()

url = "https://www.binance.com/bg"
num_links = 3

os.makedirs("screenshots", exist_ok=True)

asyncio.run(take_screenshot(url, num_links))
