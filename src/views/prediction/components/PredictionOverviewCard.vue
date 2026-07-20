<template>
  <el-card class="prediction-overview-card" shadow="never">
    <template #header>
      <div class="overview-header">
        <div>
          <span class="overview-title">Function Overview</span>
          <p class="overview-description">{{ config.description }}</p>
        </div>
        <el-tag :type="statusType" effect="dark">{{ statusLabel }}</el-tag>
      </div>
    </template>

    <el-row :gutter="16" class="overview-grid">
      <el-col :xs="24" :sm="12" :lg="6">
        <section class="overview-section">
          <h3>Prediction Target</h3>
          <p>{{ config.predictionTarget }}</p>
        </section>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <section class="overview-section">
          <h3>Input Data</h3>
          <ul v-if="inputItems.length">
            <li v-for="(item, index) in inputItems" :key="getItemKey(item, index)">
              <span>{{ getItemLabel(item) }}</span>
              <small v-if="getItemDescription(item)">{{ getItemDescription(item) }}</small>
            </li>
          </ul>
          <p v-else>No input schema configured</p>
        </section>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <section class="overview-section">
          <h3>Output Result</h3>
          <ul v-if="outputItems.length">
            <li v-for="(item, index) in outputItems" :key="getItemKey(item, index)">
              <span>{{ getOutputLabel(item) }}</span>
            </li>
          </ul>
          <p v-else>No output schema configured</p>
        </section>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <section class="overview-section status-section">
          <h3>Model Status</h3>
          <strong :class="['status-text', { deployed: isDeployed }]">{{ statusLabel }}</strong>
          <p>{{ statusDescription }}</p>
        </section>
      </el-col>
    </el-row>

    <div class="api-interface">
      <span>Reserved API Interface</span>
      <code>{{ config.apiEndpoint }}</code>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  config: {
    type: Object,
    required: true
  }
})

const normalizeSchema = (schema) => {
  if (Array.isArray(schema)) return schema
  return schema ? [schema] : []
}

const inputItems = computed(() => normalizeSchema(props.config.inputSchema))
const outputItems = computed(() => normalizeSchema(props.config.outputSchema))
const isDeployed = computed(() => props.config.status === 'deployed')
const statusLabel = computed(() => isDeployed.value ? 'Deployed' : 'Under Development')
const statusType = computed(() => isDeployed.value ? 'success' : 'warning')
const statusDescription = computed(() => isDeployed.value
  ? 'The prediction model is available for use.'
  : 'The prediction model is under development.')

const getItemKey = (item, index) => {
  return typeof item === 'object' && item?.key ? item.key : `${String(item)}-${index}`
}

const getItemLabel = (item) => {
  return typeof item === 'object' ? (item.label || item.key) : item
}

const getItemDescription = (item) => {
  return typeof item === 'object' ? item.description : ''
}

const getOutputLabel = (item) => {
  if (typeof item !== 'object') return item
  return item.unit ? `${item.label || item.key} (${item.unit})` : (item.label || item.key)
}
</script>

<style scoped>
.prediction-overview-card {
  margin-bottom: 20px;
  border-color: #dcdfe6;
}

.overview-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.overview-title {
  color: #303133;
  font-size: 17px;
  font-weight: 600;
}

.overview-description {
  margin: 7px 0 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.overview-grid {
  row-gap: 16px;
}

.overview-section {
  box-sizing: border-box;
  min-height: 150px;
  height: 100%;
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  background: #f8fafc;
}

.overview-section h3 {
  margin: 0 0 12px;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.overview-section p {
  margin: 0;
  color: #606266;
  font-size: 13px;
  line-height: 1.6;
}

.overview-section ul {
  margin: 0;
  padding-left: 18px;
  color: #606266;
}

.overview-section li {
  margin-bottom: 7px;
  font-size: 13px;
  line-height: 1.45;
}

.overview-section li:last-child {
  margin-bottom: 0;
}

.overview-section li small {
  display: block;
  margin-top: 2px;
  color: #909399;
  font-size: 12px;
}

.status-text {
  display: block;
  margin-bottom: 8px;
  color: #e6a23c;
  font-size: 15px;
}

.status-text.deployed {
  color: #67c23a;
}

.api-interface {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  padding: 12px 16px;
  border-left: 3px solid #409eff;
  border-radius: 4px;
  background: #ecf5ff;
  color: #606266;
  font-size: 13px;
}

.api-interface code {
  overflow-wrap: anywhere;
  color: #1d5f9e;
  font-family: Consolas, 'Courier New', monospace;
}

@media (max-width: 767px) {
  .overview-header,
  .api-interface {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
