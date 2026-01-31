<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>设备管理</span>
          <div style="display: flex; align-items: center; gap: 10px;">
            <!-- 下拉选择框 -->
            <el-select v-model="selectedRegion" placeholder="选择区域" style="width: 120px;">
              <el-option label="全部区域" value="" />
              <el-option v-for="region in uniqueRegions" :key="region" :label="region" :value="region" />
            </el-select>
            <el-select v-model="selectedStore" placeholder="选择门店" style="width: 120px;">
              <el-option label="全部门店" value="" />
              <el-option v-for="store in filteredStores" :key="store" :label="store" :value="store" />
            </el-select>
            <el-select v-model="selectedStatus" placeholder="选择状态" style="width: 100px;">
              <el-option label="全部状态" value="" />
              <el-option label="在线" value="online" />
              <el-option label="离线" value="offline" />
            </el-select>
            <!-- 搜索框 -->
            <el-input
              v-model="searchKeyword"
              placeholder="搜索设备名称/IP"
              style="width: 200px;"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="success" @click="checkAllDevices" :loading="checkingStatus">
              <el-icon><Refresh /></el-icon>
              检查状态
            </el-button>
            <el-button type="primary" @click="showAddDialog = true">
              <el-icon><Plus /></el-icon>
              添加设备
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 设备统计卡片 -->
      <el-row :gutter="20" class="mb-4">
        <el-col :span="6">
          <el-card>
            <div class="stat-card">
              <div class="stat-number">{{ deviceStats.total || 0 }}</div>
              <div class="stat-label">总设备数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-card">
              <div class="stat-number online">{{ deviceStats.online || 0 }}</div>
              <div class="stat-label">在线设备</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-card">
              <div class="stat-number offline">{{ deviceStats.offline || 0 }}</div>
              <div class="stat-label">离线设备</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-card">
              <div class="stat-number rate">{{ deviceStats.onlineRate || 0 }}%</div>
              <div class="stat-label">在线率</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-table :data="paginatedDevices" style="width: 100%" v-loading="devicesStore.loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="设备名称" />
        <el-table-column prop="region" label="区域" />
        <el-table-column prop="store" label="门店" />
        <el-table-column prop="ip" label="IP地址" />
        <el-table-column prop="port" label="端口" width="80" />
        <el-table-column prop="chs" label="通道数" width="80" />
        <el-table-column prop="protocol" label="协议" width="80">
          <template #default="{ row }">
            <el-tag :type="row.protocol === 'rtsp' ? 'primary' : 'success'">
              {{ row.protocol?.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'online' ? 'success' : 'danger'">
              {{ row.status === 'online' ? '在线' : '离线' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="280">
          <template #default="{ row }">
            <el-button type="success" size="small" @click="checkSingleDevice(row)" :loading="row.checking">
              <el-icon><Refresh /></el-icon>
              检查
            </el-button>
            <el-button type="primary" size="small" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页控件 -->
      <div class="pagination-container" style="margin-top: 20px; text-align: right;">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="filteredDevices.length"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑设备对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingDevice ? '编辑设备' : '添加设备'"
      width="500px"
    >
      <el-form ref="deviceFormRef" :model="deviceForm" :rules="rules" label-width="100px">
        <el-form-item label="设备名称" prop="name">
          <el-input v-model="deviceForm.name" placeholder="请输入设备名称" />
        </el-form-item>
        <el-form-item label="区域" prop="region">
          <el-input v-model="deviceForm.region" placeholder="请输入区域" />
        </el-form-item>
        <el-form-item label="门店" prop="store">
          <el-input v-model="deviceForm.store" placeholder="请输入门店" />
        </el-form-item>
        <el-form-item label="IP地址" prop="ip">
          <el-input v-model="deviceForm.ip" placeholder="请输入IP地址" />
        </el-form-item>
        <el-form-item label="端口" prop="port">
          <el-input-number v-model="deviceForm.port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="用户名" prop="user">
          <el-input v-model="deviceForm.user" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="pwd">
          <el-input v-model="deviceForm.pwd" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="通道数" prop="chs">
          <el-input-number v-model="deviceForm.chs" :min="1" :max="32" />
        </el-form-item>
        <el-form-item label="协议类型" prop="protocol">
          <el-select v-model="deviceForm.protocol" placeholder="请选择协议类型">
            <el-option label="RTSP" value="rtsp" />
            <el-option label="HTTP" value="http" />
            <el-option label="HTTPS" value="https" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useDevicesStore } from '@/stores/devices'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus, Edit, Delete, Search } from '@element-plus/icons-vue'


const devicesStore = useDevicesStore()

// 新增：搜索和筛选相关变量
const searchKeyword = ref('')
const selectedRegion = ref('')
const selectedStore = ref('')
const selectedStatus = ref('')

// 新增：分页相关变量
const currentPage = ref(1)
const pageSize = ref(10)

const showAddDialog = ref(false)
const editingDevice = ref(null)
const submitting = ref(false)
const checkingStatus = ref(false)
const deviceFormRef = ref()
const deviceStats = ref({
  total: 0,
  online: 0,
  offline: 0,
  onlineRate: 0
})

const deviceForm = reactive({
  name: '',
  region: '',
  store: '',
  ip: '',
  port: 554,
  user: '',
  pwd: '',
  chs: 1,
  protocol: 'http'  // 默认为HTTP协议，方便添加HTTP设备
})

const rules = {
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  region: [{ required: true, message: '请输入区域', trigger: 'blur' }],
  store: [{ required: true, message: '请输入门店', trigger: 'blur' }],
  ip: [{ required: true, message: '请输入IP地址', trigger: 'blur' }],
  user: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  pwd: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

// 新增：计算属性 - 唯一区域列表
const uniqueRegions = computed(() => {
  const regions = new Set()
  devicesStore.devices.forEach(device => {
    if (device.region) {
      regions.add(device.region)
    }
  })
  return Array.from(regions)
})

// 新增：计算属性 - 根据区域筛选门店列表
const filteredStores = computed(() => {
  const stores = new Set()
  devicesStore.devices.forEach(device => {
    // 如果没有选择区域，或者设备区域与选择的区域匹配，则添加该设备的门店
    if ((!selectedRegion.value || device.region === selectedRegion.value) && device.store) {
      stores.add(device.store)
    }
  })
  return Array.from(stores)
})

// 新增：计算属性 - 筛选后的设备列表
const filteredDevices = computed(() => {
  return devicesStore.devices.filter(device => {
    // 区域筛选
    if (selectedRegion.value && device.region !== selectedRegion.value) {
      return false
    }
    // 门店筛选
    if (selectedStore.value && device.store !== selectedStore.value) {
      return false
    }
    // 状态筛选
    if (selectedStatus.value && device.status !== selectedStatus.value) {
      return false
    }
    // 关键词搜索
    if (searchKeyword.value) {
      const keyword = searchKeyword.value.toLowerCase()
      return (
        (device.name && device.name.toLowerCase().includes(keyword)) ||
        (device.ip && device.ip.toLowerCase().includes(keyword))
      )
    }
    return true
  })
})

// 新增：计算属性 - 分页后的设备列表
const paginatedDevices = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDevices.value.slice(start, end)
})

// 新增：分页处理函数
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1  // 重置为第一页
}

const handleCurrentChange = (current) => {
  currentPage.value = current
}

const resetForm = () => {
  Object.assign(deviceForm, {
    name: '',
    region: '',
    store: '',
    ip: '',
    port: 80,  // HTTP默认端口
    user: '',
    pwd: '',
    chs: 1,
    protocol: 'http'  // 默认为HTTP协议
  })
  editingDevice.value = null
}

const handleAdd = () => {
  resetForm()
  showAddDialog.value = true
}

const handleEdit = (device) => {
  editingDevice.value = device
  Object.assign(deviceForm, device)
  showAddDialog.value = true
}

const handleDelete = async (device) => {
  try {
    if (!device || !device.id || !device.name) {
      ElMessage.error('设备信息不完整，无法删除')
      return
    }
    
    await ElMessageBox.confirm(
      `确定要删除设备 "${device.name}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    const result = await retryOperation(() => devicesStore.deleteDevice(device.id))
    
    if (result.success) {
      ElMessage.success('删除成功')
      // 删除后重置分页状态
      currentPage.value = 1
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    if (error === 'cancel') {
      // 用户取消删除
      return
    }
    
    const errorMessage = handleApiError(error, '删除设备失败')
    ElMessage.error(errorMessage)
    console.error(error)
  }
}

import { handleApiError, retryOperation } from '@/utils/errorHandler.js'
import api from '@/utils/api'

const handleSubmit = async () => {
  if (!deviceFormRef.value) return
  
  await deviceFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        let result
        if (editingDevice.value) {
          result = await retryOperation(() => devicesStore.updateDevice(editingDevice.value.id, deviceForm))
        } else {
          result = await retryOperation(() => devicesStore.addDevice(deviceForm))
        }
        
        if (result.success) {
          ElMessage.success(editingDevice.value ? '更新成功' : '添加成功')
          showAddDialog.value = false
          resetForm()
          // 操作后重置分页状态
          currentPage.value = 1
        } else {
          ElMessage.error(result.message)
        }
      } catch (error) {
        // 401错误由路由守卫处理，这里不再显示提示
        if (error.response?.status === 401) {
          console.warn('认证失败，将由系统统一处理')
          return
        }
        
        const errorMessage = handleApiError(error, editingDevice.value ? '更新设备失败' : '添加设备失败')
        if (errorMessage) {
          ElMessage.error(errorMessage)
        }
        console.error(error)
      } finally {
        submitting.value = false
      }
    }
  })
}

const checkSingleDevice = async (device) => {
  try {
    if (!device || !device.id) {
      ElMessage.error('设备信息不完整，无法检查状态')
      return
    }
    
    device.checking = true
    const response = await retryOperation(() => api.post(`/devices/${device.id}/check-status`))
    
    if (response.data) {
      // 更新设备状态
      const index = devicesStore.devices.findIndex(d => d.id === device.id)
      if (index !== -1) {
        devicesStore.devices[index].status = response.data.status
      }
      
      ElMessage.success(
        `设备 ${response.data.name || `ID:${device.id}`} 状态: ${response.data.status === 'online' ? '在线' : '离线'}`
      )
    }
  } catch (error) {
      // 401错误由路由守卫处理
      if (error.response?.status === 401) {
        console.warn('认证失败，将由系统统一处理')
        return
      }
      
      const errorMessage = handleApiError(error, '检查设备状态失败')
      if (errorMessage) {
        ElMessage.error(errorMessage)
      }
      console.error(error)
    } finally {
    device.checking = false
  }
}

const checkAllDevices = async () => {
  try {
    checkingStatus.value = true
    const response = await retryOperation(() => api.post('/devices/check-all-status'))
    
    if (response.data && response.data.results) {
      // 更新所有设备状态
      response.data.results.forEach(result => {
        const index = devicesStore.devices.findIndex(d => d.id === result.device_id)
        if (index !== -1) {
          devicesStore.devices[index].status = result.status
        }
      })
      
      const onlineCount = response.data.results.filter(r => r.status === 'online').length
      ElMessage.success(`检查完成，${onlineCount}/${response.data.results.length} 设备在线`)
    } else {
      ElMessage.warning('未收到有效的设备状态数据')
    }
  } catch (error) {
    // 401错误由路由守卫处理
    if (error.response?.status === 401) {
      console.warn('认证失败，将由系统统一处理')
      return
    }
    
    const errorMessage = handleApiError(error, '检查设备状态失败')
    ElMessage.error(errorMessage)
    console.error(error)
  } finally {
    checkingStatus.value = false
  }
}

const fetchDeviceStats = async () => {
  try {
    const response = await api.get('/devices/stats')
    if (response.data) {
      deviceStats.value = response.data
    }
  } catch (error) {
    console.error('获取设备统计信息失败:', error)
  }
}



onMounted(() => {
  devicesStore.fetchDevices()
  fetchDeviceStats()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.stat-card {
  text-align: center;
  padding: 10px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-number.online {
  color: #67c23a;
}

.stat-number.offline {
  color: #f56c6c;
}

.stat-number.rate {
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.mb-4 {
  margin-bottom: 16px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>