import httpx
import base64
import xml.etree.ElementTree as ET
import json
from datetime import datetime

# DANH SÁCH MÁY: Bạn chỉ cần sửa danh sách này là xong
DEVICES = [
    {"model": "SM-X820", "csc": "XSP", "name": "Tab S10 Plus"},
    {"model": "SM-S928B", "csc": "XXV", "name": "S24 Ultra"},
]

async def fetch_firmware(model, csc):
    url = "https://fota-cloud-dn.ospserver.net/firmware/FUS/check"
    # Giả lập thiết bị thật (FUS 4.0) để Samsung không chặn
    headers = {
        "User-Agent": "FUS-4.0/Android",
        "Content-Type": "application/xml",
        "Accept": "application/xml"
    }
    # Payload chuẩn Protocol 3.0
    payload = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><FUSRequest><Device><Model>{model}</Model><SalesCode>{csc}</SalesCode></Device><Protocol>3.0</Protocol></FUSRequest>'
    
    async with httpx.AsyncClient(verify=False) as client:
        try:
            r = await client.post(url, content=payload, headers=headers, timeout=20.0)
            # Giải mã Base64 đặc trưng của Samsung
            decoded_xml = base64.b64decode(r.text).decode('utf-8')
            root = ET.fromstring(decoded_xml)
            
            # Lấy build mới nhất
            fw = root.find(".//fw_version")
            if fw is None: fw = root.find(".//latest")
            
            return fw.text if fw is not None else "Internal Build (Beta/Chưa có)"
        except:
            return "Server Samsung Busy"

async def main():
    results = []
    print(f"--- Đang quét {len(DEVICES)} thiết bị ---")
    for d in DEVICES:
        version = await fetch_firmware(d['model'], d['csc'])
        results.append({
            "name": d['name'],
            "model": d['model'],
            "csc": d['csc'],
            "version": version,
            "time": datetime.now().strftime("%H:%M - %d/%m/%Y")
        })
        print(f"✔ {d['model']} -> {version}")

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

