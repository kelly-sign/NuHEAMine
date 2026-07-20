<template>
  <div class="system-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="system-info-card">
          <template #header>
            <div class="card-header">
              <span>System Status</span>
              <el-button 
                size="small"
                @click="refreshSystemInfo"
                :loading="refreshing"
              >
                Refresh
              </el-button>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="metric-card">
                <h3>CPU Usage</h3>
                <el-progress
                  type="dashboard"
                  :percentage="systemInfo.cpu?.usage_percent || 0"
                  :color="getProgressColor"
                />
                <div class="metric-info">
                  CPU Cores: {{ systemInfo.cpu?.count || 0 }}
                </div>
              </div>
            </el-col>
            
            <el-col :span="8">
              <div class="metric-card">
                <h3>Memory Usage</h3>
                <el-progress
                  type="dashboard"
                  :percentage="systemInfo.memory?.percent || 0"
                  :color="getProgressColor"
                />
                <div class="metric-info">
                  Total Memory: {{ formatBytes(systemInfo.memory?.total) }}
                  <br>
                  Available Memory: {{ formatBytes(systemInfo.memory?.free) }}
                </div>
              </div>
            </el-col>
            
            <el-col :span="8">
              <div class="metric-card">
                <h3>Disk Usage</h3>
                <el-progress
                  type="dashboard"
                  :percentage="systemInfo.disk?.percent || 0"
                  :color="getProgressColor"
                />
                <div class="metric-info">
                  Total Space: {{ formatBytes(systemInfo.disk?.total) }}
                  <br>
                  Available Space: {{ formatBytes(systemInfo.disk?.free) }}
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="24">
        <el-card class="log-card">
          <template #header>
            <div class="card-header">
              <span>System Logs</span>
              <div class="filter-group">
                <el-select
                  v-model="logFilter.level"
                  placeholder="Log level"
                  clearable
                >
                  <el-option label="Information" value="INFO" />
                  <el-option label="Warning" value="WARNING" />
                  <el-option label="Error" value="ERROR" />
                  <el-option label="Debug" value="DEBUG" />
                </el-select>
                
                <el-select
                  v-model="logFilter.type"
                  placeholder="Log type"
                  clearable
                >
                  <el-option label="User Actions" value="USER" />
                  <el-option label="System Actions" value="SYSTEM" />
                  <el-option label="Security" value="SECURITY" />
                  <el-option label="Performance" value="PERFORMANCE" />
                </el-select>
                
                <el-date-picker
                  v-model="logFilter.dateRange"
                  type="daterange"
                  range-separator="to"
                  start-placeholder="Start date"
                  end-placeholder="End date"
                />
                
                <el-button type="primary" @click="handleFilter">
                  Filter
                </el-button>
              </div>
            </div>
          </template>

          <el-table :data="logs" style="width: 100%">
            <el-table-column prop="created_at" label="Time" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="level" label="Level" width="100">
              <template #default="scope">
                <el-tag :type="getLogLevelType(scope.row.level)">
                  {{ scope.row.level }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="log_type" label="Type" width="120" />
            <el-table-column prop="message" label="Message" />
            <el-table-column prop="ip_address" label="IP Address" width="140" />
          </el-table>

          <div class="pagination">
            <el-pagination
              :current-page="currentPage"
              :page-size="pageSize"
              :total="total"
              @current-change="handleCurrentChange"
              layout="total, prev, pager, next"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const systemInfo = ref({})
const refreshing = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const logFilter = reactive({
  level: '',
  type: '',
  dateRange: []
})

const logs = ref([])

// 获取系统信息
const getSystemInfo = async () => {
  try {
    refreshing.value = true
    // TODO: 调用获取系统信息API
    // const res = await api.getSystemInfo()
    // systemInfo.value = res.data
    
    // 模拟数据
    systemInfo.value = {
      cpu: {
        usage_percent: 45,
        count: 8
      },
      memory: {
        total: 16 * 1024 * 1024 * 1024,
        used: 8 * 1024 * 1024 * 1024,
        free: 8 * 1024 * 1024 * 1024,
        percent: 50
      },
      disk: {
        total: 512 * 1024 * 1024 * 1024,
        used: 256 * 1024 * 1024 * 1024,
        free: 256 * 1024 * 1024 * 1024,
        percent: 50
      }
    }
  } catch (error) {
    ElMessage.error('Failed to load system information')
  } finally {
    refreshing.value = false
  }
}

// 获取系统日志
const getLogs = async () => {
  try {
    // TODO: 调用获取日志API
    // const res = await api.getLogs({
    //   page: currentPage.value,
    //   ...logFilter
    // })
    // logs.value = res.data.results
    // total.value = res.data.count
    
    // 模拟数据
    logs.value = [
      {
        id: 1,
        level: 'INFO',
        log_type: 'USER',
        message: 'User logged in successfully',
        ip_address: '192.168.1.1',
        created_at: '2024-03-20T10:00:00Z'
      }
    ]
    total.value = 100
  } catch (error) {
    ElMessage.error('Failed to load system logs')
  }
}

const refreshSystemInfo = () => {
  getSystemInfo()
}

const handleFilter = () => {
  currentPage.value = 1
  getLogs()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  getLogs()
}

const getProgressColor = (percentage) => {
  if (percentage < 60) return '#67C23A'
  if (percentage < 80) return '#E6A23C'
  return '#F56C6C'
}

const getLogLevelType = (level) => {
  const types = {
    INFO: '',
    WARNING: 'warning',
    ERROR: 'danger',
    DEBUG: 'info'
  }
  return types[level] || ''
}

const formatBytes = (bytes) => {
  if (!bytes) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  getSystemInfo()
  getLogs()
})
</script>

<style scoped>
.system-container {
  padding: 20px;
}

.mt-20 {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-card {
  text-align: center;
  padding: 20px;
}

.metric-info {
  margin-top: 10px;
  font-size: 14px;
  color: #666;
}

.filter-group {
  display: flex;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style> 
