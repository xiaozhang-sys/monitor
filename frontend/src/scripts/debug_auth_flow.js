// 浏览器控制台调试脚本 - 验证认证流程
// 使用方法：在浏览器F12控制台中粘贴运行

console.log('=== 认证流程调试脚本 ===');

// 检查当前URL和基础配置
console.log('当前URL:', window.location.href);
console.log('API基础URL:', '/api');

// 检查Cookie状态
console.log('=== Cookie状态 ===');
const token = document.cookie.split('; ').find(row => row.startsWith('token='));
console.log('Token存在:', !!token);
if (token) {
  console.log('Token值:', token.split('=')[1]);
}

// 测试登录API
async function testLogin() {
  console.log('=== 测试登录API ===');
  try {
    const formData = new FormData();
    formData.append('username', '${USERNAME}');
    formData.append('password', '${PASSWORD}');
    
    console.log('发送请求到:', '/api/token');
    const response = await fetch('/api/token', {
      method: 'POST',
      body: formData,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    
    console.log('响应状态:', response.status);
    const data = await response.json();
    console.log('响应数据:', data);
    return data;
  } catch (error) {
    console.error('登录错误:', error);
    throw error;
  }
}

// 测试设备API
async function testDevices() {
  console.log('=== 测试设备API ===');
  try {
    console.log('发送请求到:', '/api/devices');
    const response = await fetch('/api/devices');
    console.log('响应状态:', response.status);
    const data = await response.json();
    console.log('设备数量:', data.length);
    return data;
  } catch (error) {
    console.error('设备API错误:', error);
    throw error;
  }
}

// 运行测试
async function runTests() {
  try {
    await testLogin();
    await testDevices();
  } catch (error) {
    console.error('测试失败:', error);
  }
}

console.log('运行测试命令: await runTests()');
console.log('或单独测试: await testLogin() 或 await testDevices()');