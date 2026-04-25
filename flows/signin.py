#!/usr/bin/env python3
"""
Login script - Detect and click login button
"""
import asyncio
from playwright.async_api import async_playwright


async def detect_and_click_login_button(page):
    """
    Detect login button and click it
    """
    try:
        selector = ".page_loginLink__aLlv_"
        
        
        login_button = page.locator(selector)
        
        if await login_button.is_visible():
            print("✓ Login button found!")
            await login_button.click()
            print("✓ Login button clicked!")
            return True
        else:
            print("✗ Login button not visible")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
