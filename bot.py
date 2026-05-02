import os
import datetime
from playwright.sync_api import sync_playwright

USER = os.getenv('AEROTHAI_USER')
PASS = os.getenv('AEROTHAI_PASS')

def run(playwright):
    # เปิดเบราว์เซอร์ล่องหน และตั้ง Timezone เป็นของไทย (UTC+7)
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        timezone_id="Asia/Bangkok",
        accept_downloads=True # เปิดสิทธิ์ให้บอทดาวน์โหลดไฟล์ได้
    )
    page = context.new_page()

    print("🌍 1. กำลังเข้าหน้า Login...")
    page.goto("https://www.aerothai.aero/CASServices/Login.aspx?application=AIM&returnurl=https://notamthai.aerothai.aero/Login.aspx&originalReturnUrl=/NewiPIB.aspx")
    page.wait_for_timeout(3000)

    print("🔑 2. กำลังกรอก Username / Password...")
    page.locator('input[type="text"]').first.fill(USER)
    page.locator('input[type="password"]').first.fill(PASS)
    page.locator('input[type="submit"], button[type="submit"], input[value="Login"]').first.click()

    print("⏳ 3. รอระบบพาเข้าสู่หน้ากรอกข้อมูล (NewiPIB.aspx)...")
    page.wait_for_url("**/NewiPIB.aspx", timeout=20000)
    page.wait_for_timeout(3000) # รอสคริปต์บนหน้าเว็บโหลดเสร็จ

    print("📝 4. กำลังกรอกแบบฟอร์มภารกิจ...")
    # 4.1 เลือก PIB Type: Area (BKK FIR only)
    page.locator("xpath=//label[contains(text(), 'Area')]/preceding-sibling::input").click()
    page.wait_for_timeout(1000)

    # 4.2 ติ๊กเลือก NOTAM Zone (VTBX, VTPX, VTUX)
    for zone in ['VTBX', 'VTPX', 'VTUX']:
        checkbox = page.locator(f"xpath=//label[contains(text(), '{zone}')]/preceding-sibling::input")
        if not checkbox.is_checked():
            checkbox.check()

    # 4.3 กรอกข้อมูลสนามบินและ Callsign
    page.locator("xpath=//*[contains(text(), 'Callsign')]/ancestor::tr[1]//input[@type='text']").fill("SCL")
    page.locator("xpath=//*[contains(text(), 'Departure Aerodrome')]/ancestor::tr[1]//input[@type='text']").fill("VTBL")
    page.locator("xpath=//*[contains(text(), 'Destination Aerodrome')]/ancestor::tr[1]//input[@type='text']").fill("VTPI")
    page.locator("xpath=//*[contains(text(), 'Alternate Aerodrome')]/ancestor::tr[1]//input[@type='text']").fill("VTUN")

    # 4.4 คำนวณวันที่ "พรุ่งนี้" อัตโนมัติ
    thai_time = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
    tomorrow = thai_time + datetime.timedelta(days=1)
    
    # เตรียม Format วันที่เผื่อไว้ 2 แบบ
    iso_date = tomorrow.strftime("%Y-%m-%d") # แบบสากล
    th_date = tomorrow.strftime("%d/%m/%Y")  # แบบไทย

    start_date_input = page.locator("xpath=//*[contains(text(), 'Start Period')]/ancestor::tr[1]//input").first
    end_date_input = page.locator("xpath=//*[contains(text(), 'End Period')]/ancestor::tr[1]//input").first

    try:
        start_date_input.fill(iso_date)
        end_date_input.fill(iso_date)
    except:
        start_date_input.fill(th_date)
        end_date_input.fill(th_date)

    print("🚀 5. กดปุ่ม Create PIB...")
    page.locator("text='Create PIB'").click()

    print("⏳ 6. รอประมวลผลข้อมูล (กำลังเข้าหน้า NewResultPIB.aspx)...")
    page.wait_for_url("**/NewResultPIB.aspx", timeout=30000)
    page.wait_for_timeout(2000)

    print("📄 7. กำลังสั่ง Generate PDF และดาวน์โหลด...")
    # โค้ดดักจับไฟล์ดาวน์โหลดที่เด้งออกมาจากเบราว์เซอร์
    with page.expect_download(timeout=45000) as download_info:
        page.locator("text='Generate PDF'").click()

    download = download_info.value
    file_name = f"Mission_PIB_{tomorrow.strftime('%Y-%m-%d')}.pdf"
    download.save_as(file_name)

    print(f"🎉 8. ดาวน์โหลดเสร็จสมบูรณ์! ได้ไฟล์ชื่อ: {file_name}")
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
