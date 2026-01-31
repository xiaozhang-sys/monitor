/**
 * 统一错误处理工具函数
 */

/**
 * 处理API错误并返回用户友好的错误消息
 * @param {Error} error - 捕获的错误对象
 * @param {string} defaultMessage - 默认错误消息
 * @returns {string} 用户友好的错误消息
 */
export const handleApiError = (error, defaultMessage = '操作失败') => {
  console.error('API Error:', error)
  
  // 网络错误
  if (error.code === 'ERR_NETWORK') {
    return '网络连接失败，请检查网络设置'
  }
  
  // HTTP错误响应
  if (error.response) {
    switch (error.response.status) {
      case 400:
        return '请求参数错误'
      case 401:
        // 401错误由路由守卫处理，这里返回空字符串避免重复提示
        return ''
      case 403:
        return '访问被拒绝，权限不足'
      case 404:
        return '请求的资源未找到'
      case 408:
        return '请求超时，请稍后重试'
      case 409:
        return '资源冲突'
      case 500:
        return '服务器内部错误'
      case 502:
        return '网关错误'
      case 503:
        return '服务暂时不可用'
      case 504:
        return '网关超时'
      default:
        return `请求失败 (${error.response.status})`
    }
  }
  
  // 请求发送失败（如网络问题）
  if (error.request) {
    return '无法连接到服务器，请检查网络连接'
  }
  
  // 其他错误
  return defaultMessage
}

/**
 * 重试异步操作
 * @param {Function} operation - 要重试的操作函数
 * @param {number} maxRetries - 最大重试次数
 * @param {number} delay - 重试延迟（毫秒）
 * @returns {Promise<any>} 操作结果
 */
export const retryOperation = async (operation, maxRetries = 3, delay = 1000) => {
  let lastError = null

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await operation()
    } catch (error) {
      lastError = error
      console.warn(`操作失败，重试中... (${i + 1}/${maxRetries})`, error)
      
      if (i < maxRetries - 1) {
        // 指数退避策略
        await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)))
      }
    }
  }

  throw lastError
}

/**
 * 处理视频播放错误
 * @param {Event} errorEvent - 视频错误事件
 * @returns {string} 错误描述
 */
export const handleVideoError = (errorEvent) => {
  const videoElement = errorEvent.target
  const errorCode = videoElement.error?.code
  const errorMessage = videoElement.error?.message || '未知错误'
  
  let detailedError = ''
  switch (errorCode) {
    case MediaError.MEDIA_ERR_ABORTED:
      detailedError = '视频加载被中止'
      break
    case MediaError.MEDIA_ERR_NETWORK:
      detailedError = '网络连接错误'
      break
    case MediaError.MEDIA_ERR_DECODE:
      detailedError = '视频解码错误（格式不支持）'
      break
    case MediaError.MEDIA_ERR_SRC_NOT_SUPPORTED:
      detailedError = '视频格式不支持或URL错误'
      break
    default:
      detailedError = '未知播放错误'
  }
  
  console.error('视频播放错误详情:', {
    code: errorCode,
    message: errorMessage
  })
  
  return `视频加载失败: ${detailedError}`
}