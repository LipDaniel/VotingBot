#!/usr/bin/env python3
"""
Sample Playwright script
"""
import asyncio
from playwright.async_api import async_playwright

from flows.signin import detect_and_click_login_button


async def main():
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to a website
        await page.goto("https://events.elle.vn")
        
        
        await detect_and_click_login_button(page)
        # Keep browser open for 30 seconds
        await page.wait_for_timeout(30000)
        # Close browser
        # await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
