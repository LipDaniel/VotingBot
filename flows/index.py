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
    async with async_playwright() as p:
        print('=' * 100)
        print(f"RUN {index}/{total_run}: START VOTING FOR {celebrity_name.upper()}")

        max_retries = 4  # Số lần thử click lại submit
        mid = None
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # Navigate to a website
            await page.goto("https://events.elle.vn")

            print(f'☑️ STEP 1: GENERATED TEMP EMAIL ...')
            temp_email, timestamp = get_temp_email()
            print(f'>>> EMAIL: {temp_email}')

            # SIGN UP
            print('☑️ STEP 2: BẮT ĐẦU ĐĂNG KÝ ...')
            await sign_up_flow(page, temp_email)
            current_url = page.url

            # BYPASS CAPTCHA
            isBypassed = await bypass_captcha(current_url, page)
            if (isBypassed == True):
                for attempt in range(max_retries + 1):
                    print(f">>>>>> LẦN THỬ {attempt + 1}: CLICK NÚT SUBMIT GỬI VỀ INBOX---")
                    await click_fake_submit(page)
                    check_duration = 30

                    print(f">>>>>> CHỜ: {check_duration} GIẤY ...")
                    await page.wait_for_timeout(check_duration * 1000)

                    # GET EMAIL MID
                    mid = get_email_mid(temp_email, timestamp)
                    print(">>>>>> MID: " + str(mid))

                    if mid:
                        print(f">>>>>> THÀNH CÔNG! LẤY ĐƯỢC MID: {mid}")
                        break
                    else:
                        print(f">>>>>> LẦN THỬ {attempt + 1} THẤT BẠI: KHÔNG NHẬN ĐƯỢC MAIL.")
                        if attempt < max_retries - 1:
                            await page.wait_for_timeout(2000)
                if(mid == None):
                    print(f'>>>>>> GET MAIL ĐĂNG KÝ THẤT BẠI SAU {max_retries + 1} LẦN THỬ. RUN {index} THẤT BẠI!')
                    print('>>>>>> EXITING ...')
                else:
                    # GET FULL EMAIL LAST MESSAGE
                    message = get_full_email_last_message(temp_email, mid)

                    # GET VERIFY LINK AND GO TO IT
                    link = get_link_via_message(message)
                    await page.goto(link)
                    print('>>> ĐĂNG KÝ HOÀN THÀNH, ĐANG CHỜ EMAIL XÁC NHẬN ...')

                    print('☑️ STEP 3: BẮT ĐẦU ĐĂNG NHẬP ...')
                    await sign_in_flow(page, temp_email)
                    current_url = page.url

                    # BYPASS CAPTCHA
                    await bypass_captcha(current_url, page)

                    # WAIT
                    await page.wait_for_timeout(15000)

                    print('☑️ STEP 4: BẮT ĐẦU VOTE ...')
                    # Get in the main page after signed in
                    await page.locator("a", has_text="Vào trang 2026").click()
                    await page.wait_for_url("**/elle-beauty-awards-2026")
                    await page.locator("a").filter(has_text="Nhân vật").first.click()
                    await page.wait_for_url("**/nhan-vat")
                    await vote(page, celebrity_name, index, total_run)
                    await page.wait_for_timeout(5000)
                    await browser.close()
        finally:
            await browser.close()


async def vote(page, celebrity_name, index, total_run):
    card = page.locator("article").filter(
        has=page.locator("h3", has_text=celebrity_name)
    )
    await page.wait_for_timeout(5000)
    button = card.locator("button", has_text="Bình chọn").first
    await button.evaluate("(el) => el.click()")
    print(f"✔️ ✔️ ✔️ VOTED FOR {celebrity_name.upper()} | COMPLETED {index}/{total_run}")
    