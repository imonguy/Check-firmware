import httpx
import base64
import xml.etree.ElementTree as ET
import json
from datetime import datetime

# BẠN MUỐN CHECK MÁY NÀO THÌ NHẬP VÀO ĐÂY
DEVICES = [
    {"model": "SM-X820", "csc": "XSP"},
    {"model": "SM-S928B", "csc": "XXV"},
]

def fus_decrypt(data):
    try: return base64.b64decode(data).decode('utf-8')
    except: return data

async def capture(model, csc):
    url = "https://fota-cloud-dn.ospserver.net/firmware/FUS/check"
    headers = {"User-Agent": "FUS-4.0/Android", "Content-Type": "application/xml"}
    payload = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><FUSRequest><Device><Model>{model}</Model><SalesCode>{csc}</SalesCode></Device><Protocol>3.0</Protocol></FUSRequest>'
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(url, content=payload, headers=headers, timeout=15)
            root = ET.fromstring(fus_decrypt(r.text))
            fw = root.find(".//fw_version")
            if fw is None: fw = root.find(".//latest")
            return fw.text if fw is not None else "Không tìm thấy Firmware"
        except: return "Lỗi kết nối Server"

async def main():
    res = []
    for d in DEVICES:
        v = await capture(d['model'], d['csc'])
        res.append({**d, "version": v, "time": datetime.now().strftime("%H:%M:%S %d/%m/%Y")})
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
