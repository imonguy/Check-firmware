import httpx
import base64
import xml.etree.ElementTree as ET
import json
from datetime import datetime

# DANH SÁCH THIẾT BỊ KHÔNG GIỚI HẠN
DEVICES = [
    # --- DÒNG S & S FE ---
    {"model": "SM-S928B", "csc": "XXV", "name": "Galaxy S24 Ultra", "type": "S Series"},
    {"model": "SM-S921B", "csc": "XXV", "name": "Galaxy S24", "type": "S Series"},
    {"model": "SM-S711B", "csc": "XXV", "name": "Galaxy S23 FE", "type": "S FE"},
    
    # --- DÒNG Z (FOLD & FLIP) ---
    {"model": "SM-F946B", "csc": "XXV", "name": "Galaxy Z Fold 5", "type": "Z Series"},
    {"model": "SM-F731B", "csc": "XXV", "name": "Galaxy Z Flip 5", "type": "Z Series"},

    # --- DÒNG A & M ---
    {"model": "SM-A556E", "csc": "XXV", "name": "Galaxy A55", "type": "A Series"},
    {"model": "SM-A356E", "csc": "XXV", "name": "Galaxy A35", "type": "A Series"},
    {"model": "SM-M556B", "csc": "XXV", "name": "Galaxy M55", "type": "M Series"},

    # --- DÒNG TABLET (TAB S, FE, LITE, A) ---
    {"model": "SM-X910", "csc": "XXV", "name": "Tab S9 Ultra", "type": "Tab S"},
    {"model": "SM-X510", "csc": "XXV", "name": "Tab S9 FE", "type": "Tab FE"},
    {"model": "SM-P613", "csc": "XXV", "name": "Tab S6 Lite", "type": "Tab Lite"},
    {"model": "SM-X210", "csc": "XXV", "name": "Tab A9+", "type": "Tab A"},

    # --- BẢN TEST NỘI BỘ (Để săn One UI sớm nhất) ---
    {"model": "SM-S928B", "csc": "EUX", "name": "S24 Ultra (Internal EU)", "type": "Internal Test"},
]

def fus_decrypt(data):
    try: return base64.b64decode(data).decode('utf-8')
    except: return data

async def capture_fota(model, csc):
    url = "https://fota-cloud-dn.ospserver.net/firmware/FUS/check"
    headers = {"User-Agent": "FUS-4.0/Android", "Content-Type": "application/xml"}
    payload = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <FUSRequest><Device><Model>{model}</Model><SalesCode>{csc}</SalesCode></Device><Protocol>3.0</Protocol></FUSRequest>"""
    
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(url, content=payload, headers=headers, timeout=20.0)
            xml_text = fus_decrypt(r.text)
            root = ET.fromstring(xml_text)
            fw = root.find(".//fw_version")
            if fw is None: fw = root.find(".//latest")
            return fw.text if fw is not None else "Pending/Hidden"
        except: return "Server Error"

async def main():
    results = []
    print(f"🚀 Bắt đầu quét {len(DEVICES)} thiết bị...")
    for d in DEVICES:
        version = await capture_fota(d['model'], d['csc'])
        results.append({
            "name": d['name'], "model": d['model'], "csc": d['csc'],
            "version": version, "type": d['type'],
            "time": datetime.now().strftime("%H:%M - %d/%m/%Y")
        })
        print(f"OK: {d['name']}")
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

