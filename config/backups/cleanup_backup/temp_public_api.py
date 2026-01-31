
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
