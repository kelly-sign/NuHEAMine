<template>
  <div class="prediction-result">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="result-card">
          <template #header>
            <div class="card-header">
              <span>Prediction Details</span>
              <el-button-group>
                <el-button size="small" @click="handleSave">Save</el-button>
                <el-button size="small" @click="handleExport">Export</el-button>
              </el-button-group>
            </div>
          </template>

          <el-descriptions border>
            <el-descriptions-item label="Prediction Time">
              {{ formatDate(result.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="Prediction Model">
              {{ result.model_name }}
            </el-descriptions-item>
            
            <el-descriptions-item label="Input Parameters" :span="2">
              <div class="params-list">
                <div v-for="(value, key) in result.input_data" :key="key" class="param-item">
                  <span class="param-label">{{ getParamLabel(key) }}:</span>
                  <span class="param-value">{{ formatValue(value, key) }}</span>
                </div>
              </div>
            </el-descriptions-item>
            
            <el-descriptions-item label="Prediction Result" :span="2">
              <div class="result-metrics">
                <el-row :gutter="20">
                  <el-col :span="12" v-for="(value, key) in result.output_data" :key="key">
                    <div class="metric-card">
                      <div class="metric-value">{{ formatValue(value, key) }}</div>
                      <div class="metric-label">{{ getMetricLabel(key) }}</div>
                    </div>
                  </el-col>
                </el-row>
              </div>
            </el-descriptions-item>
            
            <el-descriptions-item v-if="result.confidence != null" label="Confidence Assessment">
              <el-progress
                :percentage="result.confidence * 100"
                :status="getConfidenceStatus(result.confidence)"
              />
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Performance Comparison</span>
              <el-select v-model="selectedMetric" size="small">
                <el-option
                  v-for="(label, key) in metricLabels"
                  :key="key"
                  :label="label"
                  :value="key"
                />
              </el-select>
            </div>
          </template>

          <div class="chart-container" ref="chartRef"></div>

          <div class="chart-legend">
            <div class="legend-item">
              <div class="legend-color" style="background-color: #409EFF"></div>
              <span>Predicted Value</span>
            </div>
            <div class="legend-item">
              <div class="legend-color" style="background-color: #67C23A"></div>
              <span>Reference Range</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 保存预测结果对话框 -->
    <el-dialog
      v-model="saveDialogVisible"
      title="Save Prediction Result"
      width="30%"
    >
      <el-form :model="saveForm" label-width="80px">
        <el-form-item label="Name">
          <el-input v-model="saveForm.name" placeholder="Enter a name" />
        </el-form-item>
        <el-form-item label="Notes">
          <el-input
            v-model="saveForm.remarks"
            type="textarea"
            rows="3"
            placeholder="Enter notes"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="saveDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSaveConfirm">Confirm</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const props = defineProps({
  result: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['save'])

const chartRef = ref(null)
let chart = null

const selectedMetric = ref('Pred_HV')
const saveDialogVisible = ref(false)
const saveForm = ref({
  name: '',
  remarks: ''
})

const metricLabels = {
  Pred_HV: 'Hardness (HV)',
  hardness: 'Hardness (HV)',
  yieldStrength: 'Yield Strength (MPa)',
  tensileStrength: 'Tensile Strength (MPa)',
  elongation: 'Elongation (%)'
}

const paramLabels = {
  temperature: 'Heat-Treatment Temperature (deg C)',
  holdingTime: 'Holding Time (h)'
}

// 格式化参数标签
const getParamLabel = (key) => {
  if (key === 'composition') return 'Composition'
  return paramLabels[key] || key
}

// 格式化指标标签
const getMetricLabel = (key) => {
  return metricLabels[key] || key
}

// 格式化数值
const formatValue = (value, key) => {
  if (key === 'composition') {
    return Object.entries(value)
      .map(([element, percent]) => `${element}: ${percent}%`)
      .join(', ')
  }
  if (typeof value === 'number') {
    return value.toFixed(2)
  }
  return value
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

// 初始化图表
const initChart = () => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)
    window.addEventListener('resize', () => chart.resize())
  }
}

// 更新图表
const updateChart = () => {
  if (!chart || !props.result?.output_data) return
  const out = props.result.output_data
  const keys = Object.keys(out).filter(k => typeof out[k] === 'number')
  if (keys.length === 0) return
  const label = keys.includes(selectedMetric.value) ? selectedMetric.value : keys[0]
  const value = out[label]
  const ref = props.result.reference_range?.[label]
  const option = {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: ref ? ['Predicted Value', 'Reference Range'] : ['Predicted Value'] },
    yAxis: { type: 'value', name: metricLabels[label] || label },
    series: [
      {
        name: 'Predicted Value',
        type: 'bar',
        data: ref ? [value, (ref.min + ref.max) / 2] : [value],
        itemStyle: { color: '#409EFF' }
      }
    ]
  }
  chart.setOption(option)
}

// 保存预测结果
const handleSave = () => {
  saveDialogVisible.value = true
  saveForm.value.name = `Prediction_${new Date().toLocaleString('en-US')}`
}

const handleSaveConfirm = () => {
  emit('save', {
    ...props.result,
    ...saveForm.value
  })
  saveDialogVisible.value = false
  ElMessage.success('Saved successfully')
}

// 导出预测结果
const handleExport = () => {
  // TODO: 实现导出功能
  ElMessage.success('Export successful')
}

watch(selectedMetric, () => {
  updateChart()
})

watch(() => props.result, (r) => {
  if (r?.output_data && Object.keys(r.output_data).length) {
    const first = Object.keys(r.output_data)[0]
    if (typeof r.output_data[first] === 'number') selectedMetric.value = first
  }
  updateChart()
}, { immediate: true })

onMounted(() => {
  initChart()
  updateChart()
})
</script>

<style scoped>
.prediction-result {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.params-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.param-item {
  display: flex;
  align-items: center;
}

.param-label {
  color: #666;
  margin-right: 8px;
}

.result-metrics {
  padding: 10px 0;
}

.metric-card {
  text-align: center;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 10px;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.metric-label {
  margin-top: 8px;
  color: #666;
}

.chart-container {
  height: 300px;
}

.chart-legend {
  display: flex;
  justify-content: center;
  margin-top: 15px;
  gap: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  margin-right: 8px;
}
</style> 
