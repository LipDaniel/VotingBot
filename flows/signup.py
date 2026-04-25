
#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright
from .signin import detect_and_click_login_button

async def sign_up_flow(page):
    try:
        await detect_and_click_login_button(page)
        await go_to_signup_page(page)
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

async def go_to_signup_page(page):
    try:
        await page.get_by_text("Tạo tài khoản").click()
        await page.fill('input[name="username"]', "test@gmail.com")
        await page.fill('input[name="email"]', "test@gmail.com")
        await page.fill('input[name="password"]', "test@gmail.com")
        await page.fill('input[name="passwordConfirmation"]', "test@gmail.com")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
