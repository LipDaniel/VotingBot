#!/usr/bin/env python3
"""
Login script - Detect and click login button
"""

async def detect_and_click_login_button(page):
    """
    Detect login button and click it
    """
    try:
        selector = ".page_loginLink__aLlv_"
        login_button = page.locator(selector)
        
        if await login_button.is_visible():
            await login_button.click()
            return True
        else:
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

async def sign_in_flow(page, temp_email):
    """
    Detect login button and click it
    """
    try:
        await detect_and_click_login_button(page)
        await page.fill('input[name="identifier"]', temp_email)
        await page.fill('input[name="password"]', "test@gmail.com")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

