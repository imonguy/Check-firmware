import httpx, base64, json, asyncio
import xml.etree.ElementTree as ET
from datetime import datetime

# DANH SÁCH MÁY CỦA BẠN
DEVICES = [
    {"model": "SM-X820", "csc": "XSP"},
    {"model": "SM-S928B", "csc": "XXV"}
]

async def get_fw(model, csc):
    url = "https://fota-cloud-dn.ospserver.net/firmware/FUS/check"
    # Header đầy đủ để đánh lừa server Samsung
    headers = {
        "User-Agent": "FUS-4.0/Android",
        "Content-Type": "application/xml",
        "Accept": "application/xml"
    }
    # Payload XML chuẩn hóa theo định dạng 2026
    data = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><FUSRequest><Device><Model>{model}</Model><SalesCode>{csc}</SalesCode></Device><Protocol>3.0</Protocol></FUSRequest>'
    
    async with httpx.AsyncClient(verify=False) as client: # Bỏ qua xác thực SSL nếu cần
        try:
            r = await client.post(url, content=data, headers=headers, timeout=20)
            # Giải mã và lấy dữ liệu
            res = base64.b64decode(r.text).decode('utf-8')
            root = ET.fromstring(res)
            fw = root.find(".//fw_version") or root.find(".//latest")
            return fw.text if fw is not None else "Chưa có Firmware"
        except: 
            return "Server Busy - Thử lại sau"

async def main():
    tasks = [get_fw(d['model'], d['csc']) for d in DEVICES]
    results = await asyncio.gather(*tasks)
    final = []
    for i, d in enumerate(DEVICES):
        final.append({
            "model": d['model'], 
            "csc": d['csc'], 
            "version": results[i], 
            "time": datetime.now().strftime("%H:%M:%S %d/%m/%Y")
        })
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(final, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    asyncio.run(main())


