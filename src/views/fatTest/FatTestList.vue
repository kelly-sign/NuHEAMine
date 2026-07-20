<template>
  <div class="fat-test-list-container">
    <PageHeader title="Fatigue Test Table" />
    
    <div class="list-actions">
      <!-- Search form -->
      <el-form :inline="true" :model="searchForm" class="search-form" @submit.prevent>
        <el-form-item label="Material ID">
          <el-input v-model="searchForm.material_id" placeholder="Material ID" clearable @keyup.enter="handleSearch"></el-input>
        </el-form-item>
        <el-form-item label="Process ID">
          <el-input v-model="searchForm.process_id" placeholder="Process ID" clearable @keyup.enter="handleSearch"></el-input>
        </el-form-item>
        <el-form-item label="Environment Temperature (℃)">
          <div class="range-input">
            <el-input v-model="searchForm.environment_temp_min" placeholder="Min" @keyup.enter="handleSearch" class="range-input-min"></el-input>
            <span class="range-separator">-</span>
            <el-input v-model="searchForm.environment_temp_max" placeholder="Max" @keyup.enter="handleSearch" class="range-input-max"></el-input>
          </div>
        </el-form-item>
        <el-form-item label="Stress Ratio">
          <div class="range-input">
            <el-input v-model="searchForm.stress_ratio_min" placeholder="Min" @keyup.enter="handleSearch" class="range-input-min"></el-input>
            <span class="range-separator">-</span>
            <el-input v-model="searchForm.stress_ratio_max" placeholder="Max" @keyup.enter="handleSearch" class="range-input-max"></el-input>
          </div>
        </el-form-item>
        <el-form-item label="Stress Range (MPa)">
          <div class="range-input">
            <el-input v-model="searchForm.stress_range_min" placeholder="Min" @keyup.enter="handleSearch" class="range-input-min"></el-input>
            <span class="range-separator">-</span>
            <el-input v-model="searchForm.stress_range_max" placeholder="Max" @keyup.enter="handleSearch" class="range-input-max"></el-input>
          </div>
        </el-form-item>
        <el-form-item label="Mean Stress (MPa)">
          <div class="range-input">
            <el-input v-model="searchForm.mean_stress_min" placeholder="Min" @keyup.enter="handleSearch" class="range-input-min"></el-input>
            <span class="range-separator">-</span>
            <el-input v-model="searchForm.mean_stress_max" placeholder="Max" @keyup.enter="handleSearch" class="range-input-max"></el-input>
          </div>
        </el-form-item>
        <el-form-item label="Fatigue Life (cycles)">
          <div class="range-input">
            <el-input v-model="searchForm.fatigue_life_min" placeholder="Min" @keyup.enter="handleSearch" class="range-input-min"></el-input>
            <span class="range-separator">-</span>
            <el-input v-model="searchForm.fatigue_life_max" placeholder="Max" @keyup.enter="handleSearch" class="range-input-max"></el-input>
          </div>
        </el-form-item>
        <el-form-item label="Fatigue Limit (MPa)">
          <div class="range-input">
            <el-input v-model="searchForm.fatigue_limit_min" placeholder="Min" @keyup.enter="handleSearch" class="range-input-min"></el-input>
            <span class="range-separator">-</span>
            <el-input v-model="searchForm.fatigue_limit_max" placeholder="Max" @keyup.enter="handleSearch" class="range-input-max"></el-input>
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="resetSearchForm">Reset</el-button>
        </el-form-item>
      </el-form>
      
      <!-- Actions按钮 -->
      <div class="action-buttons">
        <el-button type="primary" @click="showAddDialog">Add</el-button>
        <el-button type="success" @click="showImportDialog">Import</el-button>
        <el-button type="warning" @click="handleExport">Export</el-button>
        <el-button type="danger" @click="handleBatchDelete" :disabled="selectedItems.length === 0">Delete Selected</el-button>
      </div>
    </div>
    
    <!-- Data table -->
    <el-table
      v-loading="loading"
      :data="tableData"
      stripe
      border
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="fatigue_id" label="Fatigue Test ID" width="100" sortable />
      <el-table-column label="Material ID" width="120">
        <template #default="scope">
          {{ scope.row.material?.material_id || scope.row.material_id }}
        </template>
      </el-table-column>
      <el-table-column label="Process ID" width="120">
        <template #default="scope">
          {{ scope.row.process?.process_id || scope.row.process_id }}
        </template>
      </el-table-column>
      <el-table-column prop="fatigue_method" label="Test Type" width="160">
        <template #default="scope">
          {{ formatFatigueMethod(scope.row.fatigue_method) }}
        </template>
      </el-table-column>
      <el-table-column prop="stress_ratio" label="Stress Ratio" width="120" />
      <el-table-column prop="stress_range" label="Stress Range" width="120" />
      <el-table-column prop="mean_stress" label="Mean Stress" width="120" />
      <el-table-column prop="loading_frequency" label="Loading Frequency" width="120" />
      <el-table-column prop="environment_temp" label="Environment Temperature" width="120" />
      <el-table-column prop="fatigue_life" label="Fatigue Life" width="120" />
      <el-table-column prop="fatigue_limit" label="Fatigue Limit" width="120" />
      <el-table-column prop="entry_time" label="Entry Time" width="180" />
      <el-table-column prop="modify_time" label="Update Time" width="180" />
      <el-table-column label="Actions" fixed="right" width="200">
        <template #default="scope">
          <el-button size="small" @click="showEditDialog(scope.row)">Edit</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.row)">Delete</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        background
        layout="total, sizes, prev, pager, next, jumper"
        :current-page="pagination.currentPage"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pagination.pageSize"
        :total="pagination.total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- Add/Edit dialog -->
    <el-dialog
      :title="dialogType === 'add' ? 'Add Fatigue Test Data' : 'Edit Fatigue Test Data'"
      v-model="dialogVisible"
      width="60%"
    >
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="Material ID" prop="material_id">
          <el-input v-model="formData.material_id" placeholder="Please enter material ID" />
        </el-form-item>
        <el-form-item label="Process ID" prop="process_id">
          <el-input v-model="formData.process_id" placeholder="Please enter process ID" />
        </el-form-item>
        <el-form-item label="Test Type" prop="fatigue_method">
          <el-select v-model="formData.fatigue_method" placeholder="Please select a test type" style="width: 100%">
            <el-option label="High-Cycle Fatigue" value="高周疲劳" />
            <el-option label="Low-Cycle Fatigue" value="低周疲劳" />
            <el-option label="Very-High-Cycle Fatigue" value="超高周疲劳" />
            <el-option label="Thermal Fatigue" value="热疲劳" />
            <el-option label="Contact Fatigue" value="接触疲劳" />
          </el-select>
        </el-form-item>
        <el-form-item label="Stress Ratio" prop="stress_ratio">
          <el-input v-model.number="formData.stress_ratio" placeholder="Enter the stress ratio" />
        </el-form-item>
        <el-form-item label="Stress Range" prop="stress_range">
          <el-input v-model.number="formData.stress_range" placeholder="Enter the stress range" />
        </el-form-item>
        <el-form-item label="Mean Stress" prop="mean_stress">
          <el-input v-model.number="formData.mean_stress" placeholder="Enter the mean stress" />
        </el-form-item>
        <el-form-item label="Loading Frequency" prop="loading_frequency">
          <el-input v-model.number="formData.loading_frequency" placeholder="Enter the loading frequency" />
        </el-form-item>
        <el-form-item label="Environment Temperature" prop="environment_temp">
          <el-input v-model.number="formData.environment_temp" placeholder="Enter the environment temperature" />
        </el-form-item>
        <el-form-item label="Fatigue Life" prop="fatigue_life">
          <el-input v-model.number="formData.fatigue_life" placeholder="Enter the fatigue life" />
        </el-form-item>
        <el-form-item label="Fatigue Limit" prop="fatigue_limit">
          <el-input v-model.number="formData.fatigue_limit" placeholder="Enter the fatigue limit" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="submitForm">Confirm</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- Import dialog -->
    <el-dialog title="Import Fatigue Test Data" v-model="importDialogVisible" width="40%">
      <el-upload
        class="upload-demo"
        drag
        :action="null"
        :auto-upload="false"
        :on-change="handleFileChange"
        :before-upload="beforeImportUpload"
        :show-file-list="true"
        accept=".xlsx,.xls,.csv"
        :multiple="false"
        name="file"
        ref="uploadRef"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">Drop a file here or <em>click to upload</em></div>
        <template #tip>
          <div class="el-upload__tip">
            <p>Upload an Excel or CSV file containing Material ID and Process ID columns.</p>
            <p>Optional columns: Fatigue Test ID, Test Type, Stress Ratio, Stress Range, Mean Stress, Loading Frequency, Environment Temperature, Fatigue Life, and Fatigue Limit.</p>
            <p>If a specified Fatigue Test ID already exists, a new ID will be generated and the existing record will not be overwritten.</p>
            <a href="javascript:void(0)" @click="downloadTemplate">Download Import Template</a>
          </div>
        </template>
      </el-upload>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importDialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="submitImport">Upload</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- Export dialog -->
    <el-dialog title="Export Fatigue Test Data" v-model="exportDialogVisible" width="40%">
      <el-form :model="exportForm" label-width="80px">
        <el-form-item label="Export Format">
          <el-radio-group v-model="exportForm.format">
            <el-radio label="excel">Excel</el-radio>
            <el-radio label="csv">CSV</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Export Range">
          <el-radio-group v-model="exportForm.scope">
            <el-radio label="all">All Data</el-radio>
            <el-radio label="selected">Selected Data</el-radio>
            <el-radio label="filtered">Filtered Data</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="exportDialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="confirmExport">Export</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import PageHeader from '@/components/common/PageHeader.vue'
import { 
  getFatTests, getFatTestDetail, createFatTest, 
  updateFatTest, deleteFatTest, exportFatTests, importFatTests 
} from '@/api/fatTest'
import { getToken } from '@/utils/auth'

export default {
  name: 'FatTestList',
  components: {
    PageHeader,
    UploadFilled
  },
  setup() {
    // 数据定义
    const loading = ref(false)
    const tableData = ref([])
    const selectedItems = ref([])
    const dialogVisible = ref(false)
    const dialogType = ref('add') // 'add' 或 'edit'
    const formRef = ref(null)
    const currentId = ref(null)
    const importDialogVisible = ref(false)
    const exportDialogVisible = ref(false)
    
    // 分页参数
    const pagination = reactive({
      currentPage: 1,
      pageSize: 10,
      total: 0
    })
    
    // Search form
    const searchForm = reactive({
      material_id: '',
      process_id: '',
      environment_temp_min: '',
      environment_temp_max: '',
      stress_ratio_min: '',
      stress_ratio_max: '',
      stress_range_min: '',
      stress_range_max: '',
      mean_stress_min: '',
      mean_stress_max: '',
      fatigue_life_min: '',
      fatigue_life_max: '',
      fatigue_limit_min: '',
      fatigue_limit_max: ''
    })

    const fatigueMethodLabels = {
      '高周疲劳': 'High-Cycle Fatigue',
      '低周疲劳': 'Low-Cycle Fatigue',
      '超高周疲劳': 'Very-High-Cycle Fatigue',
      '热疲劳': 'Thermal Fatigue',
      '接触疲劳': 'Contact Fatigue',
      'High Cycle Fatigue': 'High-Cycle Fatigue',
      'Low Cycle Fatigue': 'Low-Cycle Fatigue',
      'Ultra High Cycle Fatigue': 'Very-High-Cycle Fatigue',
      'Very High Cycle Fatigue': 'Very-High-Cycle Fatigue'
    }

    const formatFatigueMethod = (value) => fatigueMethodLabels[value] || value || '-'
    
    // 表单数据
    const formData = reactive({
      material_id: '',
      process_id: '',
      fatigue_method: '',
      stress_ratio: '',
      stress_range: '',
      mean_stress: '',
      loading_frequency: '',
      environment_temp: '',
      fatigue_life: '',
      fatigue_limit: ''
    })
    
    // 导出表单
    const exportForm = reactive({
      format: 'excel', // 'excel' 或 'csv'
      scope: 'all' // 'all', 'selected', 'filtered'
    })
    
    // 验证规则
    const rules = {
      material_id: [
        { required: true, message: 'Please enter material ID', trigger: 'blur' },
        { type: 'integer', message: 'Material ID must be an integer', trigger: 'blur', transform: (value) => parseInt(value, 10) }
      ],
      process_id: [
        { required: true, message: 'Please enter process ID', trigger: 'blur' },
        { type: 'integer', message: 'Process ID must be an integer', trigger: 'blur', transform: (value) => parseInt(value, 10) }
      ],
      fatigue_method: [
        { required: false, message: 'Please select a test type', trigger: 'change' }
      ],
      stress_ratio: [
        { required: false, trigger: 'blur' },
        { 
          type: 'number', 
          message: 'Stress ratio must be numeric', 
          trigger: 'blur',
          transform: (value) => value === '' ? undefined : parseFloat(value)
        }
      ],
      stress_range: [
        { required: false, trigger: 'blur' },
        { 
          type: 'number', 
          message: 'Stress range must be numeric', 
          trigger: 'blur',
          transform: (value) => value === '' ? undefined : parseFloat(value)
        }
      ],
      mean_stress: [
        { required: false, trigger: 'blur' },
        { 
          type: 'number', 
          message: 'Mean stress must be numeric', 
          trigger: 'blur',
          transform: (value) => value === '' ? undefined : parseFloat(value)
        }
      ],
      loading_frequency: [
        { required: false, trigger: 'blur' },
        { 
          type: 'number', 
          message: 'Loading frequency must be numeric', 
          trigger: 'blur',
          transform: (value) => value === '' ? undefined : parseFloat(value)
        }
      ],
      environment_temp: [
        { required: false, trigger: 'blur' },
        { 
          type: 'number', 
          message: 'Environment temperature must be numeric', 
          trigger: 'blur',
          transform: (value) => value === '' ? undefined : parseFloat(value),
          validator: (rule, value, callback) => {
            if (value !== '' && value !== null && value !== undefined && value < -273.15) {
              callback(new Error('Environment temperature cannot be below absolute zero (-273.15℃)'));
            } else {
              callback();
            }
          }
        }
      ],
      fatigue_life: [
        { required: false, trigger: 'blur' },
        { 
          type: 'number', 
          message: 'Fatigue life must be numeric', 
          trigger: 'blur',
          transform: (value) => value === '' ? undefined : parseFloat(value),
          validator: (rule, value, callback) => {
            if (value !== '' && value !== null && value !== undefined && value < 0) {
              callback(new Error('Fatigue life cannot be negative'));
            } else {
              callback();
            }
          }
        }
      ],
      fatigue_limit: [
        { required: false, trigger: 'blur' },
        { 
          type: 'number', 
          message: 'Fatigue limit must be numeric', 
          trigger: 'blur',
          transform: (value) => value === '' ? undefined : parseFloat(value)
        }
      ]
    }
    
    // 上传配置
    const importAction = `${process.env.VUE_APP_API_URL}/fat-tests/import_data/`
    const uploadHeaders = {
      Authorization: `Bearer ${getToken()}`
    }

    // 初始加载数据
    const loadData = async () => {
      loading.value = true
      try {
        const params = {
          page: pagination.currentPage,
          page_size: pagination.pageSize,
          ...searchForm
        }
        
        const response = await getFatTests(params)
        if (response && response.data) {
          tableData.value = response.data.results || response.data
          pagination.total = response.data.count || tableData.value.length
        }
      } catch (error) {
        console.error('Failed to load fatigue test data:')
        ElMessage.error('Failed to load fatigue test data. Please try again.')
      } finally {
        loading.value = false
      }
    }
    
    // Search
    const handleSearch = () => {
      pagination.currentPage = 1
      loadData()
    }
    
    // ResetSearch form
    const resetSearchForm = () => {
      for (const key in searchForm) {
        searchForm[key] = ''
      }
      handleSearch()
    }
    
    // 选择变更
    const handleSelectionChange = (selection) => {
      selectedItems.value = selection
    }
    
    // 分页大小变更
    const handleSizeChange = (size) => {
      pagination.pageSize = size
      loadData()
    }
    
    // 分页页码变更
    const handleCurrentChange = (page) => {
      pagination.currentPage = page
      loadData()
    }
    
    // 显示Add对话框
    const showAddDialog = () => {
      dialogType.value = 'add'
      resetFormData()
      dialogVisible.value = true
    }
    
    // 显示Edit对话框
    const showEditDialog = async (row) => {
      dialogType.value = 'edit'
      currentId.value = row.fatigue_id
      
      try {
        const response = await getFatTestDetail(row.fatigue_id)
        if (response && response.data) {
          const data = response.data
          
          formData.material_id = data.material_id || (data.material ? data.material.material_id : '')
          formData.process_id = data.process_id || (data.process ? data.process.process_id : '')
          formData.fatigue_method = data.fatigue_method || ''
          formData.stress_ratio = data.stress_ratio !== undefined && data.stress_ratio !== null ? data.stress_ratio : ''
          formData.stress_range = data.stress_range !== undefined && data.stress_range !== null ? data.stress_range : ''
          formData.mean_stress = data.mean_stress !== undefined && data.mean_stress !== null ? data.mean_stress : ''
          formData.loading_frequency = data.loading_frequency !== undefined && data.loading_frequency !== null ? data.loading_frequency : ''
          formData.environment_temp = data.environment_temp !== undefined && data.environment_temp !== null ? data.environment_temp : ''
          formData.fatigue_life = data.fatigue_life !== undefined && data.fatigue_life !== null ? data.fatigue_life : ''
          formData.fatigue_limit = data.fatigue_limit !== undefined && data.fatigue_limit !== null ? data.fatigue_limit : ''
        }
      } catch (error) {
        console.error('Failed to load details:')
        ElMessage.error('Failed to load record details. Please try again.')
      }
      
      dialogVisible.value = true
    }
    
    // Reset表单数据
    const resetFormData = () => {
      for (const key in formData) {
        formData[key] = ''
      }
      currentId.value = null
    }
    
    // 提交表单
    const submitForm = () => {
      if (!formRef.value) return
      
      formRef.value.validate(async (valid) => {
        if (valid) {
          try {
            // 准备数据 - 确保数值字段正确转换
            const preparedData = {
              material_id: parseInt(formData.material_id, 10),
              process_id: parseInt(formData.process_id, 10),
              fatigue_method: formData.fatigue_method,
              // 处理数值字段：空字符串转为null，其他转为数值
              stress_ratio: formData.stress_ratio === '' ? null : parseFloat(formData.stress_ratio),
              stress_range: formData.stress_range === '' ? null : parseFloat(formData.stress_range),
              mean_stress: formData.mean_stress === '' ? null : parseFloat(formData.mean_stress),
              loading_frequency: formData.loading_frequency === '' ? null : parseFloat(formData.loading_frequency),
              environment_temp: formData.environment_temp === '' ? null : parseFloat(formData.environment_temp),
              fatigue_life: formData.fatigue_life === '' ? null : parseFloat(formData.fatigue_life),
              fatigue_limit: formData.fatigue_limit === '' ? null : parseFloat(formData.fatigue_limit)
            }
            
            if (dialogType.value === 'add') {
              await createFatTest(preparedData)
              ElMessage.success('Added successfully')
            } else {
              await updateFatTest(currentId.value, preparedData)
              ElMessage.success('Updated successfully')
            }
            
            dialogVisible.value = false
            loadData()
          } catch (error) {
            console.error('Operation failed:')
            
            // 显示错误信息
            ElMessage.error(`Failed to ${dialogType.value === 'add' ? 'add' : 'update'} the fatigue test data`)
          }
        }
      })
    }
    
    // Delete
    const handleDelete = (row) => {
      ElMessageBox.confirm('This will permanently delete the record. Continue?', 'Confirm', {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }).then(async () => {
        try {
          await deleteFatTest(row.fatigue_id)
          ElMessage.success('Deleted successfully')
          loadData()
        } catch (error) {
          console.error('Delete failed:')
          ElMessage.error('Failed to delete the record. Please try again.')
        }
      }).catch(() => {
        // UserCancelDelete
      })
    }
    
    // 批量Delete
    const handleBatchDelete = () => {
      if (selectedItems.value.length === 0) {
        ElMessage.warning('Please select at least one record')
        return
      }
      
      ElMessageBox.confirm(`This will permanently delete ${selectedItems.value.length} records. Continue?`, 'Confirm', {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }).then(async () => {
        try {
          const promises = selectedItems.value.map(item => deleteFatTest(item.fatigue_id))
          await Promise.all(promises)
          ElMessage.success('Selected records deleted successfully')
          loadData()
        } catch (error) {
          console.error('Batch delete failed:')
          ElMessage.error('Failed to delete the selected records. Please try again.')
        }
      }).catch(() => {
        // UserCancelDelete
      })
    }
    
    // 显示Import dialog
    const showImportDialog = () => {
      importDialogVisible.value = true
    }
    
    // 导入前验证
    const beforeImportUpload = (file) => {
      const validTypes = ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv']
      if (!validTypes.includes(file.type)) {
        ElMessage.error('Only Excel or CSV files are allowed')
        return false
      }
      return true
    }
    
    // 选中文件处理
    const uploadRef = ref(null)
    const selectedFile = ref(null)
    
    const handleFileChange = (file) => {
      selectedFile.value = file.raw
    }
    
    // 提交导入
    const submitImport = async () => {
      if (!selectedFile.value) {
        ElMessage.warning('Please select a file first')
        return
      }
      
      // 创建FormData
      const formData = new FormData()
      formData.append('file', selectedFile.value)
      
      try {
        loading.value = true
        ElMessage.info('Uploading data, please wait...')
        
        // Add随机数防止缓存
        const timestamp = new Date().getTime()
        const response = await importFatTests(formData)
        
        if (response && response.data) {
          const responseData = response.data
          
          // 处理响应结果
          if (responseData.success_count > 0 || (responseData.success === true && responseData.success_count > 0)) {
            // 有成功导入的记录
            const errorCount = responseData.error_count || 0
            
            if (errorCount > 0) {
              ElMessage({
                message: `Import partially complete: ${responseData.success_count} succeeded and ${errorCount} failed`,
                type: 'warning',
                duration: 5000
              })
              
              // 显示错误详情
              if (responseData.errors && responseData.errors.length > 0) {
                const errorDetails = responseData.errors.map(err => `Row ${err.row}: Import validation failed.`).join('\n')
                console.error('Import error details:')
                ElMessageBox.alert(errorDetails, 'Error Details', {
                  confirmButtonText: 'Confirm',
                  type: 'warning'
                })
              }
            } else {
              const autoIncrementCount = responseData.auto_increment_count || 0
              let successMessage = `Import successful: ${responseData.success_count} records`
              if (autoIncrementCount > 0) {
                successMessage += `; ${autoIncrementCount} records used automatically generated IDs`
              }
              
              ElMessage({
                message: successMessage,
                type: 'success'
              })
            }
            importDialogVisible.value = false
            // Reset上传组件
            if (uploadRef.value) {
              uploadRef.value.clearFiles()
            }
            selectedFile.value = null
            loadData() // 刷新数据
          } else if (responseData.error_count > 0 || (responseData.errors && responseData.errors.length > 0)) {
            // 只有错误记录
            let errorMsg = 'Import failed. The following rows contain errors:\n'
            const errors = responseData.errors || []
            errors.forEach(err => {
              errorMsg += `Row ${err.row}: Import validation failed.\n`
            })
            ElMessage({
              message: 'Import failed. Review the error details.',
              type: 'error',
              duration: 5000
            })
            ElMessageBox.alert(errorMsg, 'Error Details', {
              confirmButtonText: 'Confirm',
              type: 'error'
            })
          } else if (responseData.detail) {
            // 有错误详情
            ElMessage.error('Import failed. Please check the file and try again.')
          } else {
            // 无法识别的响应格式
            ElMessage.success('Operation complete. Refresh the page to view the latest data.')
            importDialogVisible.value = false
            loadData()
          }
        }
      } catch (error) {
        console.error('Import failed:')
        const errorMsg = 'Import failed. Please check the file and data format.'
        
        ElMessage({
          message: errorMsg,
          type: 'error',
          duration: 5000
        })
      } finally {
        loading.value = false
      }
    }
    
    // 下载导入模板
    const downloadTemplate = () => {
      // 创建确认对话框
      ElMessageBox.confirm(
        'Select the template language',
        'Download Template',
        {
          confirmButtonText: 'Standard Template',
          cancelButtonText: 'English Template',
          distinguishCancelAndClose: true,
          type: 'info'
        }
      ).then(() => {
        // User选择了中文模板
        downloadTemplateWithLang('zh')
      }).catch((action) => {
        if (action === 'cancel') {
          // User选择了英文模板
          downloadTemplateWithLang('en')
        }
      })
    }
    
    // 根据语言Download Template
    const downloadTemplateWithLang = (lang) => {
      // 设置表头和示例数据
      let headers, sampleData, filename
      
      if (lang === 'zh') {
        // 中文模板
        headers = ['Fatigue Test ID', 'Material ID', 'Process ID', 'Test Type', 'Stress Ratio', 'Stress Range', 'Mean Stress', 'Loading Frequency', 'Environment Temperature', 'Fatigue Life', 'Fatigue Limit']
        sampleData = ['', '1', '1', 'High Cycle Fatigue', '0.1', '200', '100', '10', '25', '10000', '150']
        filename = 'fatigue_test_import_template_standard.csv'
      } else {
        // 英文模板
        headers = ['Fatigue Test ID', 'Material ID', 'Process ID', 'Test Type', 'Stress Ratio', 'Stress Range', 'Mean Stress', 'Loading Frequency', 'Environment Temperature', 'Fatigue Life', 'Fatigue Limit']
        sampleData = ['', '1', '1', 'High Cycle Fatigue', '0.1', '200', '100', '10', '25', '10000', '150']
        filename = 'fatigue_test_import_template.csv'
      }
      
      // 生成CSV文本
      let csvContent = ''
      
      // 增加BOM标记，确保Excel可以正确识别UTF-8编码
      csvContent = '\ufeff' + headers.join(',') + '\n' + sampleData.join(',')
      
      // 创建Blob对象，明确设置为UTF-8编码
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      
      // 创建下载链接并触发下载
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      
      // 清理
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      
      ElMessage.success(`${lang === 'zh' ? 'Standard' : 'English'} CSV template downloaded`)
    }
    
    // 处理导出
    const handleExport = () => {
      exportDialogVisible.value = true
    }
    
    // 确认导出
    const confirmExport = async () => {
      try {
        let property_ids = []
        
        if (exportForm.scope === 'selected') {
          if (selectedItems.value.length === 0) {
            ElMessage.warning('Please select at least one record')
            return
          }
          property_ids = selectedItems.value.map(item => item.fatigue_id)
        }
        
        const params = {
          format: exportForm.format,
          property_ids: property_ids
        }
        
        // 如果是筛选的数据，AddSearch条件
        if (exportForm.scope === 'filtered') {
          params.filter_params = { ...searchForm }
        }
        
        const response = await exportFatTests(params)
        
        if (response && response.data) {
          // 创建blob链接并下载
          const blob = new Blob([response.data], { 
            type: exportForm.format === 'csv' 
              ? 'text/csv' 
              : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
          })
          const link = document.createElement('a')
          link.href = URL.createObjectURL(blob)
          link.download = `fatigue_test_data_${new Date().getTime()}.${exportForm.format === 'csv' ? 'csv' : 'xlsx'}`
          link.click()
          URL.revokeObjectURL(link.href)
          
          ElMessage.success('Export successful')
          exportDialogVisible.value = false
        }
      } catch (error) {
        console.error('Export failed:')
        ElMessage.error('Export failed. Please try again.')
      }
    }
    
    onMounted(() => {
      loadData()
    })
    
    return {
      loading,
      tableData,
      pagination,
      searchForm,
      formatFatigueMethod,
      formData,
      rules,
      formRef,
      dialogVisible,
      dialogType,
      importDialogVisible,
      exportDialogVisible,
      exportForm,
      selectedItems,
      importAction,
      uploadHeaders,
      uploadRef,
      handleSearch,
      resetSearchForm,
      handleSelectionChange,
      handleSizeChange,
      handleCurrentChange,
      showAddDialog,
      showEditDialog,
      submitForm,
      handleDelete,
      handleBatchDelete,
      showImportDialog,
      beforeImportUpload,
      handleFileChange,
      submitImport,
      downloadTemplate,
      downloadTemplateWithLang,
      handleExport,
      confirmExport
    }
  }
}
</script>

<style scoped>
.fat-test-list-container {
  padding: 20px;
}

.list-actions {
  margin-bottom: 20px;
}

.search-form {
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.range-input {
  display: flex;
  align-items: center;
}

.range-input-min,
.range-input-max {
  width: 120px;
}

.range-separator {
  margin: 0 5px;
}

.action-buttons {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style> 
