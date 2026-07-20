<template>
  <div class="data-import">
    <page-header 
      title="Data Import"
      subtitle="Import material data in bulk"
    >
      <template #actions>
        <el-button @click="downloadTemplate">
          Download Template
        </el-button>
      </template>
    </page-header>

    <el-card class="import-card">
      <el-upload
        class="upload-area"
        drag
        action="#"
        :auto-upload="false"
        :show-file-list="true"
        :on-change="handleFileChange"
        :before-upload="beforeUpload"
        accept=".xlsx,.xls,.csv"
      >
        <el-icon class="upload-icon"><Upload /></el-icon>
        <div class="upload-text">
          <span>Drop file here or <em>click to upload</em></span>
          <p class="upload-tip">Supports .xlsx, .xls, and .csv files</p>
        </div>
      </el-upload>

      <!-- 导入配置 -->
      <div class="import-config" v-if="fileList.length > 0">
        <h3>Import Settings</h3>
        <el-form :model="importConfig" label-width="100px">
          <el-form-item label="Data Type">
            <el-radio-group v-model="importConfig.dataType">
              <el-radio label="HEA">High-Entropy Alloy</el-radio>
              <el-radio label="traditional">Traditional Alloy</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="Duplicate Records">
            <el-radio-group v-model="importConfig.duplicateHandle">
              <el-radio label="skip">Skip</el-radio>
              <el-radio label="update">Update</el-radio>
              <el-radio label="create">Create</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item>
            <el-button 
              type="primary" 
              @click="handleImport"
              :loading="importing"
            >
              Start Import
            </el-button>
            <el-button @click="handleReset">Reset</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 导入进度 -->
      <div class="import-progress" v-if="importing">
        <el-progress 
          :percentage="importProgress"
          :status="importProgress === 100 ? 'success' : ''"
        />
        <p class="progress-text">
          {{ importProgress === 100 ? 'Import complete' : 'Importing...' }}
          {{ importProgress }}%
        </p>
      </div>

      <!-- Import Results -->
      <div class="import-result" v-if="importResult.show">
        <el-alert
          :title="importResult.success ? 'Import successful' : 'Import failed'"
          :type="importResult.success ? 'success' : 'error'"
          :description="importResult.message"
          show-icon
          :closable="false"
        />
        
        <div class="result-stats" v-if="importResult.success">
          <p>Total records: {{ importResult.total }}</p>
          <p>Imported: {{ importResult.success_count }}</p>
          <p>Failed: {{ importResult.fail_count }}</p>
        </div>

        <!-- 错误记录 -->
        <div class="error-records" v-if="importResult.errors.length > 0">
          <h4>Error Records</h4>
          <el-table :data="importResult.errors" border size="small">
            <el-table-column prop="row" label="Row" width="80" />
            <el-table-column prop="field" label="Field" width="120" />
            <el-table-column label="Error">
              <template #default>Import validation failed for this row.</template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'

const store = useStore()

// 文件列表
const fileList = ref([])

// 导入配置
const importConfig = reactive({
  dataType: 'HEA',
  duplicateHandle: 'skip'
})

// 导入状态
const importing = ref(false)
const importProgress = ref(0)

// Import Results
const importResult = reactive({
  show: false,
  success: false,
  message: '',
  total: 0,
  success_count: 0,
  fail_count: 0,
  errors: []
})

// 文件变更处理
const handleFileChange = (file) => {
  fileList.value = [file]
}

// 上传前验证
const beforeUpload = (file) => {
  const isExcel = file.type === 'application/vnd.ms-excel' || 
                  file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  const isCSV = file.type === 'text/csv'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isExcel && !isCSV) {
    ElMessage.error('Only Excel or CSV files are allowed!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('File size cannot exceed 2 MB!')
    return false
  }
  return true
}

// Download Template
const downloadTemplate = () => {
  // TODO: 实现模板下载
  const link = document.createElement('a')
  link.href = '/templates/material_import_template.xlsx'
  link.download = 'material_import_template.xlsx'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 开始导入
const handleImport = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('Please select a file to import')
    return
  }

  try {
    importing.value = true
    importProgress.value = 0
    importResult.show = false

    // 模拟进度
    const timer = setInterval(() => {
      if (importProgress.value < 90) {
        importProgress.value += 10
      }
    }, 300)

    // 调用导入API
    const formData = new FormData()
    formData.append('file', fileList.value[0].raw)
    formData.append('type', importConfig.dataType)
    formData.append('duplicate_handle', importConfig.duplicateHandle)

    const result = await store.dispatch('material/importMaterials', formData)
    
    clearInterval(timer)
    importProgress.value = 100

    // 显示结果
    importResult.show = true
    importResult.success = true
    importResult.message = 'Data imported successfully'
    importResult.total = result.total
    importResult.success_count = result.success_count
    importResult.fail_count = result.fail_count
    importResult.errors = result.errors || []

    if (result.fail_count > 0) {
      ElMessage.warning(`Import complete, but ${result.fail_count} records failed`)
    } else {
      ElMessage.success('Import successful')
    }
  } catch (error) {
    console.error('Material import failed:')
    importResult.show = true
    importResult.success = false
    importResult.message = 'Import failed. Please check the file and try again.'
    ElMessage.error('Import failed')
  } finally {
    importing.value = false
  }
}

// Reset
const handleReset = () => {
  fileList.value = []
  importConfig.dataType = 'HEA'
  importConfig.duplicateHandle = 'skip'
  importProgress.value = 0
  importResult.show = false
}
</script>

<style scoped>
.data-import {
  padding: 20px;
}

.import-card {
  margin-top: 20px;
}

.upload-area {
  text-align: center;
}

.upload-icon {
  font-size: 48px;
  color: #909399;
  margin-bottom: 10px;
}

.upload-text em {
  color: #409EFF;
  font-style: normal;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 10px;
}

.import-config {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #EBEEF5;
}

.import-progress {
  margin-top: 20px;
}

.progress-text {
  text-align: center;
  margin-top: 10px;
  color: #606266;
}

.import-result {
  margin-top: 20px;
}

.result-stats {
  margin: 15px 0;
  color: #606266;
}

.error-records {
  margin-top: 20px;
}

.error-records h4 {
  margin-bottom: 10px;
  color: #F56C6C;
}
</style> 
