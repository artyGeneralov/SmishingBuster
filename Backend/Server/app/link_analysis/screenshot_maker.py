import random
import string
import os
from selenium import webdriver
from PIL import Image
import asyncio
from concurrent.futures import ThreadPoolExecutor

def generate_random_filename(extension='.png', length=10):
    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return random_chars + extension

def take_full_page_screenshot(driver, save_directory):
    random_filename = generate_random_filename()
    save_path = os.path.join(save_directory, random_filename)
    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    driver.execute_script(f"window.scrollTo(0, {viewport_height + 50});")
    driver.implicitly_wait(2)
    driver.save_screenshot(save_path)
    return random_filename

def sync_take_screenshot(url, save_directory):
    driver = webdriver.Chrome()
    
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    try:
        driver.get(url)
        screenshot_name = take_full_page_screenshot(driver, save_directory)
        return screenshot_name
    finally:
        driver.quit()

async def take_screenshot(url, save_directory):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, sync_take_screenshot, url, save_directory)
