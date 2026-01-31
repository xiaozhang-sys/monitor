import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useDevicesStore = defineStore('devices', () => {
  const devices = ref([])
  const regions = ref([])
  const loading = ref(false)

  const fetchDevices = async () => {
  loading.value = true
  try {
    // 直接获取设备数据，依赖路由守卫的认证检查
    const response = await api.get('/devices')
    devices.value = response.data
    console.log('成功获取设备数据:', devices.value.length, '个设备')
  } catch (error) {
    console.error('获取设备列表失败:', error)
    if (error.response?.status === 401) {
      // 401错误由路由守卫统一处理，这里不再重复处理
      console.error('认证失败，将跳转到登录页')
    }
  } finally {
    loading.value = false
  }
}

  const fetchRegions = async () => {
    try {
      const response = await api.get('/regions')
      regions.value = response.data
    } catch (error) {
      console.error('获取区域列表失败:', error)
    }
  }

  const addDevice = async (device) => {
    try {
      const response = await api.post('/import', device)
      await fetchDevices()
      return { success: true, data: response.data }
    } catch (error) {
      return { success: false, message: error.response?.data?.detail || '添加失败' }
    }
  }

  const updateDevice = async (id, device) => {
    try {
      await api.put(`/devices/${id}`, device)
      await fetchDevices()
      return { success: true }
    } catch (error) {
      return { success: false, message: error.response?.data?.detail || '更新失败' }
    }
  }

  const deleteDevice = async (id) => {
    try {
      await api.delete(`/devices/${id}`)
      await fetchDevices()
      return { success: true }
    } catch (error) {
      return { success: false, message: error.response?.data?.detail || '删除失败' }
    }
  }

  const getDeviceById = (id) => {
    return devices.value.find(device => device.id === id)
  }

  const getDevicesByRegion = (region) => {
    return devices.value.filter(device => device.region === region)
  }

  return {
    devices,
    regions,
    loading,
    fetchDevices,
    fetchRegions,
    addDevice,
    updateDevice,
    deleteDevice,
    getDeviceById,
    getDevicesByRegion
  }
})