// 前端配置文件 - 临时解决认证问题
window.APP_CONFIG = {
  API_BASE_URL: 'http://localhost:8004',
  WEBRTC_URL: 'http://localhost:8090',
  DEBUG_MODE: true
};

// 覆盖默认API配置
if (window.APP_CONFIG) {
  // 创建新的API实例，绕过认证
  window.tempApi = {
    get: async (url) => {
      const response = await fetch(window.APP_CONFIG.API_BASE_URL + url);
      return {
        data: await response.json(),
        status: response.status
      };
    }
  };
}

console.log('临时配置已加载，使用公共API端口8004');