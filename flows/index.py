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

import warnings

warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    message=r"coroutine 'Locator.click' was never awaited"
)

async def run_playwright_flow(celebrity_name, index, total_run):
    run_number_prefix = f"RUN {index}/{total_run}:"
    async with async_playwright() as p:
        print(f"{run_number_prefix} START VOTING PROCESS FOR {celebrity_name.upper()}")

        max_retries = 3  # Số lần thử click lại submit
        mid = None
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # Navigate to a website
            await page.goto("https://events.elle.vn")

            print(f'{run_number_prefix} ☑️ STEP 1: GENERATING TEMP EMAIL ...')
            temp_email, timestamp = get_temp_email()
            print(f'{run_number_prefix} >>> EMAIL: {temp_email}')

            # SIGN UP
            print(f'{run_number_prefix} ☑️ STEP 2: BẮT ĐẦU ĐĂNG KÝ ...')
            await sign_up_flow(page, temp_email)
            current_url = page.url

            # BYPASS CAPTCHA
            isBypassed = await bypass_captcha(current_url, page, run_number_prefix)
            if (isBypassed == True):
                print(f"{run_number_prefix} >>> CLICK NÚT SUBMIT GỬI VỀ INBOX---")
                await click_fake_submit(page)
                check_duration = 30

                print(f"{run_number_prefix} >>> CHỜ: {check_duration} GIÂY ...")
                await page.wait_for_timeout(check_duration * 1000)
                print(f"{run_number_prefix} >>> Đang lấy mail ...")
                # GET EMAIL MID
                mid = get_email_mid(temp_email, timestamp)

                if mid:
                    print(f"{run_number_prefix} >>> THÀNH CÔNG! LẤY ĐƯỢC MID: {mid}")
                else:
                    print(f"{run_number_prefix} >>> THẤT BẠI: KHÔNG NHẬN ĐƯỢC MAIL.")
                if(mid == None):
                    print(f'{run_number_prefix} >>> GET MAIL ĐĂNG KÝ THẤT BẠI. RUN {index} THẤT BẠI! EXITING ...')
                else:
                    # GET FULL EMAIL LAST MESSAGE
                    message = get_full_email_last_message(temp_email, mid, run_number_prefix)

                    # GET VERIFY LINK AND GO TO IT
                    link = get_link_via_message(message)
                    await page.goto(link)
                    print(f'{run_number_prefix} >>> ĐĂNG KÝ HOÀN THÀNH, ĐANG CHỜ EMAIL XÁC NHẬN ...')

                    print(f'{run_number_prefix} ☑️ STEP 3: BẮT ĐẦU ĐĂNG NHẬP ...')
                    await sign_in_flow(page, temp_email)
                    current_url = page.url

                    # BYPASS CAPTCHA
                    await bypass_captcha(current_url, page, run_number_prefix)

                    # WAIT
                    await page.wait_for_timeout(20000)

                    print(f'{run_number_prefix} ☑️ STEP 4: BẮT ĐẦU VOTE ...')
                    # Get in the voting page after signed in
                    # await page.locator("a", has_text="Vào trang 2026").click()
                    # await page.wait_for_url("**/elle-beauty-awards-2026")
                    # await page.locator("a").filter(has_text="Nhân vật").first.click()
                    # await page.wait_for_url("**/nhan-vat")
                    await page.goto("https://events.elle.vn/elle-beauty-awards-2026/nhan-vat")
                    await vote(page, celebrity_name, index, total_run)
                    await page.wait_for_timeout(5000)
                    await browser.close()
        finally:
            await browser.close()

async def vote(page, celebrity_name, index, total_run):
    card = page.locator("article").filter(
        has=page.locator("h3", has_text=celebrity_name)
    )
    button = card.locator("button", has_text="Bình chọn").first
    await button.evaluate("(el) => el.click()")
    print('=' * 100)
    print(f"COMPLETED RUN {index}/{total_run}: ✔️ ✔️ ✔️ VOTED FOR {celebrity_name.upper()}")
    print('=' * 100)
    