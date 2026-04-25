#!/usr/bin/env python3
"""
Sample Playwright script
"""
import asyncio
from playwright.async_api import async_playwright
from flows.signup import sign_up_flow

async def main():
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to a website
        await page.goto("https://events.elle.vn")
        
        await sign_up_flow(page)
        # Keep browser open for 30 seconds
        await page.wait_for_timeout(30000)
        # Close browser
        # await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
