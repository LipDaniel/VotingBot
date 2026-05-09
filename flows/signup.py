
#!/usr/bin/env python3
from .signin import detect_and_click_login_button

async def sign_up_flow(page, temp_email):
    try:
        await detect_and_click_login_button(page)
        await go_to_signup_page(page, temp_email)
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

async def go_to_signup_page(page, temp_email):
    try:
        username = temp_email.split("@")[0]
        print("✓ Sign up button clicked!")
        await page.get_by_text("Tạo tài khoản").click()
        await page.fill('input[name="username"]', username)
        await page.fill('input[name="email"]', temp_email)
        await page.fill('input[name="password"]', "test@gmail.com")
        await page.fill('input[name="passwordConfirmation"]', "test@gmail.com")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
