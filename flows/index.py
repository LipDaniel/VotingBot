from playwright.async_api import async_playwright

from flows.bypass_captcha import bypass_captcha, click_fake_submit
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
        max_retries = 4  # Số lần thử click lại submit
        mid = None
        print('=' * 100)
        print(f"Run {run_number}: start voting for {celebrity_name}")

        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # Navigate to a website
            await page.goto("https://events.elle.vn")

            print('=' * 100)
            print('getting temp email ...')
            temp_email, timestamp = get_temp_email()

            # SIGN UP
            await sign_up_flow(page, temp_email)
            current_url = page.url
            print(f"Current URL: {current_url}")

            print('=' * 100)
            print('Starting sign up flow ...')
            # BYPASS CAPTCHA
            isBypassed = await bypass_captcha(current_url, page)
            if (isBypassed == False):
                print('*' * 100)
                print(f'Bypass captcha thất bại. Run {run_number} thất bại!')
            else:
                for attempt in range(max_retries + 1):
                    print(f"--- Lần thử {attempt + 1}: click nút submit đợi email gửi về inbox---")
                    await click_fake_submit(page)
                    check_duration = 30

                    print(f"chờ: {check_duration} giây ...")
                    await page.wait_for_timeout(check_duration * 1000)

                    # GET EMAIL MID
                    mid = get_email_mid(temp_email, timestamp)
                    print("mid: " + str(mid))

                    if mid:
                        print(f"Thành công! Lấy được mid: {mid}")
                        break
                    else:
                        print(f"Lần thử {attempt + 1} thất bại: Không nhận được mail.")
                        # Nếu chưa phải lần thử cuối, có thể F5 nhẹ hoặc đợi 1 chút trước khi click lại
                        if attempt < max_retries - 1:
                            await page.wait_for_timeout(2000)
                if(mid == None):
                    print('*' * 100)
                    print(f'Get mail đăng ký thất bại sau {max_retries + 1} lần thử. Run {run_number} thất bại!')
                    print('exiting ...')
                else:
                    # GET FULL EMAIL LAST MESSAGE
                    message = get_full_email_last_message(temp_email, mid)

                    # GET VERIFY LINK AND GO TO IT
                    link = get_link_via_message(message)
                    print("link hoàn thành đăng ký: ", link)
                    await page.goto(link)
                    print('Sign up flow completed!')

                    print('=' * 100)
                    print('Starting sign in flow ...')
                    await sign_in_flow(page, temp_email)
                    current_url = page.url

                    # BYPASS CAPTCHA
                    await bypass_captcha(current_url, page)

                    # WAIT
                    await page.wait_for_timeout(15000)

                    print('Sign in flow completed!')

                    print('=' * 100)
                    print('Starting to get in the voting page after signed in ...')
                    # Get in the main page after signed in
                    await page.locator("a", has_text="Vào trang 2026").click()
                    await page.wait_for_url("**/elle-beauty-awards-2026")
                    await page.locator("a").filter(has_text="Nhân vật").first.click()
                    await page.wait_for_url("**/nhan-vat")

                    print('=' * 100)
                    print('Voting...')
                    print('Voting completed!')
                    print(f"Run {run_number}: reached voting page for {celebrity_name}")
        finally:
            await browser.close()
