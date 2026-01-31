// 在浏览器控制台中运行的调试脚本
(function() {
    console.log('=== 认证调试信息 ===');
    
    // 检查Cookie中的token
    const token = document.cookie.split('; ').find(row => row.startsWith('token='));
    console.log('Cookie中的token:', token ? token.split('=')[1] : '未找到');
    
    // 检查localStorage
    console.log('localStorage中的auth_token:', localStorage.getItem('auth_token') || '未找到');
    
    // 测试API调用
    fetch('/api/devices', {
        headers: token ? { 'Authorization': `Bearer ${token.split('=')[1]}` } : {}
    })
    .then(response => {
        console.log('API响应状态:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('设备数量:', data.length);
    })
    .catch(error => {
        console.error('API调用错误:', error);
    });
    
    // 检查API客户端
    console.log('API客户端配置:', window.api ? '已定义' : '未定义');
    
})();