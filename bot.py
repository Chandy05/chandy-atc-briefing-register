import os
import datetime
from playwright.sync_api import sync_playwright

USER = os.getenv('AEROTHAI_USER')
PASS = os.getenv('AEROTHAI_PASS')

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(timezone_id="Asia/Bangkok", accept_downloads=True)
    page = context.new_page()

    try:
        print("🌍 1. กำลังเข้าหน้า Login...")
        page.goto("https://www.aerothai.aero/CASServices/Login.aspx?application=AIM&returnurl=https://notamthai.aerothai.aero/Login.aspx&originalReturnUrl=/NewiPIB.aspx")
        
        print("🔑 2. กำลังกรอก Username / Password...")
        page.locator('input[type="text"]').first.fill(USER)
        page.locator('input[type="password"]').first.fill(PASS)
        page.locator('input[type="submit"], button[type="submit"], input[value="Login"]').first.click()

        print("⏳ 3. รอเช็คผลการล็อกอิน...")
        page.wait_for_timeout(4000)
        page.screenshot(path="debug_01_after_login.png") # ถ่ายรูปไว้ดูว่าติดอะไรไหม

        # ตรวจสอบเผื่อมีแจ้งเตือนให้ Force Login (กรณีมีคนล็อกอินค้างไว้)
        if page.locator("text='Force Login'").count() > 0 or page.locator("text='force login'").count() > 0:
            print("⚠️ พบการล็อกอินซ้อน กำลังกด Force Login ทะลุเข้าไป...")
            page.locator("text='Force Login'").first.click()
            page.wait_for_timeout(4000)

        # รอจนกว่าคำว่า Callsign จะโผล่ขึ้นมาจริงๆ
        print("⏳ กำลังรอหน้าฟอร์ม NewiPIB...")
        page.wait_for_selector("text='Callsign'", timeout=20000)
        page.screenshot(path="debug_02_inside_form.png")

        print("📝 4. กำลังกรอกแบบฟอร์มภารกิจ...")
        
        # 4.1 เลือก PIB Type: Area (BKK FIR only)
        page.locator("td, span, label").filter(has_text="Area (BKK FIR only)").locator("input[type='radio']").first.check(force=True)
        page.wait_for_timeout(2000)

        # 4.2 ติ๊กเลือก NOTAM Zone
        zones_to_check = ['VTBX', 'VTPX', 'VTUX']
        zones_to_uncheck = ['VTCX', 'VTSX']

        for zone in zones_to_check:
            cb = page.locator("td, span").filter(has_text=zone).locator("input[type='checkbox']")
            if cb.count() > 0:
                cb.first.check(force=True)

        for zone in zones_to_uncheck:
            cb = page.locator("td, span").filter(has_text=zone).locator("input[type='checkbox']")
            if cb.count() > 0:
                cb.first.uncheck(force=True)

        # 4.3 กรอกข้อมูลสนามบินและ Callsign
        page.locator("tr").filter(has_text="Callsign").locator("input[type='text']").first.fill("SCL")
        page.locator("tr").filter(has_text="Departure Aerodrome").locator("input[type='text']").first.fill("VTBL")
        page.locator("tr").filter(has_text="Destination Aerodrome").locator("input[type='text']").first.fill("VTPI")
        page.locator("tr").filter(has_text="Alternate Aerodrome").locator("input[type='text']").first.fill("VTUN")

        # 4.4 คำนวณวันที่พรุ่งนี้
        thai_time = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
        tomorrow = thai_time + datetime.timedelta(days=1)
        date_str = tomorrow.strftime("%d/%m/%Y")
        
        print(f"📅 กำหนดวันที่เป็น: {date_str} (00:00 - 23:59)")
        start_row = page.locator("tr").filter(has_text="Start Period")
        start_row.locator("input[type='text']").nth(0).fill(date_str)
        start_row.locator("input[type='text']").nth(1).fill("00:00")

        end_row = page.locator("tr").filter(has_text="End Period")
        end_row.locator("input[type='text']").nth(0).fill(date_str)
        end_row.locator("input[type='text']").nth(1).fill("23:59")

        print("🚀 5. กดปุ่ม Create PIB...")
        page.locator("text='Create PIB'").click()

        print("⏳ 6. รอประมวลผลข้อมูล (หน้า Result)...")
        page.wait_for_selector("text='Generate PDF'", timeout=45000)
        page.screenshot(path="debug_03_result_ready.png")
        page.wait_for_timeout(3000)

        print("📄 7. กำลังสั่ง Generate PDF...")
        page.evaluate("document.querySelectorAll('form').forEach(f => f.target = '_self');")
        page.evaluate("window.open = function(url, name, features) { window.location.href = url; return window; };")

        with page.expect_response(lambda response: "NewResultPIB.aspx" in response.url, timeout=45000) as response_info:
            page.locator("text='Generate PDF'").click()

        pdf_bytes = response_info.value.body()
        
        file_name = f"Mission_PIB_{tomorrow.strftime('%Y-%m-%d')}.pdf"
        with open(file_name, "wb") as f:
            f.write(pdf_bytes)

        print(f"🎉 8. ดึงข้อมูลเสร็จสมบูรณ์! ได้ไฟล์ชื่อ: {file_name}")

    except Exception as e:
        print(f"🚨 เกิดข้อผิดพลาด: {str(e)}")
        page.screenshot(path="error_screenshot_final.png", full_page=True)
        raise e
    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
