
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import uvicorn

app = FastAPI(title="临时设备API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/devices")
async def get_devices_public():
    try:
        conn = sqlite3.connect('data/devices.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, region, store, ip, port, user, pwd, chs, name, status, protocol FROM devices")
        devices = cursor.fetchall()
        conn.close()
        
        result = []
        for device in devices:
            result.append({
                "id": device[0],
                "region": device[1],
                "store": device[2],
                "ip": device[3],
                "port": device[4],
                "user": device[5],
                "pwd": device[6],
                "chs": device[7],
                "name": device[8],
                "status": device[9],
                "protocol": device[10]
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/devices/stats")
async def get_device_stats():
    try:
        conn = sqlite3.connect('data/devices.db')
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM devices")
        statuses = cursor.fetchall()
        conn.close()
        
        total = len(statuses)
        online = sum(1 for status in statuses if status[0] == 'online')
        offline = total - online
        online_rate = round((online / total * 100), 1) if total > 0 else 0
        
        return {
            "total": total,
            "online": online,
            "offline": offline,
            "onlineRate": online_rate
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/regions")
async def get_regions():
    try:
        conn = sqlite3.connect('data/devices.db')
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT region FROM devices")
        regions = cursor.fetchall()
        conn.close()
        
        return [region[0] for region in regions if region[0]]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/devices/{device_id}/check-status")
async def check_device_status(device_id: int):
    try:
        conn = sqlite3.connect('data/devices.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, ip, port, user, pwd, protocol FROM devices WHERE id = ?", (device_id,))
        device = cursor.fetchone()
        conn.close()
        
        if not device:
            raise HTTPException(status_code=404, detail="设备未找到")
        
        # 模拟状态检查 - 在实际应用中这里会进行RTSP连接测试
        return {
            "device_id": device[0],
            "status": "online",  # 模拟在线状态
            "checked_at": "2024-01-01T00:00:00Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/devices/check-all-status")
async def check_all_devices_status():
    try:
        conn = sqlite3.connect('data/devices.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, ip, port, user, pwd, protocol FROM devices")
        devices = cursor.fetchall()
        conn.close()
        
        results = []
        for device in devices:
            results.append({
                "device_id": device[0],
                "status": "online",  # 模拟在线状态
                "checked_at": "2024-01-01T00:00:00Z"
            })
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
