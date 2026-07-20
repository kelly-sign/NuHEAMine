<template>
  <div class="page-container">
    <!-- Search区域 -->
    <div class="toolbar-container">
      <div class="search-container">
        <el-row :gutter="10">
          <el-col :span="8">
            <el-input
              v-model="searchQuery"
              placeholder="Search by irradiation type or ID"
              clearable
              @keyup.enter="handleSearch"
              @clear="handleSearch"
            >
              <template #append>
                <el-button icon="el-icon-search" @click="handleSearch"></el-button>
              </template>
            </el-input>
          </el-col>
          <el-col :span="6">
            <el-input
              v-model="irradiatIdFilter"
              placeholder="Filter by irradiation ID"
              clearable
              @keyup.enter="handleSearch"
              @clear="handleSearch"
            ></el-input>
          </el-col>
          <el-col :span="6">
            <el-input
              v-model="irradiatTypeFilter"
              placeholder="Filter by irradiation type"
              clearable
              @keyup.enter="handleSearch"
              @clear="handleSearch"
            ></el-input>
          </el-col>
        </el-row>
      </div>
      <!-- 工具按钮 -->
      <div class="button-container">
        <el-button type="primary" @click="showAddDialog">Add</el-button>
        <el-button type="danger" :disabled="!selectedRows.length" @click="batchDelete">Delete Selected</el-button>
        <el-button type="success" @click="showImportDialog">Import</el-button>
        <el-button type="info" @click="exportData">Export</el-button>
      </div>
    </div>

    <!-- Data table -->
    <el-table
      v-loading="loading"
      :data="tableData"
      @selection-change="handleSelectionChange"
      border
      style="width: 100%"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="irradiat_id" label="Irradiation ID" width="100" />
      <el-table-column prop="irradiat_type" label="Irradiation Type" />
      <el-table-column prop="irradiat_energy" label="Particle Energy (MeV)" />
      <el-table-column prop="irradiat_temp" label="Irradiation Temperature (°C)" />
      <el-table-column prop="irradiat_dose" label="Irradiation Dose (dpa)" />
      <el-table-column prop="irradiat_fluence" label="Irradiation Fluence (cm⁻²)" />
      <el-table-column prop="displac_damage" label="Displacement Damage (dpa)" />
      <el-table-column prop="entry_time" label="Entry Time" />
      <el-table-column label="Actions" width="150" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="showEditDialog(scope.row)">Edit</el-button>
          <el-button
            size="small"
            type="danger"
            @click="handleDelete(scope.row.irradiat_id)"
          >Delete</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        background
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalItems"
        :page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :current-page="currentPage"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- Add/Edit dialog -->
    <el-dialog
      :title="dialogType === 'add' ? 'Add Irradiation Condition' : 'Edit Irradiation Condition'"
      v-model="dialogVisible"
      width="500px"
    >
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
        <el-form-item label="Irradiation Type" prop="irradiat_type">
          <el-input v-model="formData.irradiat_type" placeholder="Enter the irradiation type" />
        </el-form-item>
        <el-form-item label="Particle Energy" prop="irradiat_energy">
          <el-input v-model.number="formData.irradiat_energy" placeholder="Enter the particle energy">
            <template #append>MeV</template>
          </el-input>
        </el-form-item>
        <el-form-item label="Irradiation Temperature" prop="irradiat_temp">
          <el-input v-model.number="formData.irradiat_temp" placeholder="Enter the irradiation temperature">
            <template #append>°C</template>
          </el-input>
        </el-form-item>
        <el-form-item label="Irradiation Dose" prop="irradiat_dose">
          <el-input v-model.number="formData.irradiat_dose" placeholder="Enter the irradiation dose">
            <template #append>dpa</template>
          </el-input>
        </el-form-item>
        <el-form-item label="Irradiation Fluence" prop="irradiat_fluence">
          <el-input v-model="formData.irradiat_fluence" placeholder="Enter the irradiation fluence">
            <template #append>cm⁻²</template>
          </el-input>
        </el-form-item>
        <el-form-item label="Displacement Damage" prop="displac_damage">
          <el-input v-model.number="formData.displac_damage" placeholder="Enter the displacement damage">
            <template #append>dpa</template>
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitForm">Confirm</el-button>
      </template>
    </el-dialog>

    <!-- Import dialog -->
    <el-dialog title="Import Irradiation Conditions" v-model="importDialogVisible" width="500px">
      <el-upload
        class="upload-container"
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        :file-list="uploadFileList"
      >
        <template #trigger>
          <el-button size="small" type="primary">Select File</el-button>
        </template>
        <template #tip>
          <div class="el-upload__tip">
            <p>Upload an Excel or CSV file.</p>
            <p>The file may contain these columns: Irradiation ID, Irradiation Type, Particle Energy (MeV), Irradiation Temperature (°C), Irradiation Dose (dpa), Irradiation Time, Irradiation Fluence (cm⁻²), and Displacement Damage (dpa).</p>
            <p>If an irradiation ID already exists, the record will be created with a new ID instead of overwriting existing data.</p>
            <a href="javascript:void(0)" @click="downloadTemplate">Download Import Template</a>
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitImport">Confirm</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  getIrrConditionList, 
  getIrrConditionDetail, 
  createIrrCondition, 
  updateIrrCondition, 
  deleteIrrCondition, 
  batchDeleteIrrConditions,
  exportIrrConditions,
  importIrrConditions
} from '@/api/irrCondition'

export default {
  name: 'IrrConditionList',
  
  setup() {
    // 表格数据
    const tableData = ref([])
    const loading = ref(false)
    const selectedRows = ref([])
    
    // Search和分页
    const searchQuery = ref('')
    const irradiatIdFilter = ref('')
    const irradiatTypeFilter = ref('')
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalItems = ref(0)
    
    // 对话框
    const dialogVisible = ref(false)
    const dialogType = ref('add') // 'add' 或 'edit'
    const currentId = ref(null)
    const formRef = ref(null)
    
    // 表单数据
    const formData = reactive({
      irradiat_type: '',
      irradiat_energy: '',
      irradiat_temp: '',
      irradiat_dose: '',
      irradiat_fluence: '',
      displac_damage: ''
    })
    
    // 验证规则
    const rules = {
      irradiat_type: [
        { required: false, message: 'Enter the irradiation type', trigger: 'blur' }
      ],
      irradiat_energy: [
        { required: false, trigger: 'blur' },
        { type: 'number', message: 'Particle energy must be a number', trigger: 'blur' }
      ],
      irradiat_temp: [
        { required: false, trigger: 'blur' },
        { type: 'number', message: 'Irradiation temperature must be a number', trigger: 'blur' }
      ],
      irradiat_dose: [
        { required: false, trigger: 'blur' },
        { type: 'number', message: 'Irradiation dose must be a number', trigger: 'blur' }
      ],
      irradiat_fluence: [
        { required: false, trigger: 'blur' },
        { max: 100, message: 'Irradiation fluence cannot exceed 100 characters', trigger: 'blur' }
      ],
      displac_damage: [
        { required: false, trigger: 'blur' },
        { type: 'number', message: 'Displacement damage must be a number', trigger: 'blur' }
      ]
    }
    
    // 导入相关
    const importDialogVisible = ref(false)
    const uploadFileList = ref([])
    const uploadFile = ref(null)
    
    // 加载数据
    const loadData = async () => {
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          page_size: pageSize.value,
          search: searchQuery.value,
          irradiat_id: irradiatIdFilter.value || undefined,
          irradiat_type: irradiatTypeFilter.value || undefined
        }
        const response = await getIrrConditionList(params)
        tableData.value = response.data.results
        totalItems.value = response.data.count
      } catch (error) {
        console.error('Failed to load data:')
        ElMessage.error('Failed to load data. Please try again later.')
      } finally {
        loading.value = false
      }
    }
    
    // 监听选择变化
    const handleSelectionChange = (rows) => {
      selectedRows.value = rows
    }
    
    // Search
    const handleSearch = () => {
      currentPage.value = 1
      loadData()
    }
    
    // 分页
    const handleSizeChange = (size) => {
      pageSize.value = size
      loadData()
    }
    
    const handleCurrentChange = (page) => {
      currentPage.value = page
      loadData()
    }
    
    // 显示Add对话框
    const showAddDialog = () => {
      dialogType.value = 'add'
      // Reset表单
      formData.irradiat_type = ''
      formData.irradiat_energy = ''
      formData.irradiat_temp = ''
      formData.irradiat_dose = ''
      formData.irradiat_fluence = ''
      formData.displac_damage = ''
      
      dialogVisible.value = true
    }
    
    // 显示Edit对话框
    const showEditDialog = async (row) => {
      dialogType.value = 'edit'
      currentId.value = row.irradiat_id
      
      try {
        const response = await getIrrConditionDetail(row.irradiat_id)
        if (response && response.data) {
          const data = response.data
          
          formData.irradiat_type = data.irradiat_type || ''
          formData.irradiat_energy = data.irradiat_energy !== undefined && data.irradiat_energy !== null ? data.irradiat_energy : ''
          formData.irradiat_temp = data.irradiat_temp !== undefined && data.irradiat_temp !== null ? data.irradiat_temp : ''
          formData.irradiat_dose = data.irradiat_dose !== undefined && data.irradiat_dose !== null ? data.irradiat_dose : ''
          formData.irradiat_fluence = data.irradiat_fluence !== undefined && data.irradiat_fluence !== null ? data.irradiat_fluence : ''
          formData.displac_damage = data.displac_damage !== undefined && data.displac_damage !== null ? data.displac_damage : ''
        }
      } catch (error) {
        console.error('Failed to load details:')
        ElMessage.error('Failed to load details. Please try again later.')
      }
      
      dialogVisible.value = true
    }
    
    // 提交表单
    const submitForm = () => {
      if (!formRef.value) return
      
      formRef.value.validate(async (valid) => {
        if (valid) {
          try {
            // 准备数据 - 确保数值字段正确转换
            const preparedData = {
              irradiat_type: formData.irradiat_type,
              // 处理数值字段：空字符串转为null，其他转为数值
              irradiat_energy: formData.irradiat_energy === '' ? null : parseFloat(formData.irradiat_energy),
              irradiat_temp: formData.irradiat_temp === '' ? null : parseFloat(formData.irradiat_temp),
              irradiat_dose: formData.irradiat_dose === '' ? null : parseFloat(formData.irradiat_dose),
              irradiat_fluence: formData.irradiat_fluence === '' ? null : formData.irradiat_fluence,
              displac_damage: formData.displac_damage === '' ? null : parseFloat(formData.displac_damage)
            }
            
            if (dialogType.value === 'add') {
              await createIrrCondition(preparedData)
              ElMessage.success('Added successfully')
            } else {
              await updateIrrCondition(currentId.value, preparedData)
              ElMessage.success('Updated successfully')
            }
            
            dialogVisible.value = false
            loadData()
          } catch (error) {
            console.error('Operation failed:')
            
            // 显示错误信息
            ElMessage.error(`${dialogType.value === 'add' ? 'Add' : 'Update'} failed. Please check the submitted values and try again.`)
          }
        }
      })
    }
    
    // Delete
    const handleDelete = (id) => {
      ElMessageBox.confirm('Are you sure you want to delete this record?', 'Confirm', {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }).then(async () => {
        try {
          await deleteIrrCondition(id)
          ElMessage.success('Deleted successfully')
          loadData()
        } catch (error) {
          console.error('Delete failed:')
          ElMessage.error('Delete failed. Please try again.')
        }
      }).catch(() => {
        // CancelDelete
      })
    }
    
    // 批量Delete
    const batchDelete = () => {
      if (selectedRows.value.length === 0) {
        ElMessage.warning('Select at least one record to delete')
        return
      }
      
      const ids = selectedRows.value.map(row => row.irradiat_id)
      
      ElMessageBox.confirm(`Are you sure you want to delete the ${ids.length} selected record(s)?`, 'Confirm', {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }).then(async () => {
        try {
          await batchDeleteIrrConditions(ids)
          ElMessage.success('Selected records deleted successfully')
          loadData()
        } catch (error) {
          console.error('Batch delete failed:')
          ElMessage.error('Batch delete failed. Please try again.')
        }
      }).catch(() => {
        // CancelDelete
      })
    }
    
    // Export Data
    const exportData = async () => {
      try {
        const ids = selectedRows.value.length > 0 
          ? selectedRows.value.map(row => row.irradiat_id) 
          : []
        
        // 弹出选择Export Format的对话框
        ElMessageBox.confirm(
          'Select an export format:<br/><br/>' +
          '<div style="text-align:center">' +
          '<button style="margin:0 10px" id="exportExcel">Excel</button>' +
          '<button style="margin:0 10px" id="exportCSV">CSV</button>' +
          '</div>',
          'Export Data',
          {
            confirmButtonText: 'Cancel',
            cancelButtonText: 'Close',
            dangerouslyUseHTMLString: true,
            showCancelButton: false,
            closeOnClickModal: false,
            closeOnPressEscape: false,
            showConfirmButton: true,
            center: true,
            customClass: 'export-dialog'
          }
        ).then(() => {
          // User点击Cancel按钮
        }).catch(() => {
          // User点击关闭按钮
        })
        
        // AddExcel和CSV按钮的点击事件
        setTimeout(() => {
          const excelBtn = document.getElementById('exportExcel')
          const csvBtn = document.getElementById('exportCSV')
          
          if (excelBtn) {
            excelBtn.addEventListener('click', () => {
              exportFormat('excel', ids)
              document.querySelector('.export-dialog .el-message-box__close').click()
            })
          }
          
          if (csvBtn) {
            csvBtn.addEventListener('click', () => {
              exportFormat('csv', ids)
              document.querySelector('.export-dialog .el-message-box__close').click()
            })
          }
        }, 100)
      } catch (error) {
        console.error('Export failed:')
        ElMessage.error('Export failed. Please try again later.')
      }
    }
    
    // 按格式导出
    const exportFormat = async (format, ids) => {
      try {
        ElMessage.info('Exporting data. Please wait...')
        
        const response = await exportIrrConditions({
          format,
          property_ids: ids
        })
        
        // 创建下载链接
        const blob = new Blob([response.data], {
          type: format === 'excel' 
            ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
            : 'text/csv'
        })
        
        const link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        link.download = `irrcondition_data_${new Date().toISOString().split('T')[0]}.${format === 'excel' ? 'xlsx' : 'csv'}`
        link.click()
        
        // 成功Confirm
        ElMessage.success('Export successful')
      } catch (error) {
        console.error('Export failed:')
        ElMessage.error('Export failed. Please try again later.')
      }
    }
    
    // 显示Import dialog
    const showImportDialog = () => {
      uploadFileList.value = []
      uploadFile.value = null
      importDialogVisible.value = true
    }
    
    // 文件变更
    const handleFileChange = (file) => {
      uploadFile.value = file.raw
      uploadFileList.value = [file]
    }
    
    // 下载导入模板
    const downloadTemplate = () => {
      // 创建表头
      const headers = ['Irradiation ID', 'Irradiation Type', 'Particle Energy', 'Irradiation Temperature', 'Irradiation Dose', 'Irradiation Time', 'Irradiation Fluence', 'Displacement Damage']
      let csvContent = headers.join(',') + '\n'
      
      // 创建一个示例行
      const exampleRow = [
        '1', 'Ion', '2.5', '500', '1.8', '24', '5.4e14', '50'
      ]
      csvContent += exampleRow.join(',')
      
      // 创建下载链接
      const blob = new Blob([csvContent], { type: 'text/csv' })
      const link = document.createElement('a')
      link.href = window.URL.createObjectURL(blob)
      link.download = 'irrcondition_import_template.csv'
      link.click()
    }
    
    // 提交导入
    const submitImport = async () => {
      if (!uploadFile.value) {
        ElMessage.warning('Select a file to import')
        return
      }
      
      // 检查文件Type
      const fileType = uploadFile.value.type
      const validTypes = [
        'application/vnd.ms-excel', 
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/csv',
        'application/csv',
        'text/plain'
      ]
      
      if (!validTypes.includes(fileType) && !uploadFile.value.name.endsWith('.csv') && !uploadFile.value.name.endsWith('.xlsx')) {
        ElMessage.error('Unsupported file format. Upload an Excel or CSV file.')
        return
      }
      
      try {
        ElMessage.info('Importing data. Please wait...')
        
        const formData = new FormData()
        formData.append('file', uploadFile.value)
        
        const response = await importIrrConditions(formData)
        const responseData = response.data
        
        // 处理响应
        if (responseData.success_count > 0) {
          const errorCount = responseData.errors ? responseData.errors.length : 0
          
          if (errorCount > 0) {
            ElMessage({
              message: `Import partially completed: ${responseData.success_count} record(s) succeeded and ${errorCount} failed`,
              type: 'warning',
              duration: 5000
            })
            
            // 显示错误详情
            if (responseData.errors && responseData.errors.length > 0) {
              const errorDetails = responseData.errors.map((err, index) => `Import issue ${index + 1}`).join('\n')
              console.error('Import error details:')
              ElMessageBox.alert(errorDetails, 'Error Details', {
                confirmButtonText: 'Confirm',
                type: 'warning'
              })
            }
          } else {
            const autoIncrementCount = responseData.auto_increment_count || 0
            let successMessage = `Import successful: ${responseData.success_count} record(s)`
            if (autoIncrementCount > 0) {
              successMessage += `; ${autoIncrementCount} record(s) received an automatically generated ID`
            }
            
            ElMessage({
              message: successMessage,
              type: 'success'
            })
          }
          
          // 刷新数据
          loadData()
          // 关闭对话框
          importDialogVisible.value = false
        } else {
          ElMessage.warning('Import completed, but no records were imported')
        }
      } catch (error) {
        console.error('Import failed:')
        ElMessage.error('Import failed. Please check the file and try again.')
      }
    }
    
    // 初始化
    onMounted(() => {
      loadData()
    })
    
    return {
      tableData,
      loading,
      selectedRows,
      searchQuery,
      irradiatIdFilter,
      irradiatTypeFilter,
      currentPage,
      pageSize,
      totalItems,
      dialogVisible,
      dialogType,
      formRef,
      formData,
      rules,
      importDialogVisible,
      uploadFileList,
      
      loadData,
      handleSelectionChange,
      handleSearch,
      handleSizeChange,
      handleCurrentChange,
      showAddDialog,
      showEditDialog,
      submitForm,
      handleDelete,
      batchDelete,
      exportData,
      showImportDialog,
      handleFileChange,
      downloadTemplate,
      submitImport
    }
  }
}
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.toolbar-container {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
}

.search-container {
  width: 60%;
}

.button-container {
  display: flex;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.upload-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.el-upload__tip {
  margin-top: 10px;
  line-height: 1.5;
}
</style> 
