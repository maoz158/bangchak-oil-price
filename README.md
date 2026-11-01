# Bangchak Fuel Log

หน้าเว็บราคาน้ำมัน Bangchak พร้อมบันทึกการเติมของรถยนต์ (E20) และมอเตอร์ไซค์ (G95) คำนวณ กม./ลิตร และต้นทุนต่อกิโลเมตรจากข้อมูลที่กรอก

เปิดดูได้ที่ https://maoz158.github.io/bangchak-oil-price/

## วิธีทำงาน

- **ราคา:** GitHub Actions ([.github/workflows/update-prices.yml](.github/workflows/update-prices.yml)) ดึงราคาทุกวัน 05:00 น. เวลาไทย ([scripts/fetch_prices.py](scripts/fetch_prices.py))
  - `data/latest.json` ราคาล่าสุด เขียนเฉพาะเมื่อราคาที่แสดงบนหน้าเว็บเปลี่ยน
  - `data/history.json` ประวัติ G95 และ E20 บันทึกเมื่อราคาเปลี่ยน
  - เปิด GitHub Issue เมื่อราคา G95 หรือ E20 เปลี่ยน และเมื่อดึงข้อมูลไม่สำเร็จ
- **การเติม:** หน้าเว็บส่งข้อมูลไปยัง Google Apps Script ที่บันทึกลง Google Sheet ชื่อ **Fuel Log** แท็บ **Fills**
  - อ่านประวัติกลับมาจาก endpoint เดียวกัน
  - ราคาหน้าปั๊มโดยประมาณ = ราคาประกาศวันนี้ + ส่วนต่างของการเติมล่าสุด
  - กม./ลิตร คำนวณจากระยะตั้งแต่เลขไมล์แรกถึงล่าสุด หารด้วยลิตรที่เติมหลังครั้งแรก (ไม่ต้องเติมเต็มถังทุกครั้ง)

## โครงสร้าง

| ไฟล์ | หน้าที่ |
| --- | --- |
| `index.html` | หน้าเว็บทั้งหมด (HTML/CSS/JS ไฟล์เดียว) |
| `scripts/fetch_prices.py` | ดึงราคาจาก Bangchak และเขียน `data/` |
| `data/latest.json`, `data/history.json` | ข้อมูลราคาที่หน้าเว็บอ่าน |
| `.github/workflows/update-prices.yml` | ตั้งเวลาดึงราคา commit ข้อมูล และเปิด Issue |

Apps Script (Code.gs) อยู่ในโปรเจกต์ Apps Script ชื่อ Fuel Log API ไม่ได้เก็บในรีโปนี้

## ข้อควรรู้

- URL ของ Apps Script เขียนข้อมูลได้โดยใครก็ได้ที่มี ใช้งานส่วนตัวได้ แต่ไม่ควรโพสต์ในที่สาธารณะเพิ่มเติม
- ราคาประกาศเป็นราคา กทม. ที่ยังไม่รวมภาษีบำรุงท้องถิ่น กทม. ราคาหน้าปั๊มจริงอาจต่างกันตามพื้นที่
- ข้อมูลประกอบการตัดสินใจ ไม่ใช่คำแนะนำการลงทุน

## รันบนเครื่อง

```bash
python3 scripts/fetch_prices.py
python3 -m http.server 8000
```

แล้วเปิด http://127.0.0.1:8000/ (ถ้า macOS ขึ้น `CERTIFICATE_VERIFY_FAILED` ให้รัน `Install Certificates.command` ของ Python ก่อน)
