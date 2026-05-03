import os
from playwright.sync_api import sync_playwright

USER = os.getenv('AEROTHAI_USER')
PASS = os.getenv('AEROTHAI_PASS')

def run(playwright):
    # เปิดเบราว์เซอร์แบบดั้งเดิม ไม่มีเทคนิคพรางตัวใดๆ
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    
    print("🌍 1. กำลังเข้าหน้า Login...")
    page.goto("https://www.aerothai.aero/CASServices/Login.aspx?application=AIM&returnurl=https://notamthai.aerothai.aero/Login.aspx&originalReturnUrl=/NewiPIB.aspx")
    page.wait_for_timeout(3000)
    
    print("🔑 2. กำลังกรอก Username และ Password (แบบพิมพ์รวดเดียวจบ)...")
    page.locator('input[type="text"]').first.fill(USER)
    page.locator('input[type="password"]').first.fill(PASS)
    
    print("🚀 3. กำลังกดปุ่ม Login...")
    page.locator('input[type="submit"], button[type="submit"], input[value="Login"]').first.click()
    
    print("⏳ 4. รอ 8 วินาที เพื่อดูผลลัพธ์ว่าทะลุไปได้ไหม...")
    page.wait_for_timeout(8000)
    
    # ถ่ายรูปผลลัพธ์
    page.screenshot(path="old_way_result.png", full_page=True)
    print("📸 ถ่ายรูปเสร็จสิ้น! ตรวจสอบภาพ old_way_result.png ได้เลยครับ")
    
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
