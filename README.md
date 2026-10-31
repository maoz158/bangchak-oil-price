# Bangchak Fuel Decision Dashboard

หน้า dashboard ราคาน้ำมัน Bangchak เปรียบเทียบ แก๊สโซฮอล์ 95 S EVO กับ E20 S EVO พร้อมเครื่องมือวางแผนการเติม และกราฟส่วนต่างย้อนหลัง

เปิดดูออนไลน์ได้ที่ https://maoz158.github.io/bangchak-oil-price/

## วิธีทำงาน

- GitHub Actions ([.github/workflows/update-prices.yml](.github/workflows/update-prices.yml)) รันวันละครั้ง 05:00 น. เวลาไทย
- [scripts/fetch_prices.py](scripts/fetch_prices.py) ดึงราคาจาก Bangchak แล้วบันทึกไว้ในโฟลเดอร์ `data/`
  - `data/latest.json` ราคาล่าสุด (เขียนทุกครั้งที่รัน)
  - `data/history.json` ประวัติ บันทึกเฉพาะวันที่ราคา G95 หรือ E20 เปลี่ยน
- เมื่อราคาเปลี่ยน workflow จะเปิด GitHub Issue ให้อัตโนมัติ ดูการแจ้งเตือนได้จาก Issues ของ repo นี้
- หน้าเว็บ [index.html](index.html) อ่านไฟล์ใน `data/` แล้วแสดงผล GitHub Pages เสิร์ฟหน้าเว็บนี้

ไม่มี server ที่ต้องดูแล และไม่ต้องติดตั้ง dependency เพิ่ม ใช้เฉพาะ Python standard library

## รันด้วยตัวเอง

- ดึงราคาใหม่: เข้า Actions > Update oil prices > Run workflow
- ดึงราคาบนเครื่อง:

```bash
python3 scripts/fetch_prices.py
```

หมายเหตุ: ถ้าบน macOS ขึ้น `CERTIFICATE_VERIFY_FAILED` ให้รัน `Install Certificates.command` ของ Python ก่อน
หน้าเว็บต้องเปิดผ่าน http ไม่ใช่ `file://` เพราะต้องโหลดไฟล์ใน `data/`

ดูหน้าเว็บบนเครื่องได้ด้วย:

```bash
python3 -m http.server 8000
```

แล้วเปิด http://127.0.0.1:8000/

## ข้อควรรู้

- ข้อมูลมาจาก endpoint ที่หน้าเว็บ oil-price.bangchak.co.th ใช้อยู่ ไม่ใช่ API ทางการ อาจเปลี่ยนหรือปิดได้โดยไม่แจ้ง ถ้าเกิดขึ้น workflow จะเปิด Issue แจ้งความล้มเหลว
- GitHub อาจดีเลย์รัน cron ไม่กี่นาที
- ข้อมูลประกอบการตัดสินใจ ไม่ใช่คำแนะนำการลงทุน

## โครงสร้าง

| ไฟล์ | หน้าที่ |
| --- | --- |
| `index.html` | หน้า dashboard ทั้งหมด (HTML/CSS/JS ไฟล์เดียว) |
| `scripts/fetch_prices.py` | ดึงราคา เขียน `data/` และ set output ให้ workflow |
| `data/latest.json`, `data/history.json` | ข้อมูลที่หน้าเว็บอ่าน |
| `.github/workflows/update-prices.yml` | ตั้งเวลาดึงราคา commit ข้อมูล และเปิด Issue |
