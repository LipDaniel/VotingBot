#!/usr/bin/env python3
"""
Sample Playwright script
"""
import asyncio
from playwright.async_api import async_playwright
from flows.signup import sign_up_flow
from twocaptcha import TwoCaptcha
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ.get("TWOCAPTCHA_API_KEY")

solver = TwoCaptcha(api_key)

async def main():
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to a website
        await page.goto("https://events.elle.vn")
        
        await sign_up_flow(page)
        current_url = page.url
        print(f"URL hiện tại là: {current_url}")

        result = solver.turnstile(
            sitekey='0x4AAAAAACnJ4TeSqCnnHCkt',
            url=current_url,
        )

        print('result: ' + str(result))

        await page.evaluate(f"""
            (token) => {{
                document.querySelectorAll('input[name="cf-turnstile-response"]').forEach(el => el.value = token);
            }}
        """, result['code']) # type: ignore

        print("🛠️ Đang cố gắng bypass State bảo mật...")
        
        await page.evaluate(f"""
            (token) => {{
                // Hàm tìm mọi hàm có vẻ là callback
                const triggerAllCallbacks = () => {{
                    // Tìm trong window._cf_chl_opt
                    if (window._cf_chl_opt && window._cf_chl_opt.callback) {{
                        const cb = window[window._cf_chl_opt.callback];
                        if (typeof cb === 'function') cb(token);
                    }}

                    // Tìm tất cả các div turnstile và ép gọi callback từ data-attribute
                    document.querySelectorAll('.cf-turnstile').forEach(el => {{
                        const cbName = el.getAttribute('data-callback');
                        if (cbName && window[cbName]) window[cbName](token);
                    }});
                }};

                triggerAllCallbacks();

                // Nếu nút vẫn chưa hiện, ta sẽ ép Form phải chạy bằng cách tạo Event "submit"
                const form = document.querySelector('form');
                if (form) {{
                    // Tạo một event submit giả lập nhưng có thuộc tính để bypass các bộ lọc
                    const event = new Event('submit', {{ bubbles: true, cancelable: true }});
                    form.dispatchEvent(event);
                    console.log("🚀 Đã gửi Event Submit giả lập!");
                }}
            }}
        """, result['code']) # type: ignore

        print("🔨 Chiêu cuối: Tạo nút giả để kích hoạt logic Form...")
        await page.evaluate("""
            () => {
                const form = document.querySelector('form');
                if (form && !document.querySelector('.LoginForm_primaryButton__kzWKc')) {
                    const fakeBtn = document.createElement('button');
                    fakeBtn.type = 'submit';
                    fakeBtn.className = 'LoginForm_primaryButton__kzWKc'; // Trùng class nút thật
                    fakeBtn.innerText = 'Fake Submit';
                    fakeBtn.style.opacity = '0'; // Tàng hình
                    form.appendChild(fakeBtn);
                    fakeBtn.click();
                }
            }
        """)

        # if (Xác minh bảo mật không thành công. Vui lòng tải lại trang để làm mới CAPTCHA rồi thử lại.) success!
        # if (username và email đã được đăng ký...) Thử lại với username và email khác ở signup.py
        # wait to check the success state
        await page.wait_for_timeout(100000)

        # Close browser
        # await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
