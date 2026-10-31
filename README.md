# Bangchak Fuel Decision Dashboard

หน้า dashboard ราคาน้ำมัน Bangchak ดึงราคาจริงผ่าน `/api/oil` เพื่อเปรียบเทียบ แก๊สโซฮอล์ 95 S EVO กับ E20 S EVO, ช่วยวางแผนเติม และเก็บประวัติส่วนต่างราคาไว้ในเบราว์เซอร์

## รันในเครื่อง

```bash
python3 server.py
```

เปิด http://127.0.0.1:8000

> หมายเหตุ: ถ้า `/api/oil` ขึ้น `CERTIFICATE_VERIFY_FAILED` บน macOS ให้รัน
> `/Applications/Python 3.x/Install Certificates.command` ก่อน
> หรือใช้ `ALLOW_INSECURE_TLS=1 python3 server.py` (ใช้เฉพาะตอนดีบักในเครื่อง ห้ามใช้บนเซิร์ฟเวอร์จริง)

## รันออนไลน์

ต้องมี backend เพราะหน้าเว็บเรียก `/api/oil` ของตัวเอง ซึ่ง GitHub Pages รันไม่ได้

- **Render** : เชื่อม repo นี้แล้วใช้ `render.yaml` ได้เลย
- **ที่อื่นที่รัน Python ได้** : ใช้ `Procfile` หรือคำสั่ง `python3 server.py` โดยเซิร์ฟเวอร์จะอ่านค่า `PORT` จาก environment เอง

ไม่ต้องติดตั้ง dependency เพิ่ม ใช้เฉพาะ Python standard library

## โครงสร้าง

| ไฟล์ | หน้าที่ |
| --- | --- |
| `index.html` | หน้า dashboard ทั้งหมด (HTML/CSS/JS ไฟล์เดียว) |
| `server.py` | เสิร์ฟหน้าเว็บ และ proxy `/api/oil` ไปยัง API ของ Bangchak |
| `Procfile`, `render.yaml` | คำสั่งเริ่มระบบสำหรับ deploy |

## ที่มาของโปรเจกต์

รวบรวมจากโฟลเดอร์ `Oil_Price` เดิม โดยเก็บเฉพาะเวอร์ชันล่าสุดของแต่ละสาย:

- เก็บ `bangchak_oil_dashboard_planner.html` เป็น `index.html` เพราะเป็นเวอร์ชันที่สมบูรณ์ที่สุด (มี Fuel Planner, ประวัติราคา, กราฟส่วนต่าง)
- ข้ามไฟล์ที่ถูกแทนที่แล้ว: `bangchak_oil_dashboard.html`, `_plus.html`, `_plus_cards.html`, `_plus_cards_fixed.html`, `_ultimate.html`, `_ultimate_fixed.html`
- เขียน `server.py` ใหม่จาก `server_ssl_fix_v2.py` โดยให้ตรวจสอบ TLS ตามปกติ และรองรับ `PORT`/`HOST` สำหรับการรันออนไลน์
- ข้าม `server.py`, `server_fixed.py` เดิม (ถูกแทนที่แล้ว)

## แผนต่อยอด

- [ ] แยก JS/CSS ออกจาก `index.html` เพื่อดูแลง่ายขึ้น
- [ ] เก็บประวัติราคาไว้ฝั่งเซิร์ฟเวอร์แทน localStorage
- [ ] เพิ่ม health check และ log ของการดึงข้อมูลจาก Bangchak
