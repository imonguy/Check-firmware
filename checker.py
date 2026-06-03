import httpx
import base64
import xml.etree.ElementTree as ET
import json
from datetime import datetime

# DANH SÁCH THIẾT BỊ (Đã xóa hết, bạn tự thêm máy vào đây)
DEVICES = [
    # Cấu trúc: {"model": "Mã máy", "csc": "Mã vùng", "name": "Tên máy"},
    {"model": "SM-S928B", "csc": "XXV", "name": "S24 Ultra"}, 
]

def fus_decrypt(data):
    try: return base64.b64decode(data).decode('utf-8')
    except: return data

async def capture_fota(model, csc):
    url = "https://fota-cloud-dn.ospserver.net/firmware/FUS/check"
    headers = {
        "User-Agent": "FUS-4.0/Android",
        "Content-Type": "application/xml",
        "Accept": "application/xml"
    }
    payload = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><FUSRequest><Device><Model>{model}</Model><SalesCode>{csc}</SalesCode></Device><Protocol>3.0</Protocol></FUSRequest>'
    
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(url, content=payload, headers=headers, timeout=20.0)
            xml_text = fus_decrypt(r.text)
            root = ET.fromstring(xml_text)
            fw = root.find(".//fw_version")
            if fw is None: fw = root.find(".//latest")
            return fw.text if fw is not None else "Chưa có dữ liệu"
        except:
            return "Server Busy"

async def main():
    results = []
    for d in DEVICES:
        version = await capture_fota(d['model'], d['csc'])
        results.append({
            "name": d['name'],
            "model": d['model'],
            "csc": d['csc'],
            "version": version,
            "time": datetime.now().strftime("%H:%M - %d/%m/%Y")
        })

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
