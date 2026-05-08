#!/usr/bin/env python3
"""
Sample Playwright script
"""
import asyncio
from playwright.async_api import async_playwright
from flows.services import get_temp_email, get_email_mid, get_full_email_last_message, get_link_via_message
from flows.signup import sign_up_flow
from flows.signin import sign_in_flow
from flows.bypass_captcha import bypass_captcha

async def main():
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to a website
        await page.goto("https://events.elle.vn")

        # Get temp email and timestamp
        temp_email, timestamp = get_temp_email()
        print('temp_email: ', temp_email)
        print('timestamp: ', timestamp)

        # Sign up flow
        await sign_up_flow(page, temp_email)
        current_url = page.url
        print(f"URL hiện tại là: {current_url}")
        
        # Bypass turnstile captcha
        await bypass_captcha(current_url, page)

        # wait for captcha solved and send sign-up email to temp_email
        await page.wait_for_timeout(30000)

        # Get email mid
        mid = get_email_mid(temp_email, timestamp)
        print('mid: ' + str(mid))

        # Get full email last message
        message = get_full_email_last_message(temp_email, mid)
        print('message: ' + str(message))

        # Get finished signed up link and go to it
        link = get_link_via_message(message)
        print('link: ', link)
        await page.goto(link)

        # Sign in flow
        await sign_in_flow(page, temp_email)
        current_url = page.url

         # Bypass turnstile captcha
        await bypass_captcha(current_url, page)

        # wait for captcha solved
        await page.wait_for_timeout(15000)

        # Get in the main page after signed in
        await page.locator("a", has_text="Vào trang 2026").click()
        await page.wait_for_url("**/elle-beauty-awards-2026")

        # Get in the voting "Nhân vật" page
        await page.locator("a").filter(has_text="Nhân vật").first.click()
        await page.wait_for_url("**/nhan-vat")

        # Wait to see the result of full flow
        await page.wait_for_timeout(100000)
        # Close browser
        # await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
