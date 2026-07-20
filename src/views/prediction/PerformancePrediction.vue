<template>
  <div class="prediction-container">
    <page-header 
      title="Hardness (HV) Prediction"
      subtitle="Enter the atomic percentages of 15 elements in a high-entropy alloy to predict its hardness"
    >
    </page-header>

    <prediction-overview-card :config="hardnessPredictionConfig" />

    <el-tabs v-model="activeMode" class="prediction-mode-tabs">
      <el-tab-pane label="Single Prediction" name="single" />
      <el-tab-pane label="Batch Prediction" name="batch" />
    </el-tabs>

    <el-row v-show="activeMode === 'single'" :gutter="20">
      <el-col :span="12">
        <el-card class="input-card">
          <template #header>
            <div class="card-header">
              <span>Alloy Composition (at.%; recommended total: 100)</span>
            </div>
          </template>
          
          <el-form 
            ref="predictionFormRef"
            :model="predictionForm"
            :rules="predictionRules"
            label-width="80px"
          >
            <el-form-item label="Composition" prop="composition">
              <div class="composition-grid">
                <div v-for="(element, index) in elements" :key="index" class="composition-item">
                  <span class="element-label">{{ element }} %</span>
                  <el-input-number
                    v-model="predictionForm.composition[element]"
                    :min="0"
                    :max="100"
                    :precision="2"
                    :step="0.5"
                    :controls="false"
                    size="small"
                    class="composition-input"
                  />
                </div>
              </div>
              <div class="composition-sum">Composition Total: {{ compositionSum }}%</div>
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary" 
                @click="handlePredict"
                :loading="loading"
              >
                Run Prediction
              </el-button>
              <el-button @click="handleReset">Reset</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="result-card">
          <template #header>
            <div class="card-header">
              <span>Prediction Result</span>
            </div>
          </template>

          <div v-if="predictionResult" class="prediction-result">
            <el-descriptions border>
              <el-descriptions-item label="Predicted Hardness (Pred_HV)">
                {{ predictionResult.Pred_HV != null ? predictionResult.Pred_HV.toFixed(2) : '-' }} HV
              </el-descriptions-item>
            </el-descriptions>
            <div class="result-chart" ref="chartRef"></div>
          </div>

          <el-empty v-else description="Enter a composition and click Run Prediction"></el-empty>
        </el-card>
      </el-col>
    </el-row>

    <el-row v-show="activeMode === 'batch'" :gutter="20">
      <el-col :span="12">
        <el-card class="input-card">
          <template #header>
            <div class="card-header">
              <span>Batch Composition File (CSV / Excel)</span>
            </div>
          </template>
          <p class="batch-hint">
            The first row must be a header containing all 15 element columns (Al, Co, Cr, etc.). Identifier columns such as Alloys are optional. Blank cells are treated as 0.
            Processing is equivalent to running <code>predict.py</code> on the full table in one batch with the same feature engineering.
          </p>
          <el-upload
            class="batch-upload"
            :auto-upload="false"
            :show-file-list="true"
            :limit="1"
            accept=".csv,.xlsx,.xls"
            :on-change="handleBatchFile"
            :on-exceed="() => ElMessage.warning('Remove the selected file before uploading another one')"
          >
            <el-button type="primary" plain>Select File</el-button>
            <template #tip>
              <div class="el-upload__tip">{{ batchRowCount }} rows parsed</div>
            </template>
          </el-upload>
          <div class="batch-save-row">
            <span class="batch-save-label">Save History</span>
            <el-switch v-model="batchSaveHistory" active-text="Yes" inactive-text="No" />
            <span class="batch-save-tip">When enabled, each result is saved as a separate history entry</span>
          </div>
          <el-button
            type="primary"
            :loading="batchLoading"
            :disabled="!batchSamples.length"
            @click="handleBatchPredict"
          >
            Run Batch Prediction
          </el-button>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="result-card">
          <template #header>
            <div class="card-header">
              <span>Batch Prediction Results</span>
              <span v-if="batchMeta.batch_size" class="batch-meta">{{ batchMeta.batch_size }} rows</span>
            </div>
          </template>
          <el-table
            v-if="batchResults.length"
            :data="batchResults"
            border
            stripe
            max-height="420"
            size="small"
          >
            <el-table-column
              v-for="col in batchTableColumns"
              :key="col"
              :prop="col"
              :label="col"
              :min-width="col === 'Pred_HV' ? 110 : 88"
            >
              <template #default="{ row }">
                <span v-if="col === 'Pred_HV' && row[col] != null">
                  {{ formatPredCell(row[col]) }}
                </span>
                <span v-else>{{ row[col] }}</span>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="Upload a composition file and click Run Batch Prediction"></el-empty>
        </el-card>
      </el-col>
    </el-row>

    <prediction-history
      ref="historyRef"
      @view="handleViewHistory"
    />

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import * as XLSX from 'xlsx'
import PageHeader from '@/components/common/PageHeader.vue'
import PredictionHistory from './components/PredictionHistory.vue'
import PredictionOverviewCard from './components/PredictionOverviewCard.vue'
import { hvPredict, hvPredictBatch } from '@/api/prediction'
import { predictionModuleConfigs } from '@/config/predictionModules'

const elements = ['Al', 'Co', 'Cr', 'Cu', 'Fe', 'Hf', 'Mn', 'Mo', 'Nb', 'Ni', 'Ta', 'Ti', 'V', 'W', 'Zr']
const ID_KEYS = ['Alloys', 'id', 'ID', 'sample', 'Sample', 'name', 'Name']
const hardnessPredictionConfig = predictionModuleConfigs.hardness

const activeMode = ref('single')
const predictionFormRef = ref(null)
const loading = ref(false)
const chartRef = ref(null)
const historyRef = ref(null)
let chart = null

const batchSamples = ref([])
const batchResults = ref([])
const batchMeta = ref({})
const batchLoading = ref(false)
const batchSaveHistory = ref(false)

const batchRowCount = computed(() => batchSamples.value.length)

const batchTableColumns = computed(() => {
  if (!batchResults.value.length) return []
  const keys = new Set()
  batchResults.value.forEach((r) => {
    Object.keys(r).forEach((k) => keys.add(k))
  })
  const preferred = [...ID_KEYS.filter((k) => keys.has(k)), ...elements.filter((e) => keys.has(e))]
  const pred = keys.has('Pred_HV') ? ['Pred_HV'] : []
  const rest = [...keys].filter((k) => !preferred.includes(k) && !pred.includes(k))
  rest.sort()
  return [...preferred, ...rest, ...pred]
})

function normalizeHeaderKey(k) {
  return String(k).replace(/^\uFEFF/, '').trim()
}

function sheetRowsToSamples(rows) {
  return rows.map((raw) => {
    const row = {}
    Object.keys(raw).forEach((k) => {
      row[normalizeHeaderKey(k)] = raw[k]
    })
    const out = {}
    ID_KEYS.forEach((k) => {
      if (row[k] !== undefined && row[k] !== null && row[k] !== '') {
        out[k] = row[k]
      }
    })
    elements.forEach((e) => {
      const v = row[e]
      if (v !== undefined && v !== null && v !== '') {
        const n = parseFloat(v)
        if (!Number.isNaN(n)) out[e] = n
      }
    })
    return out
  })
}

function formatPredCell(v) {
  const n = Number(v)
  return Number.isFinite(n) ? n.toFixed(2) : String(v)
}

function handleBatchFile(uploadFile) {
  const file = uploadFile.raw
  if (!file) return
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = new Uint8Array(e.target.result)
      const wb = XLSX.read(data, { type: 'array' })
      const sheet = wb.Sheets[wb.SheetNames[0]]
      const rows = XLSX.utils.sheet_to_json(sheet, { defval: null, raw: false })
      batchSamples.value = sheetRowsToSamples(rows)
      batchResults.value = []
      batchMeta.value = {}
      ElMessage.success(`${batchSamples.value.length} rows parsed`)
    } catch (err) {
      batchSamples.value = []
      ElMessage.error(err?.message ? `Failed to parse file: ${err.message}` : 'Failed to parse file')
    }
  }
  reader.readAsArrayBuffer(file)
}

async function handleBatchPredict() {
  if (!batchSamples.value.length) {
    ElMessage.warning('Please upload a file first')
    return
  }
  try {
    batchLoading.value = true
    const res = await hvPredictBatch({
      samples: batchSamples.value,
      save_history: batchSaveHistory.value
    })
    const payload = res?.data || res
    batchResults.value = payload.results || []
    batchMeta.value = {
      batch_size: payload.batch_size,
      model_path: payload.model_path,
      runtime: payload.runtime
    }
    ElMessage.success(
      batchSaveHistory.value ? 'Batch prediction completed and saved to history' : 'Batch prediction completed'
    )
    if (batchSaveHistory.value && historyRef.value?.fetchRecords) {
      await historyRef.value.fetchRecords()
    }
  } catch (error) {
    ElMessage.error('Batch prediction failed')
  } finally {
    batchLoading.value = false
  }
}

const handleViewHistory = () => {}

const defaultComposition = () => {
  const o = {}
  elements.forEach(e => { o[e] = 0 })
  return o
}

const predictionForm = ref({
  composition: defaultComposition()
})

const predictionResult = ref(null)

const compositionSum = computed(() => {
  const c = predictionForm.value.composition
  const sum = elements.reduce((s, e) => s + (Number(c[e]) || 0), 0)
  return sum.toFixed(1)
})

const predictionRules = {
  composition: [
    {
      validator: (_rule, _val, cb) => {
        const sum = elements.reduce((s, e) => s + (Number(predictionForm.value.composition[e]) || 0), 0)
        if (sum <= 0) return cb(new Error('The composition total must be greater than 0'))
        cb()
      },
      trigger: 'change'
    }
  ]
}

const handlePredict = async () => {
  if (!predictionFormRef.value) return
  await predictionFormRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      loading.value = true
      const res = await hvPredict({
        composition: { ...predictionForm.value.composition }
      })
      const payload = res?.data || res
      predictionResult.value = payload.output_data || { Pred_HV: payload.Pred_HV }
      updateChart()
      ElMessage.success('Prediction completed and saved')
      if (historyRef.value && typeof historyRef.value.fetchRecords === 'function') {
        await historyRef.value.fetchRecords()
      }
    } catch (error) {
      ElMessage.error('Prediction failed')
    } finally {
      loading.value = false
    }
  })
}

const handleReset = () => {
  predictionForm.value.composition = defaultComposition()
  predictionResult.value = null
  if (chart) chart.dispose()
  chart = null
  initChart()
}

const initChart = () => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)
  }
}

const updateChart = () => {
  if (!chart || !predictionResult.value?.Pred_HV) return
  const hv = predictionResult.value.Pred_HV
  const option = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['Hardness (HV)'] },
    yAxis: { type: 'value', name: 'HV' },
    series: [{ type: 'bar', data: [hv], itemStyle: { color: '#409EFF' } }]
  }
  chart.setOption(option)
}

onMounted(() => {
  initChart()
})
</script>

<style scoped>
.prediction-container {
  padding: 20px;
}

.composition-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px 16px;
}

.composition-item {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.element-label {
  font-size: 13px;
  color: #606266;
  min-width: 48px;
  flex-shrink: 0;
}

.composition-input {
  width: 100%;
  min-width: 72px;
  max-width: 100px;
}

.composition-sum {
  margin-top: 10px;
  font-size: 13px;
  color: #909399;
}

.unit {
  margin-left: 10px;
}

.result-chart {
  height: 300px;
  margin-top: 20px;
}

.prediction-result {
  padding: 20px;
}

.prediction-mode-tabs {
  margin-bottom: 16px;
}

.batch-hint {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  margin: 0 0 12px;
}

.batch-hint code {
  font-size: 12px;
  background: #f4f4f5;
  padding: 0 4px;
  border-radius: 4px;
}

.batch-upload {
  margin-bottom: 16px;
}

.batch-save-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.batch-save-label {
  font-size: 14px;
  color: #606266;
}

.batch-save-tip {
  font-size: 12px;
  color: #909399;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.batch-meta {
  font-size: 13px;
  color: #909399;
  font-weight: normal;
}
</style> 
