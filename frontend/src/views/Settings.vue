<template>
  <div>
    <el-card>
      <template #header>
        <span>系统设置</span>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="系统信息" name="info">
          <el-descriptions title="系统信息" :column="2" border>
            <el-descriptions-item label="系统名称">零售天眼通</el-descriptions-item>
            <el-descriptions-item label="版本">v1.0.0</el-descriptions-item>
            <el-descriptions-item label="运行时间">{{ uptime }}</el-descriptions-item>
            <el-descriptions-item label="在线设备">{{ onlineDevices }} / {{ totalDevices }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        
        <el-tab-pane label="用户管理" name="users">
          <el-table :data="users" style="width: 100%">
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="role" label="角色" />
            <el-table-column prop="created_at" label="创建时间" />
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="流媒体配置" name="streaming">
          <el-form label-width="120px">
            <el-form-item label="RTMP地址">
              <el-input v-model="streamingConfig.rtmpUrl" readonly />
            </el-form-item>
            <el-form-item label="HTTP-FLV地址">
              <el-input v-model="streamingConfig.flvUrl" readonly />
            </el-form-item>
            <el-form-item label="WebRTC地址">
              <el-input v-model="streamingConfig.webrtcUrl" readonly />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDevicesStore } from '@/stores/devices'

const devicesStore = useDevicesStore()
const activeTab = ref('info')

const uptime = ref('00:00:00')
const users = ref([
  { username: 'admin', role: '管理员', created_at: '2024-01-01 00:00:00' }
])

const streamingConfig = ref({
  rtmpUrl: 'rtmp://localhost:1935/live',
  flvUrl: 'http://localhost:8085/live/[stream].flv',
  webrtcUrl: 'webrtc://localhost:8085/live/[stream]'
})

const onlineDevices = computed(() => {
  return devicesStore.devices.filter(device => device.status === 'online').length
})

const totalDevices = computed(() => {
  return devicesStore.devices.length
})

const updateUptime = () => {
  const startTime = new Date()
  setInterval(() => {
    const now = new Date()
    const diff = Math.floor((now - startTime) / 1000)
    const hours = Math.floor(diff / 3600).toString().padStart(2, '0')
    const minutes = Math.floor((diff % 3600) / 60).toString().padStart(2, '0')
    const seconds = (diff % 60).toString().padStart(2, '0')
    uptime.value = `${hours}:${minutes}:${seconds}`
  }, 1000)
}

onMounted(() => {
  devicesStore.fetchDevices()
  updateUptime()
})
</script>