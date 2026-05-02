import os
from playwright.sync_api import sync_playwright

# ดึงรหัสผ่านจากตู้เซฟ GitHub Secrets
USER = os.getenv('AEROTHAI_USER')
PASS = os.getenv('AEROTHAI_PASS')

def run(playwright):
    # เปิดเบราว์เซอร์ Chromium แบบซ่อนหน้าจอ
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    
    print("🌍 1. กำลังเข้าหน้า Login...")
    page.goto("https://www.aerothai.aero/CASServices/Login.aspx?application=AIM&returnurl=https://notamthai.aerothai.aero/Login.aspx&originalReturnUrl=/NewiPIB.aspx")
    page.wait_for_timeout(3000) # รอหน้าเว็บโหลดให้สมบูรณ์
    
    # ถ่ายรูปก่อนล็อกอิน เพื่อเช็คว่าเปิดหน้าเว็บถูกไหม
    page.screenshot(path="step1_login.png")
    
    print("🔑 2. กำลังกรอก Username และ Password...")
    # ให้บอทหาช่องกรอกข้อความช่องแรก (มักจะเป็น Username) และช่อง Password
    page.locator('input[type="text"]').first.fill(USER)
    page.locator('input[type="password"]').first.fill(PASS)
    
    # ถ่ายรูปตอนกรอกเสร็จ (แต่ยังไม่กด Enter) เพื่อเช็คว่าพิมพ์ถูกช่องไหม
    page.screenshot(path="step2_filled.png")
    
    print("🚀 3. กำลังกดปุ่ม Login...")
    # หาปุ่ม Submit หรือปุ่ม Login แล้วคลิก
    page.locator('input[type="submit"], button[type="submit"], input[value="Login"]').first.click()
    
    print("⏳ 4. รอโหลดหน้าเว็บหลัก...")
    page.wait_for_timeout(8000) # รอ 8 วินาทีให้ระบบรีไดเรกต์เข้าหน้า NewiPIB
    
    # ถ่ายรูปหลังล็อกอินสำเร็จ ว่าเข้าไปเจอหน้าตาแบบไหน
    page.screenshot(path="step3_inside.png")
    print("📸 ถ่ายรูปเสร็จสิ้น! บิดกุญแจรถสำเร็จ!")
    
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
