<template>
  <div class="page-container">
    <!-- Search区域 -->
    <div class="toolbar-container">
      <div class="search-container">
        <el-row :gutter="10" style="margin-bottom: 10px;">
          <el-col :span="8">
            <el-input
              v-model="searchQuery"
              placeholder="Search by embrittlement ID"
              clearable
              @keyup.enter="handleSearch"
              @clear="handleSearch"
            >
              <template #append>
                <el-button icon="el-icon-search" @click="handleSearch"></el-button>
              </template>
            </el-input>
          </el-col>
          <el-col :span="5">
            <el-input
              v-model="materialIdFilter"
              placeholder="Filter by material ID"
              clearable
              @keyup.enter="handleSearch"
              @clear="handleSearch"
            ></el-input>
          </el-col>
          <el-col :span="5">
            <el-input
              v-model="processIdFilter"
              placeholder="Filter by process ID"
              clearable
              @keyup.enter="handleSearch"
              @clear="handleSearch"
            ></el-input>
          </el-col>
          <el-col :span="5">
            <el-input
              v-model="irradiatIdFilter"
              placeholder="Filter by irradiation ID"
              clearable
              @keyup.enter="handleSearch"
              @clear="handleSearch"
            ></el-input>
          </el-col>
        </el-row>
        
        <!-- 新增范围Search行 -->
        <el-row :gutter="10">
          <el-col :span="11">
            <div class="range-filter">
              <span class="range-label">DBTT Range:</span>
              <el-input
                v-model="dbttMinFilter"
                placeholder="Min"
                type="number"
                clearable
                @keyup.enter="handleSearch"
                @clear="handleSearch"
                class="range-input"
              ></el-input>
              <span class="range-separator">-</span>
              <el-input
                v-model="dbttMaxFilter"
                placeholder="Max"
                type="number"
                clearable
                @keyup.enter="handleSearch"
                @clear="handleSearch"
                class="range-input"
              ></el-input>
            </div>
          </el-col>
          <el-col :span="11">
            <div class="range-filter">
              <span class="range-label">DBTT Change Range:</span>
              <el-input
                v-model="dbttDiffMinFilter"
                placeholder="Min"
                type="number"
                clearable
                @keyup.enter="handleSearch"
                @clear="handleSearch"
                class="range-input"
              ></el-input>
              <span class="range-separator">-</span>
              <el-input
                v-model="dbttDiffMaxFilter"
                placeholder="Max"
                type="number"
                clearable
                @keyup.enter="handleSearch"
                @clear="handleSearch"
                class="range-input"
              ></el-input>
            </div>
          </el-col>
          <el-col :span="2">
            <el-button type="primary" @click="handleSearch">Search</el-button>
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
      <el-table-column prop="embrittlement_id" label="Embrittlement ID" width="120" />
      <el-table-column label="Material" width="120">
        <template #default="scope">
          <div>ID: {{ scope.row.material?.material_id }}</div>
          <div>{{ scope.row.material?.material_name }}</div>
        </template>
      </el-table-column>
      <el-table-column label="Process" width="120">
        <template #default="scope">
          <div>ID: {{ scope.row.process?.process_id }}</div>
          <div>{{ scope.row.process?.fabrication }}</div>
        </template>
      </el-table-column>
      <el-table-column label="Irradiation Condition" width="120">
        <template #default="scope">
          <div>ID: {{ scope.row.irradiat?.irradiat_id }}</div>
          <div>{{ scope.row.irradiat?.irradiat_type }}</div>
        </template>
      </el-table-column>
      <el-table-column label="DBTT" width="140">
        <template #default="scope">
          {{ scope.row.dbtt }}
        </template>
      </el-table-column>
      <el-table-column label="DBTT Change" width="140">
        <template #default="scope">
          {{ scope.row.dbtt_difference }}
        </template>
      </el-table-column>
      <el-table-column prop="entry_time" label="Entry Time" width="180" />
      <el-table-column prop="modify_time" label="Updated At" width="180" />
      <el-table-column label="Actions" width="150" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="showEditDialog(scope.row)">Edit</el-button>
          <el-button
            size="small"
            type="danger"
            @click="handleDelete(scope.row.embrittlement_id)"
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
      :title="dialogType === 'add' ? 'Add Irradiation Embrittlement Record' : 'Edit Irradiation Embrittlement Record'"
      v-model="dialogVisible"
      width="500px"
    >
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="120px">
        <el-form-item label="Material" prop="material_id">
          <el-select v-model="formData.material_id" filterable placeholder="Please select a material">
            <el-option
              v-for="item in materialOptions"
              :key="item.material_id"
              :label="`${item.material_id} - ${item.material_name}`"
              :value="item.material_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Process" prop="process_id">
          <el-select v-model="formData.process_id" filterable placeholder="Please select a process">
            <el-option
              v-for="item in processOptions"
              :key="item.process_id"
              :label="`${item.process_id} - ${item.fabrication}`"
              :value="item.process_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Irradiation Condition" prop="irradiat_id">
          <el-select v-model="formData.irradiat_id" filterable placeholder="Please select irradiation condition">
            <el-option
              v-for="item in irradiatOptions"
              :key="item.irradiat_id"
              :label="`${item.irradiat_id} - ${item.irradiat_type || 'No type specified'}`"
              :value="item.irradiat_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="DBTT" prop="dbtt">
          <el-input v-model.number="formData.dbtt" placeholder="Enter the ductile-to-brittle transition temperature" />
        </el-form-item>
        <el-form-item label="DBTT Change" prop="dbtt_difference">
          <el-input v-model.number="formData.dbtt_difference" placeholder="Enter the change in DBTT" />
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
    <el-dialog title="Import Irradiation Embrittlement Data" v-model="importDialogVisible" width="500px">
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
            <p>The file may contain these columns: Material ID, Process ID, Irradiation ID, DBTT, and DBTT Change.</p>
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
  getEmbrittlementList, 
  getEmbrittlementDetail, 
  createEmbrittlement, 
  updateEmbrittlement, 
  deleteEmbrittlement, 
  batchDeleteEmbrittlements,
  exportEmbrittlements,
  importEmbrittlements,
  getMaterialList,
  getProcessList,
  getIrrConditionList,
  rangeQueryEmbrittlements
} from '@/api/embrittlement'
import * as XLSX from 'xlsx'

export default {
  name: 'EmbrittlementList',
  
  setup() {
    // 表格数据
    const tableData = ref([])
    const loading = ref(false)
    const selectedRows = ref([])
    
    // Search和分页
    const searchQuery = ref('')
    const materialIdFilter = ref('')
    const processIdFilter = ref('')
    const irradiatIdFilter = ref('')
    const dbttMinFilter = ref('')
    const dbttMaxFilter = ref('')
    const dbttDiffMinFilter = ref('')
    const dbttDiffMaxFilter = ref('')
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalItems = ref(0)
    
    // 对话框
    const dialogVisible = ref(false)
    const dialogType = ref('add') // 'add' 或 'edit'
    const currentId = ref(null)
    const formRef = ref(null)
    
    // 选项数据
    const materialOptions = ref([])
    const processOptions = ref([])
    const irradiatOptions = ref([])
    
    // 表单数据
    const formData = reactive({
      material_id: '',
      process_id: '',
      irradiat_id: '',
      dbtt: '',
      dbtt_difference: ''
    })
    
    // 验证规则
    const rules = {
      material_id: [
        { required: true, message: 'Please select a material', trigger: 'change' }
      ],
      process_id: [
        { required: true, message: 'Please select a process', trigger: 'change' }
      ],
      irradiat_id: [
        { required: true, message: 'Please select irradiation condition', trigger: 'change' }
      ],
      dbtt: [
        { required: false, trigger: 'blur' },
        { type: 'number', message: 'DBTT must be a number', trigger: 'blur' }
      ],
      dbtt_difference: [
        { required: false, trigger: 'blur' },
        { type: 'number', message: 'DBTT change must be a number', trigger: 'blur' }
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
        // 检查是否使用范围查询
        const useRangeQuery = dbttMinFilter.value || dbttMaxFilter.value || 
                             dbttDiffMinFilter.value || dbttDiffMaxFilter.value
        
        if (useRangeQuery) {
          // 使用范围查询API
          const data = {
            material_id: materialIdFilter.value || undefined,
            process_id: processIdFilter.value || undefined,
            irradiat_id: irradiatIdFilter.value || undefined,
            dbtt_min: dbttMinFilter.value || undefined,
            dbtt_max: dbttMaxFilter.value || undefined,
            dbtt_difference_min: dbttDiffMinFilter.value || undefined,
            dbtt_difference_max: dbttDiffMaxFilter.value || undefined
          }
          const response = await rangeQueryEmbrittlements(data)
          tableData.value = response.data.results
          totalItems.value = response.data.count
        } else {
          // 使用标准列表API
          const params = {
            page: currentPage.value,
            page_size: pageSize.value,
            search: searchQuery.value,
            material_id: materialIdFilter.value || undefined,
            process_id: processIdFilter.value || undefined,
            irradiat_id: irradiatIdFilter.value || undefined
          }
          const response = await getEmbrittlementList(params)
          tableData.value = response.data.results
          totalItems.value = response.data.count
        }
      } catch (error) {
        console.error('Failed to load data:')
        ElMessage.error('Failed to load data. Please try again later.')
      } finally {
        loading.value = false
      }
    }
    
    // 加载选项数据
    const loadOptions = async () => {
      try {
        // 加载材料选项
        const materialResponse = await getMaterialList()
        materialOptions.value = materialResponse.data.results || materialResponse.data || []
        
        // 加载工艺选项
        const processResponse = await getProcessList()
        processOptions.value = processResponse.data.results || processResponse.data || []
        
        // 加载辐照条件选项
        const irradiatResponse = await getIrrConditionList()
        irradiatOptions.value = irradiatResponse.data.results || irradiatResponse.data || []
      } catch (error) {
        console.error('Failed to load options:')
        ElMessage.warning('Failed to load some options. Some lists may be unavailable.')
      }
    }
    
    // Search
    const handleSearch = () => {
      currentPage.value = 1
      loadData()
    }
    
    // 选择变更
    const handleSelectionChange = (rows) => {
      selectedRows.value = rows
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
      formData.material_id = ''
      formData.process_id = ''
      formData.irradiat_id = ''
      formData.dbtt = ''
      formData.dbtt_difference = ''
      
      dialogVisible.value = true
    }
    
    // 显示Edit对话框
    const showEditDialog = async (row) => {
      dialogType.value = 'edit'
      currentId.value = row.embrittlement_id
      
      try {
        const response = await getEmbrittlementDetail(row.embrittlement_id)
        if (response && response.data) {
          const data = response.data
          
          formData.material_id = data.material?.material_id || data.material_id
          formData.process_id = data.process?.process_id || data.process_id
          formData.irradiat_id = data.irradiat?.irradiat_id || data.irradiat_id
          formData.dbtt = data.dbtt
          formData.dbtt_difference = data.dbtt_difference
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
              material_id: Number(formData.material_id),
              process_id: Number(formData.process_id),
              irradiat_id: Number(formData.irradiat_id),
              dbtt: formData.dbtt === '' ? null : Number(formData.dbtt),
              dbtt_difference: formData.dbtt_difference === '' ? null : Number(formData.dbtt_difference)
            }
            
            if (dialogType.value === 'add') {
              await createEmbrittlement(preparedData)
              ElMessage.success('Added successfully')
            } else {
              await updateEmbrittlement(currentId.value, preparedData)
              ElMessage.success('Updated successfully')
            }
            
            dialogVisible.value = false
            loadData()
          } catch (error) {
            console.error('Operation failed:')
            ElMessage.error(`${dialogType.value === 'add' ? 'Add' : 'Update'} failed. Please try again.`)
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
          await deleteEmbrittlement(id)
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
      
      const ids = selectedRows.value.map(row => row.embrittlement_id)
      
      ElMessageBox.confirm(`Are you sure you want to delete the ${ids.length} selected record(s)?`, 'Confirm', {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }).then(async () => {
        try {
          await batchDeleteEmbrittlements(ids)
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
          ? selectedRows.value.map(row => row.embrittlement_id) 
          : []
        
        const response = await exportEmbrittlements({
          format: 'excel',
          property_ids: ids
        })
        
        // 创建下载链接
        const blob = new Blob([response.data], {
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        
        const link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        link.download = `embrittlement_data_${new Date().toISOString().split('T')[0]}.xlsx`
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
      const headers = ['material_id', 'process_id', 'irradiat_id', 'dbtt', 'dbtt_difference']
      let csvContent = headers.join(',') + '\n'
      
      // 创建一个示例行
      const exampleRow = [
        '1', '1', '1', '150.5', '45.2'
      ]
      csvContent += exampleRow.join(',')
      
      // 创建下载链接
      const blob = new Blob([csvContent], { type: 'text/csv' })
      const link = document.createElement('a')
      link.href = window.URL.createObjectURL(blob)
      link.download = 'embrittlement_import_template.csv'
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
        
        const response = await importEmbrittlements(formData)
        
        if (response.data.success_count > 0) {
          const successMessage = `Import successful: ${response.data.success_count} record(s)`
          ElMessage.success(successMessage)
          
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
      loadOptions()
    })
    
    return {
      tableData,
      loading,
      selectedRows,
      searchQuery,
      materialIdFilter,
      processIdFilter,
      irradiatIdFilter,
      dbttMinFilter,
      dbttMaxFilter,
      dbttDiffMinFilter,
      dbttDiffMaxFilter,
      currentPage,
      pageSize,
      totalItems,
      dialogVisible,
      dialogType,
      formRef,
      formData,
      rules,
      materialOptions,
      processOptions,
      irradiatOptions,
      importDialogVisible,
      uploadFileList,
      uploadFile,
      
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
  flex-direction: column;
}

.search-container {
  width: 100%;
  margin-bottom: 10px;
}

.button-container {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 10px;
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

.range-filter {
  display: flex;
  align-items: center;
}

.range-label {
  margin-right: 10px;
  white-space: nowrap;
}

.range-input {
  width: 100px;
}

.range-separator {
  margin: 0 5px;
}
</style> 
