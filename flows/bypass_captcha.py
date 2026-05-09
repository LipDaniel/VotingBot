
import os
from twocaptcha import TwoCaptcha
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ.get("TWOCAPTCHA_API_KEY")

solver = TwoCaptcha(api_key)

async def bypass_captcha(current_url, page):
    try: 
        result = solver.turnstile(
            sitekey='0x4AAAAAACnJ4TeSqCnnHCkt',
            url=current_url,
        )

        if result:
            print('Solved turnstile Captcha success!')

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
        print('Bypass Captcha thành công!')
        return True
    except Exception as e:
        print("🚨 Có Lỗi xảy ra khi bypass Captcha: ", e)
        return False


async def click_fake_submit(page):
    print("🔨 Tạo nút giả để kích hoạt logic Form...")
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