<template>
  <div class="video-test-view">
    <h1>视频设备播放测试</h1>
    
    <el-form ref="deviceForm" :model="deviceForm" label-width="120px">
      <el-form-item label="设备协议">
        <el-select v-model="deviceForm.protocol" placeholder="请选择协议">
          <el-option label="HTTP" value="http"></el-option>
          <el-option label="HTTPS" value="https"></el-option>
          <el-option label="RTSP" value="rtsp"></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="设备IP">
        <el-input v-model="deviceForm.ip" placeholder="请输入设备IP地址"></el-input>
      </el-form-item>
      
      <el-form-item label="端口">
        <el-input v-model.number="deviceForm.port" placeholder="请输入端口号"></el-input>
      </el-form-item>
      
      <el-form-item label="用户名">
        <el-input v-model="deviceForm.user" placeholder="请输入设备用户名"></el-input>
      </el-form-item>
      
      <el-form-item label="密码">
        <el-input v-model="deviceForm.pwd" type="password" placeholder="请输入设备密码"></el-input>
      </el-form-item>
      
      <el-form-item label="通道号">
        <el-input v-model.number="deviceForm.chs" placeholder="请输入通道号" :value="1"></el-input>
      </el-form-item>
      
      <el-form-item label="设备品牌">
        <el-select v-model="deviceForm.brand" placeholder="请选择设备品牌">
          <el-option label="海康威视" value="hikvision"></el-option>
          <el-option label="大华" value="dahua"></el-option>
          <el-option label="其他品牌" value="other"></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="testVideo">测试视频播放</el-button>
        <el-button @click="resetForm">重置</el-button>
      </el-form-item>
    </el-form>
    
    <div v-if="testDevice" class="test-result">
      <h2>测试结果</h2>
      <div class="video-container">
        <SmartVideoPlayer :device="testDevice" />
      </div>
      <div class="debug-info">
        <h3>调试信息</h3>
        <pre>{{ JSON.stringify(testDevice, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import SmartVideoPlayer from '@/components/SmartVideoPlayer.vue'

// 表单数据
const deviceForm = reactive({
  protocol: 'http',
  ip: '',
  port: '',
  user: '',
  pwd: '',
  chs: 1,
  brand: 'hikvision'
})

// 测试设备数据
const testDevice = ref(null)

// 测试视频播放
const testVideo = () => {
  if (!deviceForm.ip) {
    alert('请输入设备IP地址')
    return
  }
  
  // 构建测试设备对象
  const device = {
    id: 'test-device-1',
    name: '测试设备',
    protocol: deviceForm.protocol,
    ip: deviceForm.ip,
    port: deviceForm.port || (deviceForm.protocol === 'https' ? 443 : 80),
    user: deviceForm.user,
    pwd: deviceForm.pwd,
    chs: deviceForm.chs || 1,
    // 根据品牌设置特定路径
    http_path: getBrandPath(deviceForm.brand, deviceForm.chs || 1)
  }
  
  testDevice.value = device
}

// 根据品牌获取路径
const getBrandPath = (brand, channel) => {
  switch (brand) {
    case 'hikvision':
      return `/ISAPI/Streaming/channels/${channel * 100 + 1}/httppreview`
    case 'dahua':
      return `/cam/realmonitor?channel=${channel}&subtype=0`
    default:
      return ''
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(deviceForm, {
    protocol: 'http',
    ip: '',
    port: '',
    user: '',
    pwd: '',
    chs: 1,
    brand: 'hikvision'
  })
  testDevice.value = null
}
</script>

<style scoped>
.video-test-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.video-container {
  width: 100%;
  height: 500px;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
  margin: 20px 0;
}

.debug-info {
  margin-top: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 4px;
}

pre {
  white-space: pre-wrap;
  word-break: break-all;
  font-size: 12px;
  line-height: 1.5;
}
</style>