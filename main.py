#!/usr/bin/env python3
"""
Sample Playwright script
"""
import asyncio

from app_window import open_app_window
from flows.index import run_playwright_flow


async def run_vote_loop(celebrity_name, amount):
    for run_number in range(1, amount + 1):
        await run_playwright_flow(celebrity_name, run_number)


async def main(data):
    celebrity_name = data["celeb"]
    amount = data["amount"]
    await run_vote_loop(celebrity_name, amount)


if __name__ == "__main__":
    data = open_app_window()
    if data:
        asyncio.run(main(data))
