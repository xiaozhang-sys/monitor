<template>
  <div class="device-test">
    <h2>设备测试页面</h2>
    <div v-if="loading">加载中...</div>
    <div v-else>
      <h3>设备数量: {{ devices.length }}</h3>
      <div v-for="device in devices" :key="device.id" class="device-item">
        <strong>{{ device?.name || '未知设备' }}</strong>
        <br>区域: {{ device?.region || '未知区域' }} - {{ device?.store || '未知门店' }}
        <br>IP: {{ device?.ip || '未知IP' }}:{{ device?.port || '未知端口' }}
        <br>状态: {{ device?.status || '未知状态' }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useDevicesStore } from '@/stores/devices'

const devicesStore = useDevicesStore()
const devices = ref([])
const loading = ref(true)

onMounted(async () => {
  console.log('设备测试页面加载...')
  await devicesStore.fetchDevices()
  devices.value = devicesStore.devices
  loading.value = false
  console.log('设备数据:', devices.value)
})
</script>

<style scoped>
.device-test {
  padding: 20px;
}
.device-item {
  border: 1px solid #ccc;
  margin: 10px 0;
  padding: 10px;
  border-radius: 4px;
}
</style>