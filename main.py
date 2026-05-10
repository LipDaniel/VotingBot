#!/usr/bin/env python3
"""
Sample Playwright script
"""
import asyncio
from playwright.async_api import async_playwright
from app_window import open_app_window
from flows.index import run_playwright_flow
import multiprocessing

# async def run_vote_loop(celebrity_name, amount):
#     for run_number in range(1, amount + 1):
#         await run_playwright_flow(celebrity_name, run_number, amount)

def worker_wrapper(celebrity_name, index, amount):
    asyncio.run(run_playwright_flow(celebrity_name, index, amount))

async def check_celebrity_name(celebrity_name):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://events.elle.vn/elle-beauty-awards-2026/nhan-vat")
        card = page.locator("article").filter(
            has=page.locator("h3", has_text=celebrity_name)
        )
        count = await card.count()
        
        if count > 0:
            return True
        else:
            print(f"Celebrity name {celebrity_name} does not exist in the page! Exiting ...")
            return False
    
async def main(data):
    celebrity_name = data["celeb"]
    total_accounts = data["amount"]
    num_processes = 6     # Số trình duyệt chạy cùng lúc (tùy vào RAM/CPU của anh)

    print("Checking celebrity name ...")
    isCelebrityNameValid = await check_celebrity_name(celebrity_name)
    if (isCelebrityNameValid):
        print(f"--- Đang khởi tạo hệ thống với {num_processes} luồng song song ---")

        # Tạo danh sách các bộ tham số: [(name, 0, 100), (name, 1, 100), ...]
        tasks = [(celebrity_name, i, total_accounts) for i in range(1, total_accounts + 1)]

        # Sử dụng Pool để quản lý các tiến trình
        with multiprocessing.Pool(processes=num_processes) as pool:
            # map sẽ phân phối các index vào các worker hiện có
            pool.starmap(worker_wrapper, tasks)


if __name__ == "__main__":
    data = open_app_window()
    if data:
        asyncio.run(main(data))
