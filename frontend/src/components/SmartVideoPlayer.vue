<template>
  <div class="smart-video-player">
    <!-- HTTP/HTTPS 设备 - 优先使用iframe嵌入厂家Web播放器 -->
    <div v-if="isHttpProtocol && !useAlternativeStream" class="http-iframe-player">
      <iframe
        v-if="iframeUrl"
        :src="iframeUrl"
        class="device-iframe"
        frameborder="0"
        allow="autoplay; fullscreen"
        @load="onIframeLoaded"
        @error="onIframeError"
      ></iframe>
      <div v-else class="error-overlay">
        <el-icon class="error-icon"><VideoPlay /></el-icon>
        <p>无法构建HTTP设备URL</p>
      </div>
      <!-- HTTP设备加载状态指示 -->
      <div v-if="iframeUrl && !error && !httpLoaded" class="loading-overlay">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <span>正在加载设备页面...</span>
      </div>
    </div>

    <!-- HTTP/HTTPS 备用方案 - 直接视频播放（如果设备支持） -->
    <div v-else-if="isHttpProtocol && useAlternativeStream" class="http-player">
      <video
        ref="videoRef"
        class="video-element"
        :src="alternativeStreamUrl"
        controls
        autoplay
        muted
        @loadedmetadata="onVideoLoaded"
        @error="onVideoError"
      >
        您的浏览器不支持视频播放
      </video>
    </div>

    <!-- RTSP 协议 - 使用 WebRTC 转换播放 -->
    <div v-else-if="isRtspProtocol" class="webrtc-player">
      <video
        ref="webrtcVideoRef"
        class="video-element"
        autoplay
        playsinline
      >
        您的浏览器不支持WebRTC
      </video>
      <div v-if="loading" class="loading-overlay">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <span>正在连接视频流...</span>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-overlay">
      <el-icon class="error-icon"><VideoPlay /></el-icon>
      <p>{{ error }}</p>
      <div class="error-actions">
        <el-button type="primary" size="small" @click="retryConnection">
          重试连接
        </el-button>
        <el-button v-if="isHttpProtocol" size="small" @click="openDeviceWeb">
          打开设备网页
        </el-button>
        <el-button v-if="isHttpProtocol" size="small" @click="switchToDirectStream">
          尝试直接流播放
        </el-button>
      </div>
    </div>

    <!-- 协议信息显示和码流控制 -->
    <div class="protocol-info">
      <el-tag :type="protocolType === 'rtsp' ? 'primary' : 'success'" size="small">
        {{ protocolType?.toUpperCase() }}
      </el-tag>
      <span class="stream-url" :title="displayUrl">{{ displayUrl }}</span>
      <!-- 码流切换按钮 -->
      <el-switch
        v-model="localStreamType"
        active-value="main"
        inactive-value="sub"
        active-text="主码流"
        inactive-text="子码流"
        size="small"
        @change="onStreamTypeChange"
        style="margin-left: 8px;"
      />
      <el-button v-if="isHttpProtocol" size="mini" @click="openDeviceWeb" style="margin-left: 8px;">
        <el-icon><Link /></el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { handleApiError, handleVideoError, retryOperation } from '@/utils/errorHandler'
import { Loading, VideoPlay, Link } from '@element-plus/icons-vue'

// 属性定义
const props = defineProps({
  device: {
    type: Object,
    required: true
  },
  streamType: {
    type: String,
    default: 'sub' // 默认为子码流，优化加载速度和网络开销
  }
})

// 事件定义
const emit = defineEmits(['loaded', 'error', 'stream-type-changed'])

// 响应式数据
const videoRef = ref(null)
const webrtcVideoRef = ref(null)
const iframeRef = ref(null)
const loading = ref(false)
const error = ref('')
const pc = ref(null)
const ws = ref(null)
const useAlternativeStream = ref(false)
const currentPathIndex = ref(0)
const httpLoaded = ref(false)
const localStreamType = ref(props.streamType)

// 计算属性
const isHttpProtocol = computed(() => {
  return props.device?.protocol === 'http' || props.device?.protocol === 'https'
})

const isRtspProtocol = computed(() => {
  return props.device?.protocol === 'rtsp'
})

// 根据设备类型生成合适的播放URL
const streamUrl = computed(() => {
  if (!props.device) return ''
  
  if (isHttpProtocol.value) {
    // HTTP/HTTPS协议：使用设备Web界面URL
    const { ip, port, user, pwd } = props.device
    if (!ip) return ''
    
    const httpPort = port || (props.device.protocol === 'https' ? 443 : 80)
    
    // 对于HTTP设备，返回Web界面URL，后续通过iframe嵌入
    return `${props.device.protocol}://${ip}:${httpPort}`
  } else if (isRtspProtocol.value) {
    // RTSP协议保持原有逻辑
    const { ip, port, user, pwd } = props.device
    if (!ip || !port) return ''
    
    const channelNumber = props.device.channel || props.device.chs || 1
    const streamType = props.streamType === 'sub' ? 2 : 1
    const channelCode = channelNumber * 100 + streamType
    
    return `rtsp://${user}:${pwd}@${ip}:${port}/Streaming/Channels/${channelCode}`
  }
  return ''
})

// 生成iframe嵌入URL（用于HTTP设备）
const iframeUrl = computed(() => {
  if (!isHttpProtocol.value || !props.device) return ''
  
  const { ip, port, user, pwd } = props.device
  const httpPort = port || (props.device.protocol === 'https' ? 443 : 80)
  
  // 常见的HTTP设备视频路径格式
  const commonPaths = [
    // 品牌A/Hikvision格式
    `/ISAPI/Streaming/channels/${(props.device.chs || 1) * 100 + 1}`,
    
    // 品牌B/Dahua格式
    `/cam/realmonitor?channel=${props.device.chs || 1}&subtype=0`,
    
    // 通用格式
    `/Streaming/channels/${(props.device.chs || 1) * 100 + 1}`,
    `/h264/ch${props.device.chs || 1}/main/av_stream`,
    
    // 基础Web界面
    '/',
    '/login',
    '/web'
  ]
  
  // 获取设备特定路径（如果有）
  const devicePath = props.device.http_path || ''
  
  if (devicePath) {
    // 如果设置了设备特定路径，使用它
    if (devicePath.includes('://')) {
      // 完整URL
      return devicePath
    } else {
      // 相对路径
      const baseUrl = `${props.device.protocol}://${ip}:${httpPort}`
      return devicePath.startsWith('/') ? `${baseUrl}${devicePath}` : `${baseUrl}/${devicePath}`
    }
  }
  
  // 构建包含认证信息的基础URL
  let baseUrl = `${props.device.protocol}://`
  
  // 添加用户名和密码（如果有）
  if (user && pwd) {
    // 注意：这种方式在现代浏览器中可能会被阻止
    // 但作为兼容性方案保留，实际部署时可能需要其他认证方式
    baseUrl += `${encodeURIComponent(user)}:${encodeURIComponent(pwd)}@`
  }
  
  baseUrl += `${ip}:${httpPort}`
  
  // 选择一个默认路径（优先选择根路径）
  return `${baseUrl}/`
})

const displayUrl = computed(() => {
  // 对于RTSP协议，不显示具体URL路径
  if (isRtspProtocol.value) {
    return '视频流连接中...'
  }
  
  if (useAlternativeStream.value) {
    const url = alternativeStreamUrl.value
    return url.length > 50 ? url.substring(0, 50) + '...' : url
  }
  
  const url = streamUrl.value
  return url.length > 50 ? url.substring(0, 50) + '...' : url
})

// 生成适合直接视频播放的URL
const alternativeStreamUrl = computed(() => {
  if (!isHttpProtocol.value || !props.device) return ''
  
  const { ip, port, user, pwd } = props.device
  const httpPort = port || (props.device.protocol === 'https' ? 443 : 80)
  const channel = props.device.chs || 1
  
  // 常见的HTTP视频流路径
  const streamPaths = [
    // Hikvision/ISAPI标准
    `/ISAPI/Streaming/channels/${channel * 100 + 1}/httppreview`,
    `/ISAPI/Streaming/channels/${channel * 100 + 1}`,
    
    // Dahua标准
    `/cam/realmonitor?channel=${channel}&subtype=0&authbasic=YWRtaW46MTIzNDU2`,
    
    // 通用RTSP转HTTP流格式
    `/mjpg/video.mjpg`,
    `/video.mjpg`,
    `/axis-cgi/mjpg/video.cgi`,
    `/cgi-bin/snapshot.cgi?chn=${channel}`,
    `/video1`,
    `/h264/ch${channel}/main/av_stream`
  ]
  
  // 构建基础URL
  let baseUrl = `${props.device.protocol}://`
  
  // 添加认证信息
  if (user && pwd) {
    baseUrl += `${encodeURIComponent(user)}:${encodeURIComponent(pwd)}@`
  }
  
  baseUrl += `${ip}:${httpPort}`
  
  // 选择当前尝试的路径
  const currentPath = streamPaths[currentPathIndex.value % streamPaths.length]
  return `${baseUrl}${currentPath}`
})

// 方法
const playHttpVideo = () => {
  if (useAlternativeStream.value) {
    console.log('尝试HTTP直接视频流:', alternativeStreamUrl.value)
    if (videoRef.value) {
      videoRef.value.src = alternativeStreamUrl.value
      videoRef.value.load()
    }
  } else {
    console.log('HTTP设备iframeURL:', iframeUrl.value)
    // iframe会在模板中自动加载，但我们可以添加额外的检测逻辑
    checkIframeContent()
  }
}

// 检测iframe内容是否成功加载视频
const checkIframeContent = () => {
  if (!iframeUrl.value) return
  
  // 延迟检测，给iframe足够的加载时间
  setTimeout(() => {
    try {
      // 注意：由于同源策略，这个检查可能会失败，但我们仍然尝试
      const iframe = document.querySelector('.device-iframe')
      if (iframe && iframe.contentDocument) {
        console.log('iframe内容加载成功')
      } else {
        console.log('iframe内容可能加载失败，准备尝试备用方案')
        // 如果iframe可能加载失败，主动触发备用方案
        setTimeout(() => {
          if (!error.value) {
            onIframeError()
          }
        }, 3000) // 3秒后如果没有错误，尝试备用方案
      }
    } catch (e) {
      console.log('无法访问iframe内容（同源策略限制），这是正常现象')
    }
  }, 1000)
}

// 尝试下一个HTTP视频路径
const tryNextPath = () => {
  if (!isHttpProtocol.value) return
  
  currentPathIndex.value++
  useAlternativeStream.value = true
  error.value = ''
  
  // 重置video元素并重新加载
  if (videoRef.value) {
    videoRef.value.pause()
    videoRef.value.src = ''
    setTimeout(() => {
      videoRef.value.src = alternativeStreamUrl.value
      videoRef.value.load()
      console.log('尝试下一个视频路径:', alternativeStreamUrl.value)
    }, 100)
  }
}

// 直接切换到直接视频流播放
const switchToDirectStream = () => {
  error.value = ''
  useAlternativeStream.value = true
  currentPathIndex.value = 0
  
  if (videoRef.value) {
    videoRef.value.pause()
    videoRef.value.src = ''
    setTimeout(() => {
      videoRef.value.src = alternativeStreamUrl.value
      videoRef.value.load()
      console.log('直接切换到视频流播放:', alternativeStreamUrl.value)
    }, 100)
  }
}

const onIframeLoaded = () => {
  console.log('HTTP设备iframe加载成功')
  httpLoaded.value = true
  emit('loaded')
}

const onIframeError = () => {
  // 当iframe加载失败时，尝试切换到备用的直接视频播放方案
  console.log('HTTP设备iframe加载失败，尝试直接视频流播放')
  
  // 重置错误状态
  error.value = ''
  httpLoaded.value = false
  
  // 切换到备用播放模式
  useAlternativeStream.value = true
  
  // 延迟加载以确保组件状态更新
  setTimeout(() => {
    if (videoRef.value) {
      videoRef.value.src = alternativeStreamUrl.value
      videoRef.value.load()
      console.log('尝试直接视频流:', alternativeStreamUrl.value)
    }
  }, 100)
}

const openDeviceWeb = () => {
  if (iframeUrl.value) {
    window.open(iframeUrl.value, '_blank')
  }
}

// 码流类型变化处理
const onStreamTypeChange = async () => {
  console.log('码流类型切换为:', localStreamType.value)
  // 更彻底地停止所有流
  await stopAllStreams()
  loading.value = true
  error.value = ''
  
  try {
    // 增加一个小延迟确保连接完全清理
    await new Promise(resolve => setTimeout(resolve, 300))
    await playRtspVideo()
    // 通知父组件码流类型变化
    emit('stream-type-changed', localStreamType.value)
  } catch (err) {
    console.error('切换码流失败:', err)
  }
}

const playRtspVideo = async () => {
  if (!webrtcVideoRef.value) return
  
  loading.value = true
  error.value = ''
  
  try {
    // 使用重试机制连接到WebRTC服务器
    await retryOperation(
      () => connectWebRTC(),
      3, // 最多重试3次
      2000 // 初始延迟2秒，指数退避
    )
  } catch (err) {
    const errorMessage = handleApiError(err, 'WebRTC连接失败')
    error.value = errorMessage
    emit('error', new Error(errorMessage))
  } finally {
    loading.value = false
  }
}

const connectWebRTC = async () => {
  try {
    // 首先清理所有现有连接
    await stopAllStreams()
    
    const config = {
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' }
      ]
    }
    
    console.log('创建新的WebRTC连接')
    pc.value = new RTCPeerConnection(config)
    
    // 添加视频轨道
    pc.value.ontrack = (event) => {
      if (webrtcVideoRef.value) {
        webrtcVideoRef.value.srcObject = event.streams[0]
      }
    }
    
    // 处理连接状态变化
    pc.value.onconnectionstatechange = () => {
      console.log('WebRTC连接状态:', pc.value.connectionState)
      if (pc.value.connectionState === 'failed') {
        const errorMessage = 'WebRTC连接失败，请检查设备配置和网络连接'
        error.value = errorMessage
        emit('error', new Error(errorMessage))
      } else if (pc.value.connectionState === 'disconnected') {
        const errorMessage = 'WebRTC连接断开，请检查网络连接'
        error.value = errorMessage
        emit('error', new Error(errorMessage))
      }
    }
    
    // 处理ICE连接状态变化
    pc.value.oniceconnectionstatechange = () => {
      console.log('ICE连接状态:', pc.value.iceConnectionState)
      if (pc.value.iceConnectionState === 'failed') {
        const errorMessage = 'ICE连接失败，请检查网络和防火墙设置'
        error.value = errorMessage
        emit('error', new Error(errorMessage))
      }
    }
    
    // 处理ICE候选
    pc.value.onicecandidate = (event) => {
      if (event.candidate) {
        console.log('发现ICE候选:', event.candidate)
      }
    }
    
    // 创建 offer - 请求音频和视频轨道
    const offer = await pc.value.createOffer({
      offerToReceiveAudio: true,
      offerToReceiveVideo: true,
      iceRestart: true // 强制创建新的ICE代理
    })
    await pc.value.setLocalDescription(offer)
    console.log('本地SDP创建成功，等待远程响应')
    
    // 发送到WebRTC服务器
    const webrtcPort = window.__WEBRTC_PORT__ || import.meta.env.VITE_WEBRTC_PORT || 8090;
    webrtcBaseUrl = import.meta.env.VITE_WEBRTC_BASE_URL || `http://localhost:${webrtcPort}`
    console.log('WebRTC配置信息:')
    console.log('- window.__WEBRTC_PORT__:', window.__WEBRTC_PORT__)
    console.log('- import.meta.env.VITE_WEBRTC_PORT:', import.meta.env.VITE_WEBRTC_PORT)
    console.log('- import.meta.env.VITE_WEBRTC_BASE_URL:', import.meta.env.VITE_WEBRTC_BASE_URL)
    console.log('- 最终webrtcBaseUrl:', webrtcBaseUrl)
    
    // 首先测试服务器连接是否可用
    try {
      console.log('正在测试WebRTC服务器连接...')
      const healthResponse = await fetch(`${webrtcBaseUrl}/health`)
      if (healthResponse.ok) {
        console.log('WebRTC服务器健康检查成功')
      } else {
        console.warn('WebRTC服务器健康检查失败:', healthResponse.status)
      }
    } catch (healthError) {
      console.warn('WebRTC服务器健康检查连接失败:', healthError.message)
    }
    
    let response
    try {
      console.log('正在发送WebRTC offer到:', `${webrtcBaseUrl}/api/offer`)
      console.log('请求数据大小:', JSON.stringify({
        sdp: offer.sdp.substring(0, 100) + '...',
        rtsp_url: streamUrl.value,
        type: 'offer',
        stream_type: localStreamType.value
      }))
      
      response = await fetch(`${webrtcBaseUrl}/api/offer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sdp: offer.sdp,
          rtsp_url: streamUrl.value,
          type: 'offer',
          stream_type: localStreamType.value
        })
      })
      
      console.log('WebRTC服务器响应状态:', response.status)
    } catch (networkError) {
      // 网络连接错误处理
      console.error('WebRTC服务器连接异常:', networkError)
      console.error('异常类型:', networkError.constructor.name)
      console.error('异常消息:', networkError.message)
      
      if (networkError instanceof TypeError && networkError.message.includes('fetch')) {
        throw new Error(`无法连接到WebRTC服务器，请确保服务器正在运行且地址正确 (${webrtcBaseUrl})`)
      }
      throw networkError
    }

    if (!response.ok) {
      // 检查是否是连接错误
      if (response.status === 0) {
        throw new Error(`无法连接到WebRTC服务器，请确保服务器正在运行且地址正确 (${webrtcBaseUrl})`)
      }
      
      let errorData
      try {
        errorData = await response.json()
      } catch (parseError) {
        throw new Error(`WebRTC服务器响应错误: ${response.status} ${response.statusText}`)
      }
      
      throw new Error(errorData.error || `WebRTC服务器响应错误: ${response.status}`)
    }
    
    const data = await response.json()
    if (data.error) {
      throw new Error(data.error)
    }
    
    // 设置远程描述
    console.log('收到WebRTC服务器响应:', data)
    
    // 保存连接ID和设置心跳
    if (data.pc_id && data.heartbeat_interval) {
      pcId = data.pc_id
      const interval = data.heartbeat_interval * 1000 // 转换为毫秒
      console.log(`设置WebRTC心跳，间隔 ${interval}ms，连接ID: ${pcId}`)
      
      // 清除旧的心跳定时器
      if (heartbeatTimer) {
        clearInterval(heartbeatTimer)
      }
      
      // 设置新的心跳定时器
      heartbeatTimer = setInterval(sendHeartbeat, interval)
    }
    
    if (data.sdp) {
      console.log('接收到SDP响应，尝试设置远程描述')
      try {
        // 使用标准SDP格式处理
        const cleanSDP = data.sdp
          .replace(/\r\n/g, '\n')
          .replace(/\r/g, '\n')
          .replace(/\n/g, '\r\n')
          .trim()
          .replace(/\r\n\r\n+/g, '\r\n')
          .replace(/\r\n$/, '\r\n')
        
        // 确保SDP以换行符结尾
        const finalSDP = cleanSDP.endsWith('\r\n') ? cleanSDP : cleanSDP + '\r\n'
        
        // 检查连接对象是否仍然有效
        if (!pc.value) {
          throw new Error('WebRTC连接对象已失效，无法设置远程描述')
        }
        
        // 检查连接状态
        const currentState = pc.value.signalingState
        console.log(`当前信令状态: ${currentState}，准备设置远程描述`)
        
        try {
          // 尝试在当前连接上设置远程描述
          // 首先检查连接是否仍然有效并处于正确状态
          if (pc.value && pc.value.signalingState !== 'closed') {
            console.log('设置标准SDP描述')
            await pc.value.setRemoteDescription({ 
              type: data.type || 'answer', 
              sdp: finalSDP
            })
          } else {
            throw new Error(`连接对象无效或已关闭，信令状态: ${pc.value ? pc.value.signalingState : 'null'}`)
          }
        } catch (stateError) {
          console.error(`SDP设置失败: ${stateError.message}，重新创建连接并尝试`) 
          
          // 清理现有连接
          try {
            if (pc.value) {
              pc.value.close()
            }
          } catch (closeError) {
            console.warn('关闭当前连接时出错:', closeError)
          }
          pc.value = null
          
          // 创建全新的连接对象
          pc.value = new RTCPeerConnection(config)
          
          // 添加必要的事件监听器
          pc.value.ontrack = (event) => {
            if (webrtcVideoRef.value) {
              webrtcVideoRef.value.srcObject = event.streams[0]
            }
          }
          
          pc.value.onconnectionstatechange = () => {
            console.log('WebRTC连接状态:', pc.value.connectionState)
          }
          
          // 尝试直接在新连接上设置远程描述
          console.log('在新连接上设置远程描述')
          await pc.value.setRemoteDescription({ 
            type: data.type || 'answer', 
            sdp: finalSDP
          })
        }
        
        console.log('SDP设置成功')
      } catch (sdpError) {
        console.error('SDP设置失败，尝试兼容性修复:', sdpError)
        
        // 确保我们有一个新的、干净的SDP进行修复
        let compatibleSDP = data.sdp;
        
        // 第一步：标准化SDP格式
        compatibleSDP = compatibleSDP
          .replace(/\r\n/g, '\n')
          .replace(/\r/g, '\n')
          .replace(/\n/g, '\r\n')
          .trim();
        
        if (!compatibleSDP.endsWith('\r\n')) {
          compatibleSDP += '\r\n';
        }
        
        // 尝试多种兼容性修复策略
        const repairStrategies = [
          // 策略1：移除指纹验证和设置固定的setup模式
          () => {
            const sdp = compatibleSDP
              .replace(/a=fingerprint:.*?\r\n/g, '')
              .replace(/a=setup:.*?\r\n/g, 'a=setup:active\r\n');
            console.log('尝试兼容性修复策略1：移除指纹验证，设置固定setup模式');
            return sdp;
          },
          
          // 策略2：简化SDP，移除ICE相关参数
          () => {
            const sdp = compatibleSDP
              .replace(/a=fingerprint:.*?\r\n/g, '')
              .replace(/a=setup:.*?\r\n/g, 'a=setup:active\r\n')
              .replace(/a=ice-options:.*?\r\n/g, '')
              .replace(/a=candidate:.*?\r\n/g, '')
              .replace(/a=end-of-candidates\r\n/g, '');
            console.log('尝试兼容性修复策略2：简化SDP，移除ICE相关参数');
            return sdp;
          },
          
          // 策略3：完全替换ICE凭证
          () => {
            const sdp = compatibleSDP
              .replace(/a=fingerprint:.*?\r\n/g, '')
              .replace(/a=setup:.*?\r\n/g, 'a=setup:active\r\n')
              .replace(/a=ice-ufrag:.*?\r\n/g, 'a=ice-ufrag:compatibility\r\n')
              .replace(/a=ice-pwd:.*?\r\n/g, 'a=ice-pwd:compatibility123456\r\n');
            console.log('尝试兼容性修复策略3：替换ICE凭证');
            return sdp;
          }
        ];
        
        // 尝试每种修复策略
        for (let i = 0; i < repairStrategies.length; i++) {
          try {
            // 确保我们有一个有效的连接对象
            if (!pc.value) {
              pc.value = new RTCPeerConnection(config);
              
              pc.value.ontrack = (event) => {
                if (webrtcVideoRef.value) {
                  webrtcVideoRef.value.srcObject = event.streams[0];
                }
              };
              
              pc.value.onconnectionstatechange = () => {
                console.log('WebRTC连接状态:', pc.value.connectionState);
              };
            }
            
            // 获取修复后的SDP
            const repairedSDP = repairStrategies[i]();
            
            try {
              // 尝试设置修复后的SDP
              await pc.value.setRemoteDescription({
                type: data.type || 'answer',
                sdp: repairedSDP
              });
              console.log(`兼容性修复策略${i+1}成功`);
              // 如果成功，跳出循环
              break;
            } catch (strategyError) {
              console.error(`兼容性修复策略${i+1}失败:`, strategyError);
              
              // 如果不是最后一种策略，清理连接并准备下一次尝试
              if (i < repairStrategies.length - 1) {
                try {
                  if (pc.value) {
                    pc.value.close();
                  }
                } catch (closeError) {
                  console.warn('关闭连接失败:', closeError);
                }
                pc.value = null;
              }
            }
          } catch (error) {
            console.error(`执行修复策略${i+1}时出错:`, error);
          }
        }
        
        // 检查连接是否成功建立
        if (!pc.value || pc.value.connectionState !== 'connected') {
          throw new Error('WebRTC连接失败: 所有兼容性修复策略均已失败');
        }
        
        console.log('SDP设置成功');
      }
    }
    
    emit('loaded')
  } catch (err) {
    console.error('WebRTC连接失败:', err)
    const errorMessage = handleApiError(err, 'WebRTC连接失败')
    error.value = errorMessage
    emit('error', new Error(errorMessage))
    
    // 清理连接
    if (pc.value) {
      pc.value.close()
      pc.value = null
    }
  }
}

// 简化版的SDP验证 - 仅处理基本格式问题
const validateAndFixSDP = (sdp) => {
  if (!sdp) return sdp
  
  // 确保使用标准CRLF换行符
  let fixedSDP = sdp
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .replace(/\n/g, '\r\n')
  
  // 确保以换行符结尾
  if (!fixedSDP.endsWith('\r\n')) {
    fixedSDP += '\r\n'
  }
  
  return fixedSDP
}

// 生成合适的ICE密码
const generateICEPassword = () => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < 32; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

const onVideoLoaded = () => {
  emit('loaded')
}

const onVideoError = (e) => {
  // 如果尝试的路径不超过3个，继续尝试下一个路径
  if (currentPathIndex.value < 3) {
    console.log('当前视频路径播放失败，尝试下一个路径')
    tryNextPath()
    return
  }
  
  // 所有路径都尝试失败后，显示错误信息
  const errorMessage = handleVideoError(e)
  error.value = errorMessage
  emit('error', new Error(errorMessage))
  
  console.error('视频播放错误详情:', {
    code: e.target.error?.code,
    message: e.target.error?.message || '未知错误',
    url: useAlternativeStream.value ? alternativeStreamUrl.value : streamUrl.value,
    device: props.device,
    pathAttempts: currentPathIndex.value + 1
  })
}

const retryConnection = async () => {
  error.value = ''
  
  try {
    if (isHttpProtocol.value) {
      // 重置尝试状态
      if (useAlternativeStream.value) {
        // 如果当前在备用模式，切换回iframe模式
        useAlternativeStream.value = false
        currentPathIndex.value = 0
      }
      playHttpVideo()
    } else if (isRtspProtocol.value) {
      await playRtspVideo()
    }
    ElMessage.success('重试连接成功')
  } catch (err) {
    const errorMessage = handleApiError(err, '重试连接失败')
    ElMessage.error(errorMessage)
  }
}

// 心跳相关变量
let heartbeatTimer = null
let pcId = null
let webrtcBaseUrl = null

// 发送心跳函数
const sendHeartbeat = async () => {
  if (!pcId || !webrtcBaseUrl) return
  
  try {
    const heartbeatResponse = await fetch(`${webrtcBaseUrl}/api/heartbeat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ pc_id: pcId })
    })
    
    if (heartbeatResponse.ok) {
      console.log('WebRTC心跳发送成功')
    } else {
      console.warn('WebRTC心跳发送失败:', heartbeatResponse.status)
    }
  } catch (heartbeatError) {
    console.warn('WebRTC心跳连接失败:', heartbeatError.message)
  }
}

const stopAllStreams = async () => {
  try {
    // 清理心跳定时器
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
    pcId = null
    
    // 清理WebRTC连接
    if (pc.value) {
      // 先移除所有事件监听器
      pc.value.ontrack = null
      pc.value.onconnectionstatechange = null
      pc.value.oniceconnectionstatechange = null
      pc.value.onicecandidate = null
      
      // 关闭连接
      pc.value.close()
      pc.value = null
    }
    
    // 清理WebSocket连接
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
    
    // 清理视频元素
    if (videoRef.value) {
      videoRef.value.pause()
      videoRef.value.src = ''
    }
    
    // 清理WebRTC视频流
    if (webrtcVideoRef.value?.srcObject) {
      webrtcVideoRef.value.srcObject.getTracks().forEach(track => {
        try {
          track.stop()
        } catch (e) {
          console.warn('停止轨道时出错:', e)
        }
      })
      webrtcVideoRef.value.srcObject = null
    }
    
    // 添加一个小延迟确保所有清理操作完成
    await new Promise(resolve => setTimeout(resolve, 100))
    console.log('所有流已成功停止和清理')
  } catch (error) {
    console.warn('清理流时出现错误:', error)
  }
}

// 生命周期
onMounted(() => {
  // 确保设备数据有效
  if (!props.device || !props.device.id) {
    error.value = '设备数据无效'
    return
  }
  
  console.log('SmartVideoPlayer 挂载，设备:', props.device.name, 'URL:', streamUrl.value)
  
  if (isHttpProtocol.value) {
    playHttpVideo()
  } else if (isRtspProtocol.value) {
    playRtspVideo()
  }
})

onUnmounted(() => {
  stopAllStreams()
})

watch(() => props.device, (newDevice, oldDevice) => {
  if (!newDevice || !newDevice.id) {
    error.value = '设备数据无效'
    return
  }
  
  console.log('设备数据变化，重新连接:', newDevice.name)
  stopAllStreams()
  
  // 重置播放状态
  useAlternativeStream.value = false
  currentPathIndex.value = 0
  httpLoaded.value = false
  
  // 延迟重新连接，确保数据完全更新
  setTimeout(() => {
    if (isHttpProtocol.value) {
      playHttpVideo()
    } else if (isRtspProtocol.value) {
      playRtspVideo()
    }
  }, 100)
}, { deep: true })

// 监听streamUrl变化
watch(streamUrl, (newUrl) => {
  if (newUrl && newUrl !== '') {
    console.log('Stream URL更新:', newUrl)
    stopAllStreams()
    setTimeout(() => {
      if (isHttpProtocol.value) {
        playHttpVideo()
      } else if (isRtspProtocol.value) {
        playRtspVideo()
      }
    }, 100)
  }
})
</script>

<style scoped>
.smart-video-player {
  position: relative;
  width: 100%;
  height: 100%;
  background: #000;
  border-radius: 4px;
  overflow: hidden;
}

.video-element {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.loading-overlay,
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  text-align: center;
}

.loading-icon {
  font-size: 48px;
  animation: spin 1s linear infinite;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.protocol-info {
  position: absolute;
  top: 8px;
  left: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 0, 0, 0.7);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: white;
}

.stream-url {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 添加HTTP iframe样式 */
.http-iframe-player {
  width: 100%;
  height: 100%;
  position: relative;
}

.device-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: #000;
}

.error-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin-top: 12px;
}
</style>