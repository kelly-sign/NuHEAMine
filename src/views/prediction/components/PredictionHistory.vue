<template>
  <div class="prediction-history">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Prediction History</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="Search prediction records"
              clearable
              class="search-input"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="filterModel"
              placeholder="Select a prediction model"
              clearable
              class="filter-select"
            >
              <el-option
                v-for="model in models"
                :key="model.id"
                :label="model.name"
                :value="model.id"
              />
            </el-select>
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="to"
              start-placeholder="Start date"
              end-placeholder="End date"
              class="date-picker"
            />
          </div>
        </div>
      </template>

      <el-table
        :data="filteredRecords"
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="created_at" label="Prediction Time" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="model_name" label="Prediction Model" width="150" />
        <el-table-column label="Input Parameters">
          <template #default="{ row }">
            <el-tooltip
              effect="dark"
              placement="top"
              :content="formatParams(row.input_data)"
            >
              <div class="params-preview">
                {{ formatParams(row.input_data) }}
              </div>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="Prediction Result">
          <template #default="{ row }">
            <div class="metrics-preview">
              <el-tag 
                v-for="(value, key) in row.output_data"
                :key="key"
                :type="getMetricTagType(key)"
                class="metric-tag"
              >
                {{ getMetricLabel(key) }}: {{ formatValue(value) }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Confidence" width="120">
          <template #default="{ row }">
            <template v-if="row.confidence != null">
              <el-progress
                :percentage="row.confidence * 100"
                :status="getConfidenceStatus(row.confidence)"
                :stroke-width="8"
              />
            </template>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150">
          <template #default="{ row }">
            <el-button-group>
              <el-button 
                size="small"
                @click="handleView(row)"
              >
                View
              </el-button>
              <el-button
                size="small"
                type="danger"
                @click="handleDelete(row)"
              >
                Delete
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 预测结果详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="Prediction Details"
      width="80%"
      destroy-on-close
    >
      <prediction-result
        v-if="selectedRecord"
        :result="selectedRecord"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import PredictionResult from './PredictionResult.vue'
import { getPredictionHistory, deletePredictionRecord } from '@/api/prediction'

const loading = ref(false)
const searchKeyword = ref('')
const filterModel = ref('')
const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const detailDialogVisible = ref(false)
const selectedRecord = ref(null)

// 模拟数据
const models = ref([
  { id: 1, name: 'Model A' },
  { id: 2, name: 'Model B' }
])

const records = ref([])

const metricLabels = {
  Pred_HV: 'Hardness (HV)',
  hardness: 'Hardness',
  yieldStrength: 'Yield Strength',
  tensileStrength: 'Tensile Strength',
  elongation: 'Elongation'
}

// 过滤记录
const filteredRecords = computed(() => {
  let result = records.value

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(record => 
      record.model_name.toLowerCase().includes(keyword) ||
      formatParams(record.input_data).toLowerCase().includes(keyword)
    )
  }

  if (filterModel.value) {
    result = result.filter(record => record.model_id === filterModel.value)
  }

  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value
    result = result.filter(record => {
      const date = new Date(record.created_at)
      return date >= start && date <= end
    })
  }

  return result
})

// 获取预测记录（后端返回数组）
const fetchRecords = async () => {
  try {
    loading.value = true
    const res = await getPredictionHistory({
      page: currentPage.value,
      page_size: pageSize.value,
      model_id: filterModel.value,
      start_date: dateRange.value?.[0],
      end_date: dateRange.value?.[1]
    })
    const payload = res?.data || res
    const list = Array.isArray(payload) ? payload : (payload.results || [])
    records.value = list
    total.value = list.length
  } catch (error) {
    ElMessage.error('Failed to load prediction history')
  } finally {
    loading.value = false
  }
}

// 格式化参数
const formatParams = (params) => {
  const parts = []
  if (params.composition && typeof params.composition === 'object') {
    const entries = Object.entries(params.composition).filter(([, v]) => v != null && Number(v) > 0)
    if (entries.length) {
      parts.push(`Composition: ${entries.map(([e, v]) => `${e}=${v}%`).join(', ')}`)
    }
  }
  if (params.temperature != null) {
    parts.push(`Temperature: ${params.temperature} deg C`)
  }
  if (params.holdingTime != null) {
    parts.push(`Holding Time: ${params.holdingTime}h`)
  }
  return parts.length ? parts.join(' | ') : 'Composition Prediction'
}

// 格式化数值
const formatValue = (value) => {
  return typeof value === 'number' ? value.toFixed(2) : value
}

// 获取指标标签Type
const getMetricTagType = (key) => {
  const types = {
    hardness: '',
    yieldStrength: 'success',
    tensileStrength: 'warning',
    elongation: 'info'
  }
  return types[key] || ''
}

// 获取可靠性状态
const getConfidenceStatus = (confidence) => {
  if (confidence >= 0.8) return 'success'
  if (confidence >= 0.6) return 'warning'
  return 'exception'
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return 'No data'
  try {
    // 统一按北京时间显示，避免受本机时区影响
    const raw = String(dateString).trim().replace(' ', 'T')
    const normalized = /Z|[+-]\d{2}:\d{2}$/.test(raw) ? raw : `${raw}+08:00`
    const d = new Date(normalized)
    if (Number.isNaN(d.getTime())) return 'No data'
    return d.toLocaleString('en-US', {
      timeZone: 'Asia/Shanghai',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    })
  } catch (error) {
    console.error('Date formatting error:')
    return 'No data'
  }
}

// 查看详情
const handleView = (record) => {
  selectedRecord.value = record
  detailDialogVisible.value = true
}

// Delete记录
const handleDelete = async (record) => {
  try {
    await ElMessageBox.confirm('Are you sure you want to delete this prediction record?', 'Confirm', {
      type: 'warning'
    })
    await deletePredictionRecord(record.id)
    ElMessage.success('Deleted successfully')
    fetchRecords()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Delete failed')
    }
  }
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchRecords()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchRecords()
}

// 监听筛选条件变化
watch([filterModel, dateRange], () => {
  currentPage.value = 1
  fetchRecords()
})

onMounted(() => {
  fetchRecords()
})

// 使用 metricLabels 或移除它
const getMetricLabel = (key) => {
  return metricLabels[key] || key
}

defineExpose({
  fetchRecords
})
</script>

<style scoped>
.prediction-history {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.search-input {
  width: 200px;
}

.filter-select {
  width: 160px;
}

.date-picker {
  width: 320px;
}

.params-preview {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}

.metrics-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.metric-tag {
  margin-right: 5px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style> 
