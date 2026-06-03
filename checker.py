import httpx, base64, json, asyncio
import xml.etree.ElementTree as ET
from datetime import datetime

# NHẬP MÁY BẠN MUỐN VÀO ĐÂY
DEVICES = [
    {"model": "SM-X820", "csc": "XSP"},
    {"model": "SM-S928B", "csc": "XXV"}
]

async def get_fw(model, csc):
    url = "https://fota-cloud-dn.ospserver.net/firmware/FUS/check"
    headers = {"User-Agent": "FUS-4.0/Android", "Content-Type": "application/xml"}
    data = f'<?xml version="1.0" encoding="UTF-8"?><FUSRequest><Device><Model>{model}</Model><SalesCode>{csc}</SalesCode></Device><Protocol>3.0</Protocol></FUSRequest>'
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(url, content=data, headers=headers)
            res = base64.b64decode(r.text).decode('utf-8')
            root = ET.fromstring(res)
            fw = root.find(".//fw_version") or root.find(".//latest")
            return fw.text if fw is not None else "Chưa có firmware"
        except: return "Lỗi Server"

async def main():
    tasks = [get_fw(d['model'], d['csc']) for d in DEVICES]
    results = await asyncio.gather(*tasks)
    final = []
    for i, d in enumerate(DEVICES):
        final.append({**d, "version": results[i], "time": datetime.now().strftime("%H:%M:%S")})
    with open("data.json", "w") as f:
        json.dump(final, f, indent=4)

if __name__ == "__main__":
    asyncio.run(main())

