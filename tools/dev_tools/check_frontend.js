// 检查前端设备数据获取
(async () => {
    try {
        console.log('检查前端设备数据...');
        
        // 模拟前端请求
        const response = await fetch('http://localhost:5173/api/devices');
        console.log('响应状态:', response.status);
        
        if (response.ok) {
            const devices = await response.json();
            console.log('设备数量:', devices.length);
            
            devices.forEach((device, index) => {
                console.log(`设备 ${index + 1}:`, {
                    name: device.name,
                    ip: device.ip,
                    port: device.port,
                    protocol: device.protocol,
                    status: device.status,
                    chs: device.chs,
                    user: device.user,
                    pwd: device.pwd ? '***' : '无密码'
                });
                
                // 构建RTSP URL
                const rtspUrl = `rtsp://${device.user || 'admin'}:${device.pwd || 'password'}@${device.ip}:${device.port || 554}/Streaming/Channels/${device.chs || 1}01`;
                console.log(`RTSP URL: ${rtspUrl}`);
            });
        } else {
            console.error('获取设备失败:', response.statusText);
        }
        
    } catch (error) {
        console.error('错误:', error.message);
    }
})();