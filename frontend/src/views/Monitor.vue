<template>
  <div class="monitor-container">
    <el-row :gutter="20">
      <el-col :span="4">
        <el-card class="region-card">
          <template #header>
            <span>区域选择</span>
          </template>
          <el-tree
            :data="regionTree"
            :props="{ label: 'label', children: 'children' }"
            @node-click="handleNodeClick"
            highlight-current
          />
        </el-card>
      </el-col>
      
      <el-col :span="20">


        <!-- 通道配置和布局控制 -->
      <div style="margin-bottom: 10px;">
        <el-card style="margin: 0;">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>
                通道配置 
                <span v-if="selectedNVR" style="font-size: 12px; color: #666;">
                  {{ selectedNVR?.name || '未知设备' }} ({{ selectedChannels.length }}/{{ availableChannels.length }})
                </span>
              </span>
              <div style="display: flex; align-items: center; gap: 10px;">
                  <span style="font-size: 12px; color: #666;">画面数：</span>
                  <el-select
                    v-model="gridLayout"
                    @change="currentPage = 1"
                    style="width: 70px;"
                    size="small"
                  >
                    <el-option :label="1" :value="1" />
                    <el-option :label="2" :value="2" />
                    <el-option :label="4" :value="4" />
                    <el-option :label="6" :value="6" />
                    <el-option :label="8" :value="8" />
                    <el-option :label="9" :value="9" />
                    <el-option :label="12" :value="12" />
                    <el-option :label="16" :value="16" />
                  </el-select>
                  <el-button 
                    size="small" 
                    type="primary" 
                    :loading="loadingStatus"
                    @click="refreshStatus"
                    style="margin-left: 10px;"
                  >
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                <div @click="configCollapsed = !configCollapsed" style="cursor: pointer; display: flex; align-items: center;">
                  <el-icon>
                    <ArrowDown v-if="configCollapsed" />
                    <ArrowUp v-else />
                  </el-icon>
                </div>
              </div>
            </div>
          </template>
          
          <el-collapse-transition>
            <div v-show="!configCollapsed">
              <!-- NVR设备选择 -->
              <div style="margin-bottom: 8px; display: flex; gap: 8px; align-items: flex-start;">
                <div style="flex: 1; min-width: 150px; max-width: 180px;">
                  <el-select
                    v-model="selectedNVR"
                    placeholder="选择NVR设备"
                    @change="onNVRSelect"
                    style="width: 100%;"
                    size="small"
                  >
                    <el-option
                       v-for="nvr in nvrDevices"
                       :key="nvr?.id || ''"
                       :label="nvr?.name || '未知设备'"
                       :value="nvr"
                     />
                  </el-select>
                </div>
                <div style="display: flex; gap: 4px; width: 120px;">
                  <el-button size="mini" @click="selectAllChannels" style="flex: 1; padding: 4px 6px; font-size: 11px;">全选</el-button>
                  <el-button size="mini" @click="clearAllChannels" style="flex: 1; padding: 4px 6px; font-size: 11px;">清空</el-button>
                </div>
              </div>

              <!-- 通道选择 -->
              <div v-if="selectedNVR">
                <div class="channel-selector" style="max-height: 120px; overflow-y: auto;">
                  <el-checkbox
                    v-for="channel in availableChannels"
                    :key="channel.id"
                    :label="channel.id"
                    v-model="selectedChannels"
                    size="small"
                  >
                    <span style="font-size: 12px;">
                      {{ channel.number }}
                      <el-tag
                        :type="channel.status === 'online' ? 'success' : 'danger'"
                        size="mini"
                        style="margin-left: 2px; font-size: 10px;"
                      >
                        {{ channel.status === 'online' ? '在线' : '离线' }}
                      </el-tag>
                    </span>
                  </el-checkbox>
                </div>
              </div>
            </div>
          </el-collapse-transition>
        </el-card>
      </div>





        <!-- 加载状态 -->
        <div v-if="!devicesLoaded" class="loading-container">
          <el-loading text="正在加载设备数据..." />
        </div>

        <!-- 监控画面区域 -->
        <div v-else class="monitor-grid layout-dynamic" :style="gridStyle">
          <!-- NVR设备网格视图 -->
          <template v-if="selectedNVR">
            <div
              v-for="channel in paginatedChannels"
              :key="channel.id"
              class="camera-item"
              :class="{ 
                'fullscreen': isFullscreen === channel.id,
                'online': channel.status === 'online',
                'offline': channel.status === 'offline'
              }"
            >
              <div class="camera-header">
                 <span>{{ selectedNVR?.name || '未知设备' }} - 通道{{ channel.number }}</span>
                 <div class="camera-controls">
                   <el-button size="mini" circle @click="toggleFullscreen(channel.id)">
                     <el-icon><FullScreen /></el-icon>
                   </el-button>
                   <el-tag 
                     :type="channel.status === 'online' ? 'success' : 'danger'" 
                     size="mini"
                     :effect="channel.status === 'online' ? 'light' : 'plain'"
                   >
                     <span class="status-indicator" :class="channel.status"></span>
                     {{ channel.status === 'online' ? '在线' : '离线' }}
                   </el-tag>
                 </div>
               </div>
              <SmartVideoPlayer
                v-if="channel.device && channel.device.id"
                :device="channel.device"
                @loaded="onVideoLoaded"
                @error="onVideoError"
              />
            </div>
          </template>
          
          <!-- 普通设备网格视图 -->
          <template v-else-if="filteredRegularCameras.length > 0">
            <div
              v-for="device in paginatedRegularDevices"
              :key="device.id"
              class="camera-item"
              :class="{ 
                'fullscreen': isFullscreen === device.id,
                'online': device.status === 'online',
                'offline': device.status === 'offline'
              }"
            >
              <div class="camera-header">
                 <span>{{ device?.name || '未知设备' }}</span>
                 <div class="camera-controls">
                   <el-button size="mini" circle @click="toggleFullscreen(device.id)">
                     <el-icon><FullScreen /></el-icon>
                   </el-button>
                   <el-tag 
                     :type="device.status === 'online' ? 'success' : 'danger'" 
                     size="mini"
                     :effect="device.status === 'online' ? 'light' : 'plain'"
                   >
                     <span class="status-indicator" :class="device.status"></span>
                     {{ device.status === 'online' ? '在线' : '离线' }}
                   </el-tag>
                 </div>
               </div>
              <SmartVideoPlayer
                v-if="device && device.id"
                :device="device"
                @loaded="onVideoLoaded"
                @error="onVideoError"
              />
            </div>
          </template>
          
          <!-- 无设备提示 -->
          <template v-else>
            <div class="no-devices">
              <el-empty description="暂无可用设备" />
            </div>
          </template>
        </div>

        <!-- 分页控制 -->
        <div v-if="totalPages > 1" class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="selectedChannels.length"
          layout="prev, pager, next, jumper"
          @current-change="handlePageChange"
        />
      </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useDevicesStore } from '@/stores/devices'
import { 
  Warning, 
  FullScreen, 
  Close, 
  ArrowLeft, 
  ArrowRight,
  ArrowDown,
  ArrowUp,
  Refresh
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import SmartVideoPlayer from '../components/SmartVideoPlayer.vue'
import { handleApiError, retryOperation } from '@/utils/errorHandler.js'
import api from '@/utils/api'

const devicesStore = useDevicesStore()

// 显示控制
const currentPage = ref(1)
const gridLayout = ref(4) // 默认4画面
const pageSize = computed(() => gridLayout.value)
const configCollapsed = ref(false) // 通道配置折叠状态
const devicesLoaded = ref(false) // 设备数据加载状态

// NVR相关
const selectedNVR = ref(null)
const selectedChannels = ref([])

// 全屏控制
const isFullscreen = ref(null)

// 区域选择
const selectedRegion = ref('')
const selectedStore = ref('')

// 状态管理
const deviceStatus = ref({})
const loadingStatus = ref(false)

// 计算属性
// 修复nvrDevices计算属性中的空值检查
const nvrDevices = computed(() => {
  let devices = devicesStore.devices.filter(device => {
    if (!device || !device.id) return false
    const hasMultipleChannels = (device.chs || 1) > 1
    const isNVR = device?.name && device.name.includes('录像机')
    return hasMultipleChannels || isNVR
  }).map(device => ({
    ...device,
    name: decodeUnicode(device?.name || '未知设备'),
    region: decodeUnicode(device?.region || '未知区域'),
    store: decodeUnicode(device?.store || '未知门店')
  }))
  
  // 根据选择的区域和门店筛选
  if (selectedRegion.value) {
    devices = devices.filter(device => device.region === selectedRegion.value)
  }
  
  if (selectedStore.value) {
    devices = devices.filter(device => device.store === selectedStore.value)
  }
  
  return devices
})

// 修复regularDevices计算属性中的空值检查
const regularDevices = computed(() => {
  return devicesStore.devices.filter(device => {
    if (!device || !device.id) return false
    const isSingleChannel = (device.chs || 1) <= 1
    const isNotNVR = !device?.name || !device.name.includes('录像机')
    return isSingleChannel && isNotNVR
  }).map(device => ({
    ...device,
    name: decodeUnicode(device?.name || '未知设备'),
    region: decodeUnicode(device?.region || '未知区域'),
    store: decodeUnicode(device?.store || '未知门店')
  }))
})

// 修复availableChannels计算属性中的空值检查
// 修复availableChannels计算属性中的通道号传递
const availableChannels = computed(() => {
  if (!selectedNVR.value) return []
  
  const chs = selectedNVR.value.chs || 1
  const channels = []
  
  for (let i = 1; i <= chs; i++) {
    // 使用真实设备状态
    const deviceId = selectedNVR.value.id
    const channelId = `${deviceId}_ch${i}`
    
    // 获取真实设备状态
    const realStatus = deviceStatus.value[deviceId] || 
                      (selectedNVR.value.status === 'online' ? 'online' : 'offline')
    
    channels.push({
      id: channelId,
      number: i,
      status: realStatus,
      device: {
        ...selectedNVR.value,
        channel: i,  // 使用channel字段表示实际通道号
        name: `${selectedNVR.value?.name || '未知设备'} - 通道${i}`
      }
    })
  }
  
  return channels
})

// 修复filteredRegularCameras计算属性中的空值检查
const filteredRegularCameras = computed(() => {
  let cameras = regularDevices.value
  
  if (selectedRegion.value) {
    cameras = cameras.filter(device => {
      const decodedRegion = decodeUnicode(device?.region || '未知区域')
      return decodedRegion === selectedRegion.value
    })
  }
  
  if (selectedStore.value) {
    cameras = cameras.filter(device => {
      const decodedStore = decodeUnicode(device?.store || '未知门店')
      return decodedStore === selectedStore.value
    })
  }
  
  return cameras
})

const hasNVRDevices = computed(() => nvrDevices.value.length > 0)





const selectedChannelObjects = computed(() => {
  return availableChannels.value.filter(ch => selectedChannels.value.includes(ch.id))
})





const paginatedRegularDevices = computed(() => {
  const devices = filteredRegularCameras.value
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return devices.slice(start, end)
})

const paginatedChannels = computed(() => {
  const channels = selectedChannelObjects.value
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return channels.slice(start, end)
})

const gridStyle = computed(() => {
  const layout = gridLayout.value
  
  if (layout === 1) return { gridTemplateColumns: '1fr', gridTemplateRows: '1fr' }
  if (layout === 2) return { gridTemplateColumns: 'repeat(2, 1fr)', gridTemplateRows: '1fr' }
  if (layout === 4) return { gridTemplateColumns: 'repeat(2, 1fr)', gridTemplateRows: 'repeat(2, 1fr)' }
  if (layout === 6) return { gridTemplateColumns: 'repeat(3, 1fr)', gridTemplateRows: 'repeat(2, 1fr)' }
  if (layout === 8) return { gridTemplateColumns: 'repeat(4, 1fr)', gridTemplateRows: 'repeat(2, 1fr)' }
  if (layout === 9) return { gridTemplateColumns: 'repeat(3, 1fr)', gridTemplateRows: 'repeat(3, 1fr)' }
  if (layout === 12) return { gridTemplateColumns: 'repeat(4, 1fr)', gridTemplateRows: 'repeat(3, 1fr)' }
  if (layout === 16) return { gridTemplateColumns: 'repeat(4, 1fr)', gridTemplateRows: 'repeat(4, 1fr)' }
  return { gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gridAutoRows: '1fr' }
})

const totalPages = computed(() => {
  if (selectedNVR.value) {
    return Math.ceil(selectedChannels.value.length / pageSize.value)
  } else {
    return Math.ceil(filteredRegularCameras.value.length / pageSize.value)
  }
})



const regionTree = computed(() => {
  const tree = []
  const regions = {}
  
  devicesStore.devices.forEach(device => {
    if (!device || !device.id) return
    
    const decodedRegion = decodeUnicode(device.region || '未知区域')
    const decodedStore = decodeUnicode(device.store || '未知门店')
    
    if (!decodedRegion || !decodedStore) return
    
    if (!regions[decodedRegion]) {
      regions[decodedRegion] = {
        label: decodedRegion,
        children: []
      }
      tree.push(regions[decodedRegion])
    }
    
    const storeExists = regions[decodedRegion].children.find(
      store => store.label === decodedStore
    )
    
    if (!storeExists) {
      regions[decodedRegion].children.push({
        label: decodedStore,
        region: decodedRegion,
        store: decodedStore
      })
    }
  })
  
  return tree
})

// 工具函数
const decodeUnicode = (text) => {
  if (!text) return ''
  return text.replace(/\\u([0-9a-fA-F]{4})/g, (match, hex) => 
    String.fromCharCode(parseInt(hex, 16))
  )
}

// 方法
const handleNodeClick = (data) => {
  if (data.region) {
    selectedRegion.value = data.region
    selectedStore.value = data.store
    
    // 检查是否为NVR设备
    const nvr = nvrDevices.value.find(device => {
        const decodedRegion = decodeUnicode(device.region)
        const decodedStore = decodeUnicode(device.store)
        return decodedRegion === data.region && decodedStore === data.store
      })
    if (nvr) {
      selectedNVR.value = nvr
      // 修复：统一行为，不默认选择任何通道，让用户手动选择
      selectedChannels.value = [] // 清空已选通道，不默认选择任何通道
    } else {
      // 如果是普通设备区域，取消NVR选择
      selectedNVR.value = null
    }
  } else {
    selectedRegion.value = data.label
    selectedStore.value = ''
    selectedNVR.value = null // 取消NVR选择
  }
}

const toggleFullscreen = (cameraId) => {
  isFullscreen.value = isFullscreen.value === cameraId ? null : cameraId
}

const handlePageChange = (page) => {
  currentPage.value = page
}

const onNVRSelect = (selectedValue) => {
  // 处理可能接收到的是对象或id的情况
  const nvr = typeof selectedValue === 'object' ? selectedValue : 
              nvrDevices.value.find(n => n.id === selectedValue)
  if (nvr) {
    selectedNVR.value = nvr
    selectedChannels.value = []  // 清空已选通道
    currentPage.value = 1
    // 移除自动全选，改为让用户手动选择通道
    
    // 选择NVR时立即检查该设备状态
    checkSingleDeviceStatus(nvr.id)
  }
}

const checkSingleDeviceStatus = async (deviceId) => {
  try {
    const response = await retryOperation(() => api.post(`/devices/${deviceId}/check-status`))
    
    const result = response.data
    if (result && result.status) {
      deviceStatus.value[deviceId] = result.status
      
      // 更新设备存储中的状态
      const device = devicesStore.devices.find(d => d.id === deviceId)
      if (device) {
        device.status = result.status
        device.last_seen = result.checked_at
      }
      
      console.log(`设备 ${deviceId} 状态检查完成: ${result.status}`)
    }
  } catch (error) {
    console.error(`检查设备 ${deviceId} 状态失败:`, error)
    // 使用现有状态
    const device = devicesStore.devices.find(d => d.id === deviceId)
    if (device && device.id) {
      deviceStatus.value[deviceId] = device.status || 'offline'
    }
    
    // 显示用户友好的错误消息
    const errorMessage = handleApiError(error, '检查设备状态失败')
    if (errorMessage) {
      ElMessage.error(errorMessage)
    }
  }
}

const selectAllChannels = () => {
  if (selectedNVR.value) {
    selectedChannels.value = availableChannels.value.map(ch => ch.id)
  }
}

const clearAllChannels = () => {
  selectedChannels.value = []
}

const refreshStatus = async () => {
  loadingStatus.value = true
  try {
    // 调用真实的设备状态检查API，添加重试机制
    const response = await retryOperation(() => api.post('/devices/check-all-status'))
    
    // 获取正确的数据格式 - 可能是数组或包含results的对象
    let responseData = response.data
    let results = []
    
    if (responseData && typeof responseData === 'object') {
      if (Array.isArray(responseData)) {
        results = responseData
      } else if (responseData.results && Array.isArray(responseData.results)) {
        results = responseData.results
      }
    }
    
    // 确保results是数组
    if (!Array.isArray(results)) {
      console.warn('API返回的数据格式不正确，期望数组但收到:', typeof results)
      results = []
    }
    
    // 更新设备状态
    for (const result of results) {
      if (result && result.device_id && result.status) {
        deviceStatus.value[result.device_id] = result.status
        
        // 同时更新设备存储中的状态
        const device = devicesStore.devices.find(d => d.id === result.device_id)
        if (device) {
          device.status = result.status
          device.last_seen = result.checked_at
        }
      }
    }
    
    console.log('设备状态更新完成:', results)
    
    // 显示成功消息
    if (results.length > 0) {
      ElMessage.success(`成功更新 ${results.length} 个设备的状态`)
    } else {
      ElMessage.warning('没有设备需要更新状态')
    }
  } catch (error) {
      // 401错误由路由守卫处理
      if (error.response?.status === 401) {
        console.warn('认证失败，将由系统统一处理')
        return
      }
      
      console.error('刷新状态失败:', error)
      
      // 如果API调用失败，使用设备存储中的状态
      for (const device of devicesStore.devices) {
        if (device && device.id) {
          deviceStatus.value[device.id] = device.status || 'offline'
        }
      }
      
      // 显示用户友好的错误提示
      const errorMessage = handleApiError(error, '刷新设备状态失败')
      if (errorMessage) {
        ElMessage.error(errorMessage)
      }
    } finally {
      loadingStatus.value = false
    }
}

// 初始化
onMounted(() => {
  if (nvrDevices.value.length > 0) {
    selectedNVR.value = nvrDevices.value[0]
  }
})

const onVideoLoaded = (camera) => {
  console.log('视频加载成功:', camera?.name || '未知设备')
}

const onVideoError = (error) => {
  console.error('视频加载失败:', error)
  ElMessage.error(`视频加载失败: ${error.message || '未知错误'}`)
}

const onChannelLoaded = (channel) => {
  console.log('通道视频加载成功:', channel.id)
}

const onChannelError = (error) => {
  console.error('通道视频加载失败:', error)
  ElMessage.error(`通道加载失败: ${error.message || '未知错误'}`)
}

// 定时刷新设备状态
let statusInterval = null

const startStatusPolling = () => {
  // 立即执行一次状态检查
  refreshStatus()
  
  // 设置定时器，每10分钟检查一次
  statusInterval = setInterval(() => {
    refreshStatus()
  }, 600000)
}

const stopStatusPolling = () => {
  if (statusInterval) {
    clearInterval(statusInterval)
    statusInterval = null
  }
}

// 初始化
onMounted(async () => {
  console.log('监控页面加载，开始获取设备数据...')
  try {
    await devicesStore.fetchDevices()
    console.log('设备数据获取完成，设备数量:', devicesStore.devices.length)
    
    // 初始化设备状态
    for (const device of devicesStore.devices) {
      deviceStatus.value[device.id] = device.status || 'offline'
    }
    
    // 标记设备数据已加载
    devicesLoaded.value = true
    
    // 启动状态轮询
    startStatusPolling()
    
    console.log('监控页面初始化完成')
  } catch (error) {
    console.error('设备数据加载失败:', error)
    ElMessage.error('设备数据加载失败，请刷新页面重试')
  }
})

// 页面卸载时清理定时器
onUnmounted(() => {
  stopStatusPolling()
})
</script>

<style scoped>
.monitor-container {
  height: calc(100vh - 120px);
}

.region-card {
  height: calc(100vh - 120px);
  overflow-y: auto;
}

.display-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.mb-4 {
  margin-bottom: 16px;
}

.ml-4 {
  margin-left: 16px;
}

.channel-selector {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 8px;
  padding: 5px;
}

.channel-checkbox {
  margin-right: 0;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
  background: #1a1a1a;
  border-radius: 8px;
}

.monitor-grid {
  display: grid;
  gap: 10px;
  height: calc(100vh - 250px);
  overflow-y: auto;
}

.monitor-grid.layout-1 {
  grid-template-columns: 1fr;
  grid-template-rows: 1fr;
}

.monitor-grid.layout-4 {
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(2, 1fr);
}

.monitor-grid.layout-9 {
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);
}

.monitor-grid.layout-16 {
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(4, 1fr);
}

.monitor-grid.layout-36 {
  grid-template-columns: repeat(6, 1fr);
  grid-template-rows: repeat(6, 1fr);
}



.camera-item,
.channel-item {
  background: #1a1a1a;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
  border: 1px solid #333;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.camera-item:hover,
.channel-item:hover {
  border-color: #409EFF;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.4);
  transform: translateY(-1px);
}

.camera-item.online {
  border-color: #67C23A;
  box-shadow: 0 2px 8px rgba(103, 194, 58, 0.2);
}

.camera-item.offline {
  border-color: #F56C6C;
  box-shadow: 0 2px 8px rgba(245, 108, 108, 0.2);
}

/* 通道状态样式 */
.channel-item.channel-online {
  border-color: #67C23A;
  box-shadow: 0 2px 8px rgba(103, 194, 58, 0.3);
}

.channel-item.channel-offline {
  border-color: #F56C6C;
  box-shadow: 0 2px 8px rgba(245, 108, 108, 0.3);
}

/* 状态指示器 */
.status-indicator {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 4px;
  animation: pulse 2s infinite;
}

.status-indicator.online {
  background-color: #67C23A;
  box-shadow: 0 0 0 0 rgba(103, 194, 58, 0.7);
}

.status-indicator.offline {
  background-color: #F56C6C;
  animation: none;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(103, 194, 58, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(103, 194, 58, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(103, 194, 58, 0);
  }
}

.camera-item.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
}

.camera-header,
.channel-header,
.single-header {
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.8) 0%, rgba(30, 30, 30, 0.8) 100%);
  color: white;
  padding: 10px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  min-height: 42px;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.camera-name {
  font-weight: 600;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  font-size: 13px;
  letter-spacing: 0.3px;
}

.camera-name {
  font-weight: bold;
}

.camera-controls,
.single-controls {
  display: flex;
  gap: 4px;
}

.channel-video,
.single-video {
  flex: 1;
  position: relative;
}

.single-camera {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.single-video {
  flex: 1;
  background: #000;
  border-radius: 4px;
  overflow: hidden;
}

.channel-item.channel-4 {
  grid-column: span 2;
  grid-row: span 2;
}

.channel-item.channel-9 {
  grid-column: span 3;
  grid-row: span 3;
}

.channel-item.channel-16 {
  grid-column: span 4;
  grid-row: span 4;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

/* 响应式布局 - 优化多画面显示 */
@media (max-width: 768px) {
  .monitor-grid {
    grid-template-columns: 1fr !important;
    grid-template-rows: repeat(auto-fit, minmax(200px, 1fr)) !important;
    gap: 8px;
  }
  
  .display-controls {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .camera-item,
  .channel-item {
    min-height: 200px;
  }
}

@media (min-width: 769px) and (max-width: 1200px) {
  .monitor-grid {
    gap: 8px;
  }
  
  .monitor-grid.layout-4 {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(2, 1fr);
  }
  
  .monitor-grid.layout-9 {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(5, 1fr);
  }
  
  .monitor-grid.layout-16 {
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(6, 1fr);
  }
  
  .monitor-grid.layout-36 {
    grid-template-columns: repeat(4, 1fr);
    grid-template-rows: repeat(9, 1fr);
  }
}

@media (min-width: 1201px) {
  .monitor-grid {
    gap: 12px;
  }
  
  .camera-item,
  .channel-item {
    min-height: 180px;
  }
}

/* 动态布局 - 根据通道数量自适应 */
.monitor-grid.layout-dynamic {
  display: grid;
  gap: 10px;
  height: calc(100vh - 250px);
  overflow-y: auto;
}

/* 智能布局 - 根据实际内容数量 */
.monitor-grid.layout-dynamic {
  display: grid;
  gap: 10px;
  height: calc(100vh - 250px);
  overflow-y: auto;
}

/* 响应式网格布局 */
@media (max-width: 768px) {
  .monitor-grid.layout-dynamic {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(auto-fit, minmax(200px, 1fr));
  }
}

@media (min-width: 769px) and (max-width: 1200px) {
  .monitor-grid.layout-dynamic {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    grid-auto-rows: 1fr;
  }
}

@media (min-width: 1201px) {
  .monitor-grid.layout-dynamic {
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    grid-auto-rows: 1fr;
  }
}

/* 当选择少量通道时的特殊布局 */
@media (min-width: 769px) {
  .monitor-grid.layout-dynamic[style*="grid-template-columns"] {
    /* 允许通过style属性动态设置 */
  }
}



/* 滚动条样式 */
.monitor-grid::-webkit-scrollbar {
  width: 8px;
}

.monitor-grid::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.monitor-grid::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}
.monitor-grid::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.no-devices {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

</style>
