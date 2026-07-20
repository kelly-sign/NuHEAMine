<template>
  <div class="prediction-page">
    <page-header :title="title" :subtitle="description" />

    <prediction-overview-card :config="overviewConfig" />

    <el-alert
      :title="statusTitle"
      :description="statusMessage"
      :type="isDeployed ? 'success' : 'warning'"
      :closable="false"
      show-icon
      class="status-alert"
    />

    <el-row :gutter="20">
      <el-col :xs="24" :lg="12">
        <el-card class="workspace-card">
          <template #header>
            <div class="card-header">
              <span>Prediction Input</span>
              <el-tag v-if="!isDeployed" type="info">Reserved Interface</el-tag>
            </div>
          </template>

          <el-form
            ref="formRef"
            :model="formData"
            :rules="formRules"
            label-position="top"
          >
            <el-form-item
              v-for="field in inputFields"
              :key="field.key"
              :label="getFieldLabel(field)"
              :prop="field.key"
            >
              <el-input-number
                v-if="field.type === 'number'"
                v-model="formData[field.key]"
                :min="field.min"
                :max="field.max"
                :step="field.step || 1"
                :precision="field.precision"
                :disabled="inputsDisabled"
                controls-position="right"
                class="full-width-input"
              />

              <el-select
                v-else-if="field.type === 'select'"
                v-model="formData[field.key]"
                :placeholder="field.placeholder"
                :disabled="inputsDisabled"
                class="full-width-input"
              >
                <el-option
                  v-for="option in field.options || []"
                  :key="getOptionValue(option)"
                  :label="getOptionLabel(option)"
                  :value="getOptionValue(option)"
                />
              </el-select>

              <el-input
                v-else
                v-model="formData[field.key]"
                :type="field.type === 'textarea' ? 'textarea' : 'text'"
                :rows="field.type === 'textarea' ? 3 : undefined"
                :placeholder="field.placeholder"
                :disabled="inputsDisabled"
              />

              <div v-if="field.description" class="field-description">
                {{ field.description }}
              </div>
            </el-form-item>

            <el-empty
              v-if="!inputFields.length"
              description="The input schema has not been configured"
              :image-size="72"
            />

            <div class="form-actions">
              <el-button
                type="primary"
                :loading="loading"
                @click="handleSubmit"
              >
                Run Prediction
              </el-button>
              <el-button :disabled="loading" @click="resetForm">Reset</el-button>
            </div>
          </el-form>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card class="workspace-card result-card">
          <template #header>
            <div class="card-header">
              <span>Prediction Result</span>
              <span class="result-unit">{{ outputSummary }}</span>
            </div>
          </template>

          <el-descriptions v-if="predictionResult" :column="1" border>
            <el-descriptions-item
              v-for="field in outputFields"
              :key="field.key"
              :label="field.label || field.key"
            >
              {{ formatResultValue(getResultValue(field.key)) }}
              <span v-if="field.unit && getResultValue(field.key) != null" class="unit-label">
                {{ field.unit }}
              </span>
            </el-descriptions-item>
          </el-descriptions>

          <div v-if="predictionResult" class="raw-result">
            <span>API Response</span>
            <pre>{{ formattedResult }}</pre>
          </div>

          <el-empty
            v-else
            :description="emptyResultMessage"
            :image-size="100"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import { submitPrediction } from '@/api/prediction'
import PredictionOverviewCard from './PredictionOverviewCard.vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  status: {
    type: String,
    default: 'developing'
  },
  route: {
    type: String,
    default: ''
  },
  predictionTarget: {
    type: String,
    default: ''
  },
  inputSchema: {
    type: [Array, String],
    default: () => []
  },
  outputSchema: {
    type: [Array, String],
    default: () => []
  },
  apiEndpoint: {
    type: String,
    required: true
  }
})

const formRef = ref(null)
const formData = reactive({})
const loading = ref(false)
const predictionResult = ref(null)
const runtimeStatus = ref(props.status)

const normalizeSchema = (schema, prefix) => {
  const items = Array.isArray(schema) ? schema : (schema ? [schema] : [])
  return items.map((item, index) => {
    if (typeof item === 'object') return item
    return {
      key: `${prefix}_${index}`,
      label: String(item),
      type: 'text'
    }
  })
}

const inputFields = computed(() => normalizeSchema(props.inputSchema, 'input'))
const outputFields = computed(() => normalizeSchema(props.outputSchema, 'output'))
const isDeployed = computed(() => runtimeStatus.value === 'deployed')
const inputsDisabled = computed(() => loading.value)

const overviewConfig = computed(() => ({
  title: props.title,
  description: props.description,
  status: runtimeStatus.value,
  route: props.route,
  predictionTarget: props.predictionTarget,
  inputSchema: props.inputSchema,
  outputSchema: props.outputSchema,
  apiEndpoint: props.apiEndpoint
}))

const statusTitle = computed(() => isDeployed.value
  ? 'Model Deployed'
  : 'Model Under Development')

const statusMessage = computed(() => isDeployed.value
  ? 'The model endpoint is available. Complete the inputs to run a prediction.'
  : 'This reserved interface is ready for model integration. Submit the configured inputs to check the current API status.')

const emptyResultMessage = computed(() => isDeployed.value
  ? 'Complete the input fields and run a prediction'
  : 'Prediction results will appear here when the reserved API provides a deployed model response')

const outputSummary = computed(() => {
  return outputFields.value
    .map(field => field.unit ? `${field.label} (${field.unit})` : field.label)
    .filter(Boolean)
    .join(' / ')
})

const formRules = computed(() => {
  const rules = {}
  inputFields.value.forEach((field) => {
    if (field.required) {
      rules[field.key] = [{
        required: true,
        message: `${field.label || field.key} is required`,
        trigger: field.type === 'select' ? 'change' : 'blur'
      }]
    }
  })
  return rules
})

const initializeForm = () => {
  Object.keys(formData).forEach(key => delete formData[key])
  inputFields.value.forEach((field) => {
    if (Object.prototype.hasOwnProperty.call(field, 'defaultValue')) {
      formData[field.key] = field.defaultValue
    } else {
      formData[field.key] = field.type === 'number' ? null : ''
    }
  })
  predictionResult.value = null
  nextTick(() => formRef.value?.clearValidate())
}

const getFieldLabel = (field) => {
  return field.unit ? `${field.label || field.key} (${field.unit})` : (field.label || field.key)
}

const getOptionLabel = (option) => {
  return typeof option === 'object' ? option.label : option
}

const getOptionValue = (option) => {
  return typeof option === 'object' ? option.value : option
}

const getResultValue = (key) => {
  if (!predictionResult.value || typeof predictionResult.value !== 'object') return null
  return predictionResult.value[key]
}

const formatResultValue = (value) => {
  if (value == null || value === '') return '-'
  if (typeof value === 'number') return Number.isInteger(value) ? value : value.toFixed(2)
  if (typeof value === 'object') return JSON.stringify(value)
  return value
}

const formattedResult = computed(() => {
  try {
    return JSON.stringify(predictionResult.value, null, 2)
  } catch (error) {
    return String(predictionResult.value)
  }
})

const handleSubmit = async () => {
  try {
    if (formRef.value) {
      const valid = await formRef.value.validate().catch(() => false)
      if (!valid) return
    }

    loading.value = true
    const response = await submitPrediction(props.apiEndpoint, { ...formData })
    const payload = response?.data || response

    if (payload?.status === 'developing') {
      runtimeStatus.value = 'developing'
      predictionResult.value = null
      ElMessage.info(payload.message || 'Prediction model is under development')
      return
    }

    runtimeStatus.value = 'deployed'
    predictionResult.value = payload?.output_data || payload?.result || payload
    ElMessage.success('Prediction completed')
  } catch (error) {
    ElMessage.error('Prediction failed')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  initializeForm()
}

watch(
  [() => props.route, () => props.inputSchema, () => props.status],
  () => {
    runtimeStatus.value = props.status
    initializeForm()
  },
  { immediate: true }
)
</script>

<style scoped>
.prediction-page {
  min-height: 100%;
  padding: 20px;
  background: #f5f7fa;
}

.status-alert {
  margin-bottom: 20px;
}

.workspace-card {
  min-height: 450px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: #303133;
  font-weight: 600;
}

.full-width-input {
  width: 100%;
}

.field-description {
  width: 100%;
  margin-top: 5px;
  color: #909399;
  font-size: 12px;
  line-height: 1.5;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 8px;
}

.result-unit {
  color: #909399;
  font-size: 12px;
  font-weight: 400;
  text-align: right;
}

.unit-label {
  margin-left: 4px;
  color: #909399;
}

.raw-result {
  margin-top: 18px;
}

.raw-result > span {
  color: #606266;
  font-size: 13px;
  font-weight: 600;
}

.raw-result pre {
  overflow: auto;
  max-height: 230px;
  margin: 8px 0 0;
  padding: 14px;
  border-radius: 4px;
  background: #f5f7fa;
  color: #303133;
  font-family: Consolas, 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

@media (max-width: 1199px) {
  .workspace-card {
    min-height: auto;
  }
}
</style>
