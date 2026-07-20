<template>
  <div class="process-list-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>Process List</span>
          <div class="header-buttons">
            <el-button type="success" @click="handleImport">Import Data</el-button>
            <el-button type="warning" @click="handleExport">Export Data</el-button>
            <el-button type="primary" @click="handleAdd">Add Process</el-button>
          </div>
        </div>
      </template>

      <!-- Search bar -->
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="Search by process name or ID"
          class="search-input"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch">Search</el-button>
          </template>
        </el-input>
        <el-button @click="handleReset" style="margin-left: 10px">Reset</el-button>
      </div>

      <!-- Data table -->
      <el-table
        v-loading="loading"
        :data="tableData"
        style="width: 100%"
        border
        stripe
        highlight-current-row
      >
        <el-table-column prop="process_id" label="Process ID" width="120" sortable />
        <el-table-column prop="fabrication" label="Fabrication Process" min-width="150" show-overflow-tooltip />
        <el-table-column label="Heat Treatment" min-width="200">
          <template #default="{ row }">
            <el-tag v-if="row.homogenization" type="success" size="small">Homogenization</el-tag>
            <el-tag v-if="row.normalization" type="info" size="small">Normalization</el-tag>
            <el-tag v-if="row.annealing" type="warning" size="small">Annealing</el-tag>
            <el-tag v-if="row.tempering" type="danger" size="small">Tempering</el-tag>
            <el-tag v-if="row.quenching" type="primary" size="small">Quenching</el-tag>
            <el-tag v-if="row.rolling" type="success" size="small">Rolling</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="entry_time" label="Entry Time" width="180" sortable>
          <template #default="{ row }">
            {{ formatDate(row.entry_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="modify_time" label="Modified Time" width="180" sortable>
          <template #default="{ row }">
            {{ formatDate(row.modify_time) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">Edit</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Add/Edit dialog -->
    <el-dialog
      :title="dialogType === 'add' ? 'Add Process' : 'Edit Process'"
      v-model="dialogVisible"
      width="60%"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="process-form"
      >
        <el-form-item label="Fabrication Process" prop="fabrication">
          <el-input v-model="form.fabrication" placeholder="Please enter fabrication process" />
        </el-form-item>

        <!-- Homogenization -->
        <el-form-item label="Homogenization">
          <el-switch v-model="form.homogenization" />
          <template v-if="form.homogenization">
            <el-form-item label="Temperature (℃)">
              <el-input-number v-model="form.homogenize_temp" :precision="1" :step="10" />
            </el-form-item>
            <el-form-item label="Time (h)">
              <el-input-number v-model="form.homogenize_time" :precision="1" :step="0.5" />
            </el-form-item>
          </template>
        </el-form-item>

        <!-- Normalization -->
        <el-form-item label="Normalization">
          <el-switch v-model="form.normalization" />
          <template v-if="form.normalization">
            <el-form-item label="Temperature (℃)">
              <el-input-number v-model="form.normalize_temp" :precision="1" :step="10" />
            </el-form-item>
            <el-form-item label="Time (h)">
              <el-input-number v-model="form.normalize_time" :precision="1" :step="0.5" />
            </el-form-item>
          </template>
        </el-form-item>

        <!-- Annealing -->
        <el-form-item label="Annealing">
          <el-switch v-model="form.annealing" />
          <template v-if="form.annealing">
            <el-form-item label="Temperature (℃)">
              <el-input-number v-model="form.annealing_temp" :precision="1" :step="10" />
            </el-form-item>
            <el-form-item label="Time (h)">
              <el-input-number v-model="form.annealing_time" :precision="1" :step="0.5" />
            </el-form-item>
          </template>
        </el-form-item>

        <!-- Tempering -->
        <el-form-item label="Tempering">
          <el-switch v-model="form.tempering" />
          <template v-if="form.tempering">
            <el-form-item label="Temperature (℃)">
              <el-input-number v-model="form.tempering_temp" :precision="1" :step="10" />
            </el-form-item>
            <el-form-item label="Time (h)">
              <el-input-number v-model="form.tempering_time" :precision="1" :step="0.5" />
            </el-form-item>
          </template>
        </el-form-item>

        <!-- Quenching -->
        <el-form-item label="Quenching">
          <el-switch v-model="form.quenching" />
          <template v-if="form.quenching">
            <el-form-item label="Type">
              <el-input v-model="form.quenching_type" placeholder="Please enter quenching type" />
            </el-form-item>
            <el-form-item label="Temperature (℃)">
              <el-input-number v-model="form.quenching_temp" :precision="1" :step="10" />
            </el-form-item>
          </template>
        </el-form-item>

        <!-- Rolling -->
        <el-form-item label="Rolling">
          <el-switch v-model="form.rolling" />
          <template v-if="form.rolling">
            <el-form-item label="Temperature (℃)">
              <el-input-number v-model="form.rolling_temp" :precision="1" :step="10" />
            </el-form-item>
            <el-form-item label="Reduction (%)">
              <el-input-number v-model="form.reduction" :precision="1" :step="0.5" />
            </el-form-item>
          </template>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="handleSubmit">Confirm</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Import dialog -->
    <el-dialog
      title="Import Data"
      v-model="importDialogVisible"
      width="30%"
    >
      <el-upload
        class="upload-demo"
        drag
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        :before-upload="beforeUpload"
        :file-list="uploadFile ? [uploadFile] : []"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          Drop file here or <em>click to upload</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            Please upload an Excel file (.xlsx, .xls)
            <el-button type="text" @click="downloadTemplate">Download Template</el-button>
          </div>
        </template>
      </el-upload>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importDialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="submitImport">Confirm</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Export dialog -->
    <el-dialog
      title="Export Data"
      v-model="exportDialogVisible"
      width="30%"
    >
      <el-form :model="exportForm" label-width="100px">
        <el-form-item label="Export Format">
          <el-radio-group v-model="exportForm.format">
            <el-radio label="excel">Excel</el-radio>
            <el-radio label="csv">CSV</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Export Range">
          <el-radio-group v-model="exportForm.range">
            <el-radio label="all">All Data</el-radio>
            <el-radio label="current">Current Page</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="exportDialogVisible = false">Cancel</el-button>
          <el-button type="primary" :loading="exportLoading" @click="handleExport">Confirm</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { getProcesses, createProcess, updateProcess, deleteProcess, importProcesses, exportProcesses } from '@/api/process'

const escapeHtml = (s) =>
  String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')

const formatProcessImportErrorLine = (err) => {
  if (err == null) return '<p>Unknown import error.</p>'
  if (typeof err === 'string') return '<p>Import validation failed.</p>'
  const row = err.row != null ? err.row : '—'
  return `<p>Row ${escapeHtml(row)}: Import validation failed.</p>`
}

// 基础数据
const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchQuery = ref('')

// 处理数据项
const processItem = (item) => {
  if (!item) return null
  return {
    ...item,
    // 确保所有布尔值字段都是布尔Type
    homogenization: Boolean(item.homogenization),
    normalization: Boolean(item.normalization),
    annealing: Boolean(item.annealing),
    tempering: Boolean(item.tempering),
    quenching: Boolean(item.quenching),
    rolling: Boolean(item.rolling),
    // 确保数值字段是数字Type
    homogenize_temp: Number(item.homogenize_temp) || null,
    homogenize_time: Number(item.homogenize_time) || null,
    normalize_temp: Number(item.normalize_temp) || null,
    normalize_time: Number(item.normalize_time) || null,
    annealing_temp: Number(item.annealing_temp) || null,
    annealing_time: Number(item.annealing_time) || null,
    tempering_temp: Number(item.tempering_temp) || null,
    tempering_time: Number(item.tempering_time) || null,
    quenching_temp: Number(item.quenching_temp) || null,
    rolling_temp: Number(item.rolling_temp) || null,
    reduction: Number(item.reduction) || null
  }
}

// 对话框控制
const dialogVisible = ref(false)
const dialogType = ref('add')
const importDialogVisible = ref(false)
const exportDialogVisible = ref(false)
const exportLoading = ref(false)
const formRef = ref(null)
const uploadFile = ref(null)

// 表单数据
const form = ref({
  fabrication: '',
  homogenization: false,
  homogenize_temp: 0,
  homogenize_time: 0,
  normalization: false,
  normalize_temp: 0,
  normalize_time: 0,
  annealing: false,
  annealing_temp: 0,
  annealing_time: 0,
  tempering: false,
  tempering_temp: 0,
  tempering_time: 0,
  quenching: false,
  quenching_type: '',
  quenching_temp: 0,
  rolling: false,
  rolling_temp: 0,
  reduction: 0
})

// 表单验证规则
const rules = {
  fabrication: [
    { required: true, message: 'Please enter fabrication process', trigger: 'blur' },
    { min: 2, max: 100, message: 'Length must be between 2 and 100 characters', trigger: 'blur' }
  ]
}

// 导出表单
const exportForm = ref({
  format: 'excel',
  range: 'all'
})

// 获取数据列表
const fetchData = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value?.trim() || ''
    }
    
    const response = await getProcesses(params)
    
    // 详细的数据格式验证
    if (!response) {
      throw new Error('No response received from server')
    }

    if (!response.data) {
      throw new Error('Response is missing data field')
    }

    const responseData = response.data

    // 如果后端直接返回数组，则直接使用
    if (Array.isArray(responseData)) {
      tableData.value = responseData.map(processItem).filter(Boolean)
      total.value = responseData.length
      return
    }

    // 如果是分页格式，则解构分页数据
    const { results, count, page, page_size, total_pages } = responseData

    if (!results) {
      throw new Error('Response data is missing results field')
    }

    if (!Array.isArray(results)) {
      console.error('Invalid results format:')
      throw new Error('results field is not an array')
    }
    
    // 处理数据
    tableData.value = results.map(processItem).filter(Boolean)
    
    // 更新分页信息
    total.value = parseInt(count) || results.length
    if (page) {
      currentPage.value = parseInt(page)
    }
    if (page_size) {
      pageSize.value = parseInt(page_size)
    }
    
  } catch (error) {
    console.error('Failed to load data:')
    ElMessage.error('Failed to load process data')
    tableData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// Search处理
const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

// ResetSearch
const handleReset = () => {
  searchQuery.value = ''
  currentPage.value = 1
  fetchData()
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  fetchData()
}

const handlePageChange = (val) => {
  currentPage.value = val
  fetchData()
}

// Add/Edit处理
const handleAdd = () => {
  dialogType.value = 'add'
  form.value = {
    fabrication: '',
    homogenization: false,
    homogenize_temp: 0,
    homogenize_time: 0,
    normalization: false,
    normalize_temp: 0,
    normalize_time: 0,
    annealing: false,
    annealing_temp: 0,
    annealing_time: 0,
    tempering: false,
    tempering_temp: 0,
    tempering_time: 0,
    quenching: false,
    quenching_type: '',
    quenching_temp: 0,
    rolling: false,
    rolling_temp: 0,
    reduction: 0
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogType.value = 'edit'
  form.value = { ...row }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    if (dialogType.value === 'add') {
      await createProcess(form.value)
      ElMessage.success('Added successfully')
    } else {
      await updateProcess(form.value.process_id, form.value)
      ElMessage.success('Updated successfully')
    }
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error('Submission failed:')
    ElMessage.error('Failed to save the process')
  }
}

// Delete处理
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('Are you sure you want to delete this process?', 'Confirm', {
      type: 'warning',
      confirmButtonText: 'Confirm',
      cancelButtonText: 'Cancel'
    })
    await deleteProcess(row.process_id)
    ElMessage.success('Deleted successfully')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete failed:')
      ElMessage.error('Failed to delete the process')
    }
  }
}

// 导入导出处理
const handleImport = () => {
  importDialogVisible.value = true
}

const handleFileChange = (file) => {
  uploadFile.value = file
}

const beforeUpload = (file) => {
  const isExcel = /\.(xlsx|xls)$/.test(file.name.toLowerCase())
  if (!isExcel) {
    ElMessage.error('Only Excel files are allowed!')
    return false
  }
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('File size cannot exceed 10MB!')
    return false
  }
  return true
}

const submitImport = async () => {
  if (!uploadFile.value) {
    ElMessage.warning('Please select a file to import')
    return
  }
  
  try {
    loading.value = true
    const formData = new FormData()
    formData.append('file', uploadFile.value.raw)
    
    // 显示加载Confirm
    const loadingInstance = ElLoading.service({
      lock: true,
      text: 'Importing data, please wait...',
      background: 'rgba(0, 0, 0, 0.7)'
    })
    
    try {
      const response = await importProcesses(formData)
      
      if (response.data && response.data.success) {
        ElMessage.success(`Import successful: ${response.data.success_count} of ${response.data.total} records imported`)
        
        if (response.data.errors && response.data.errors.length > 0) {
          ElMessageBox.alert(
            `<div style="max-height: 300px; overflow-y: auto;">
              <p>The following errors were found during import:</p>
              ${response.data.errors.map((err) => formatProcessImportErrorLine(err)).join('')}
            </div>`,
            'Import Results',
            {
              dangerouslyUseHTMLString: true,
              confirmButtonText: 'Confirm'
            }
          )
        }
        
        importDialogVisible.value = false
        uploadFile.value = null
        fetchData()
      } else {
        throw new Error(response.data?.message || 'Import failed')
      }
    } finally {
      loadingInstance.close()
    }
  } catch (error) {
    console.error('Import failed:')
    ElMessage.error('Import failed. Please check the file and try again.')
  } finally {
    loading.value = false
  }
}

const handleExport = async () => {
  try {
    exportLoading.value = true
    const processIds = exportForm.value.range === 'current' ? 
      tableData.value.map(item => item.process_id) : []
    
    const response = await exportProcesses({
      format: exportForm.value.format,
      process_ids: processIds
    })
    
    if (!response || !response.data) {
      throw new Error('Export failed: invalid response data')
    }
    
    // 创建Blob对象
    const blob = new Blob([response.data], {
      type: exportForm.value.format === 'csv' ? 
        'text/csv;charset=utf-8' : 
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `processes_${new Date().toISOString().split('T')[0]}.${exportForm.value.format === 'csv' ? 'csv' : 'xlsx'}`
    
    // 触发下载
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('Export successful')
    exportDialogVisible.value = false
  } catch (error) {
    console.error('Export failed:')
    ElMessage.error('Export failed. Please try again.')
  } finally {
    exportLoading.value = false
  }
}

const downloadTemplate = () => {
  const link = document.createElement('a')
  link.href = '/templates/process_import_template.xlsx'
  link.download = 'process_import_template.xlsx'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const formatDate = (date) => {
  if (!date) return 'No data'
  try {
    return new Date(date).toLocaleString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    })
  } catch (error) {
    console.error('Date formatting failed:')
    return 'No data'
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.process-list-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-buttons {
  display: flex;
  gap: 10px;
}

.search-bar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.search-input {
  width: 300px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.process-form {
  max-height: 60vh;
  overflow-y: auto;
  padding-right: 20px;
}

:deep(.el-form-item__content) {
  flex-wrap: wrap;
}

:deep(.el-switch + .el-form-item) {
  margin-left: 20px;
  margin-bottom: 0;
}

:deep(.el-upload-dragger) {
  width: 100%;
}

:deep(.el-upload__tip) {
  margin-top: 10px;
  line-height: 1.4;
}
</style> 
