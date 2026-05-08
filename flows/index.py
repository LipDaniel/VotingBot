from playwright.async_api import async_playwright

from flows.bypass_captcha import bypass_captcha
from flows.services import (
    get_email_mid,
    get_full_email_last_message,
    get_link_via_message,
    get_temp_email,
)
from flows.signin import sign_in_flow
from flows.signup import sign_up_flow

async def run_playwright_flow(celebrity_name, run_number):
    async with async_playwright() as p:
        print(f"Run {run_number}: start voting for {celebrity_name}")

        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # Navigate to a website
            await page.goto("https://events.elle.vn")

            # Get temp email and timestamp
            temp_email, timestamp = get_temp_email()
            print("temp_email: ", temp_email)
            print("timestamp: ", timestamp)

            # SIGN UP
            await sign_up_flow(page, temp_email)
            current_url = page.url
            print(f"Current URL: {current_url}")

            # BYPASS CAPTCHA
            await bypass_captcha(current_url, page)

            # WAIT
            await page.wait_for_timeout(30000)

            # GET EMAIL MID
            mid = get_email_mid(temp_email, timestamp)
            print("mid: " + str(mid))

            # GET FULL EMAIL LAST MESSAGE
            message = get_full_email_last_message(temp_email, mid)
            print("message: " + str(message))

            # GET VERIFY LINK AND GO TO IT
            link = get_link_via_message(message)
            print("link: ", link)
            await page.goto(link)

            # SIGN IN
            await sign_in_flow(page, temp_email)
            current_url = page.url

            # BYPASS CAPTCHA
            await bypass_captcha(current_url, page)

            # WAIT
            await page.wait_for_timeout(15000)

            # Get in the main page after signed in
            await page.locator("a", has_text="Vào trang 2026").click()
            await page.wait_for_url("**/elle-beauty-awards-2026")

            # Get in the voting page
            await page.locator("a").filter(has_text="Nhân vật").first.click()
            await page.wait_for_url("**/nhan-vat")

            print(f"Run {run_number}: reached voting page for {celebrity_name}")

            # Wait to see the result of full flow
            await page.wait_for_timeout(100000)
        finally:
            await browser.close()
