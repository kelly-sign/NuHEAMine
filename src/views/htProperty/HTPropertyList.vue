<template>
  <div class="property-list">
    <page-header 
      title="High-Temperature Mechanical Properties"
    >
      <template #actions>
        <el-button type="primary" @click="handleAdd">
          Add Property Data
        </el-button>
        <el-upload
          class="upload-demo"
          action="#"
          :auto-upload="false"
          :show-file-list="false"
          :on-change="handleFileChange"
          :disabled="importing"
        >
          <el-button :loading="importing" type="primary">
            {{ importing ? 'Importing...' : 'Import Data' }}
          </el-button>
        </el-upload>
        <el-dropdown @command="handleExportCommand" split-button type="warning" @click="handleExport">
          Export Data
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="current">Export Current Page</el-dropdown-item>
              <el-dropdown-item command="all">Export All</el-dropdown-item>
              <el-dropdown-item command="selected" :disabled="!hasSelection">Export Selected</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
    </page-header>

    <el-card class="list-card">
      <template #header>
        <div class="card-header">
          <el-form :inline="true" :model="searchForm" class="search-form">
            <el-form-item label="Material">
              <el-input v-model="searchForm.material_id" placeholder="Material ID"></el-input>
            </el-form-item>
            <el-form-item label="Process">
              <el-input v-model="searchForm.process_id" placeholder="Process ID"></el-input>
            </el-form-item>
            <el-form-item label="Test Type">
              <el-input v-model="searchForm.test_type" placeholder="Test type"></el-input>
            </el-form-item>
            
            <!-- Add范围查询表单 -->
            <el-collapse v-model="activeCollapse" class="range-search-collapse">
              <el-collapse-item title="Mechanical Property Range Search" name="1">
                <div class="range-search-content">
                  <el-row :gutter="24">
                    <el-col :span="8">
                      <el-form-item label="Test Temperature (°C)" class="range-form-item">
                        <div class="range-input-group">
                          <el-input-number 
                            v-model="searchForm.htproperty_temp_min" 
                            :precision="1" 
                            :step="0.1" 
                            :min="0"
                            :controls="false"
                            placeholder="Min"
                            class="range-input">
                          </el-input-number>
                          <span class="range-separator">-</span>
                          <el-input-number 
                            v-model="searchForm.htproperty_temp_max" 
                            :precision="1" 
                            :step="0.1" 
                            :min="0"
                            :controls="false"
                            placeholder="Max"
                            class="range-input">
                          </el-input-number>
                        </div>
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="Yield Strength (MPa)" class="range-form-item">
                        <div class="range-input-group">
                          <el-input-number 
                            v-model="searchForm.yield_strength_min" 
                            :precision="1" 
                            :step="0.1" 
                            :min="0"
                            :controls="false"
                            placeholder="Min"
                            class="range-input">
                          </el-input-number>
                          <span class="range-separator">-</span>
                          <el-input-number 
                            v-model="searchForm.yield_strength_max" 
                            :precision="1" 
                            :step="0.1" 
                            :min="0"
                            :controls="false"
                            placeholder="Max"
                            class="range-input">
                          </el-input-number>
                        </div>
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="Ultimate Strength (MPa)" class="range-form-item">
                        <div class="range-input-group">
                          <el-input-number 
                            v-model="searchForm.ultimate_strength_min" 
                            :precision="1" 
                            :step="0.1" 
                            :min="0"
                            :controls="false"
                            placeholder="Min"
                            class="range-input">
                          </el-input-number>
                          <span class="range-separator">-</span>
                          <el-input-number 
                            v-model="searchForm.ultimate_strength_max" 
                            :precision="1" 
                            :step="0.1" 
                            :min="0"
                            :controls="false"
                            placeholder="Max"
                            class="range-input">
                          </el-input-number>
                        </div>
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="Fracture Strain (%)" class="range-form-item">
                        <div class="range-input-group">
                          <el-input-number 
                            v-model="searchForm.fracture_strain_min" 
                            :precision="1" 
                            :step="0.1" 
                            :min="0"
                            :controls="false"
                            placeholder="Min"
                            class="range-input">
                          </el-input-number>
                          <span class="range-separator">-</span>
                          <el-input-number 
                            v-model="searchForm.fracture_strain_max" 
                            :precision="1" 
                            :step="0.1" 
                            :min="0"
                            :controls="false"
                            placeholder="Max"
                            class="range-input">
                          </el-input-number>
                        </div>
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>
              </el-collapse-item>
            </el-collapse>

            <el-form-item>
              <el-button type="primary" @click="handleSearch">Search</el-button>
              <el-button @click="resetSearch">Reset</el-button>
            </el-form-item>
          </el-form>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="tableData"
        border
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column prop="htproperty_id" label="Property ID" width="80"></el-table-column>
        <el-table-column label="Material Info" width="180">
          <template #default="scope">
            <div>ID: {{ scope.row.material.material_id }}</div>
            <div class="small-text">{{ scope.row.material.material_name }}</div>
          </template>
        </el-table-column>
        <el-table-column label="Process Info" width="180">
          <template #default="scope">
            <div>ID: {{ scope.row.process.process_id }}</div>
            <div class="small-text">{{ scope.row.process.fabrication }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="test_type" label="Test Type" width="120">
          <template #default="scope">
            {{ formatTestType(scope.row.test_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="htproperty_temp" label="Test Temperature (°C)" width="120"></el-table-column>
        <el-table-column prop="yield_strength" label="Yield Strength (MPa)" width="140"></el-table-column>
        <el-table-column prop="ultimate_strength" label="Ultimate Strength (MPa)" width="140"></el-table-column>
        <el-table-column prop="fracture_strain" label="Fracture Strain (%)" width="140"></el-table-column>
        <el-table-column prop="entry_time" label="Entry Time" width="160">
          <template #default="scope">
            {{ scope.row.entry_time ? new Date(scope.row.entry_time).toLocaleString() : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="modify_time" label="Update Time" width="160">
          <template #default="scope">
            {{ scope.row.modify_time ? new Date(scope.row.modify_time).toLocaleString() : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="180">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">Edit</el-button>
            <el-popconfirm
              title="Are you sure you want to delete this record?"
              @confirm="handleDelete(scope.row)"
            >
              <template #reference>
                <el-button size="small" type="danger">Delete</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        ></el-pagination>
      </div>
    </el-card>

    <!-- Add/Edit dialog -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        label-width="120px"
        label-position="right"
      >
        <el-form-item label="Material ID" prop="material_id">
          <el-input v-model="form.material_id" placeholder="Please enter material ID"></el-input>
        </el-form-item>
        <el-form-item label="Process ID" prop="process_id">
          <el-input v-model="form.process_id" placeholder="Please enter process ID"></el-input>
        </el-form-item>
        <el-form-item label="Test Type" prop="test_type">
          <el-select v-model="form.test_type" placeholder="Please select a test type" style="width: 100%">
            <el-option label="Tensile" value="拉伸"></el-option>
            <el-option label="Creep" value="蠕变"></el-option>
            <el-option label="Impact" value="冲击"></el-option>
            <el-option label="Fatigue" value="疲劳"></el-option>
            <el-option label="Compression" value="压缩"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="Test Temperature (°C)" prop="htproperty_temp">
          <el-input-number 
            v-model="form.htproperty_temp" 
            :precision="1" 
            :step="0.1" 
            :min="0"
            style="width: 100%">
          </el-input-number>
        </el-form-item>
        <el-form-item label="Yield Strength (MPa)" prop="yield_strength">
          <el-input-number 
            v-model="form.yield_strength" 
            :precision="1" 
            :step="0.1" 
            :min="0"
            style="width: 100%">
          </el-input-number>
        </el-form-item>
        <el-form-item label="Ultimate Strength (MPa)" prop="ultimate_strength">
          <el-input-number 
            v-model="form.ultimate_strength" 
            :precision="1" 
            :step="0.1" 
            :min="0"
            style="width: 100%">
          </el-input-number>
        </el-form-item>
        <el-form-item label="Fracture Strain (%)" prop="fracture_strain">
          <el-input-number 
            v-model="form.fracture_strain" 
            :precision="1" 
            :step="0.1" 
            :min="0"
            style="width: 100%">
          </el-input-number>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">
            {{ submitting ? 'Submitting...' : 'Confirm' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Import Results对话框 -->
    <el-dialog
      title="Import Results"
      v-model="importResultVisible"
      width="600px"
    >
      <div v-if="importResult">
        <el-alert
          title="Import complete"
          :type="importResult.success ? 'success' : 'error'"
          :closable="false"
          show-icon
        ></el-alert>
        <div class="import-stats" v-if="importResult.success_count || importResult.error_count">
          <div>Total: {{ importResult.success_count + importResult.error_count }}</div>
          <div>Succeeded: {{ importResult.success_count }}</div>
          <div>Failed: {{ importResult.error_count }}</div>
        </div>
        <div class="import-errors" v-if="importResult.errors && importResult.errors.length > 0">
          <h4>Error Details:</h4>
          <el-scrollbar height="200px">
            <ul>
              <li v-for="(error, index) in importResult.errors" :key="index" class="error-item">
                Import validation failed for this row.
              </li>
            </ul>
          </el-scrollbar>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importResultVisible = false">Close</el-button>
          <el-button type="primary" @click="handleRefreshAfterImport" v-if="importResult && importResult.success_count > 0">
            Refresh Data
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { getHTProperties, createHTProperty, updateHTProperty, deleteHTProperty, importHTProperties, exportHTProperties } from '@/api/htProperty'
import PageHeader from '@/components/common/PageHeader.vue'
import { getToken } from '@/utils/auth'

export default {
  name: 'HTPropertyList',
  components: {
    PageHeader
  },
  setup() {
    const router = useRouter()

    // 表格数据
    const loading = ref(false)
    const tableData = ref([])
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const multipleSelection = ref([])
    const hasSelection = computed(() => multipleSelection.value.length > 0)

    // Search form
    const activeCollapse = ref(['1'])
    const searchForm = reactive({
      material_id: '',
      process_id: '',
      test_type: '',
      htproperty_temp_min: null,
      htproperty_temp_max: null,
      yield_strength_min: null,
      yield_strength_max: null,
      ultimate_strength_min: null,
      ultimate_strength_max: null,
      fracture_strain_min: null,
      fracture_strain_max: null
    })

    const testTypeLabels = {
      '拉伸': 'Tensile',
      '蠕变': 'Creep',
      '冲击': 'Impact',
      '疲劳': 'Fatigue',
      '压缩': 'Compression'
    }

    const formatTestType = (value) => testTypeLabels[value] || value || '-'

    // 对话框表单
    const dialogTitle = ref('Add High-Temperature Property Data')
    const dialogVisible = ref(false)
    const submitting = ref(false)
    const formRef = ref(null)
    const form = reactive({
      material_id: '',
      process_id: '',
      test_type: '',
      htproperty_temp: null,
      yield_strength: null,
      ultimate_strength: null,
      fracture_strain: null
    })
    const rules = {
      material_id: [
        { required: true, message: 'Please enter material ID', trigger: 'blur' }
      ],
      process_id: [
        { required: true, message: 'Please enter process ID', trigger: 'blur' }
      ],
      test_type: [
        { required: true, message: 'Please select a test type', trigger: 'change' }
      ],
      htproperty_temp: [
        { required: true, message: 'Please enter the test temperature', trigger: 'blur' }
      ]
    }

    // 导入导出
    const importing = ref(false)
    const importResultVisible = ref(false)
    const importResult = ref(null)
    const apiBaseUrl = (process.env.VUE_APP_API_URL || '/api').replace(/\/$/, '')
    const uploadUrl = `${apiBaseUrl}/ht-properties/import_data/`
    const headers = {
      Authorization: `Bearer ${getToken()}`
    }

    // 初始化获取数据
    const fetchData = async () => {
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          page_size: pageSize.value,
          ...searchForm
        }
        const response = await getHTProperties(params)
        
        // 处理响应数据
        if (response.data) {
          tableData.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
          total.value = response.data.count || response.data.length || 0
        } else {
          tableData.value = Array.isArray(response) ? response : (response.results || [])
          total.value = response.count || response.length || 0
        }
      } catch (error) {
        console.error('Failed to load data:')
        ElMessage.error('Failed to load high-temperature property data')
      } finally {
        loading.value = false
      }
    }

    // Search
    const handleSearch = () => {
      currentPage.value = 1
      fetchData()
    }

    // ResetSearch
    const resetSearch = () => {
      Object.keys(searchForm).forEach(key => {
        searchForm[key] = key === 'material_id' || key === 'process_id' || key === 'test_type' ? '' : null
      })
      currentPage.value = 1
      fetchData()
    }

    // Add
    const handleAdd = () => {
      dialogTitle.value = 'Add High-Temperature Property Data'
      Object.keys(form).forEach(key => {
        form[key] = key === 'material_id' || key === 'process_id' || key === 'test_type' ? '' : null
      })
      dialogVisible.value = true
      editingId.value = null
    }

    // Edit
    const editingId = ref(null)
    const handleEdit = (row) => {
      dialogTitle.value = 'Edit High-Temperature Property Data'
      Object.keys(form).forEach(key => {
        form[key] = row[key]
      })
      // 处理外键关系
      form.material_id = row.material.material_id
      form.process_id = row.process.process_id
      
      editingId.value = row.htproperty_id
      dialogVisible.value = true
    }

    // 提交表单
    const submitForm = async () => {
      if (!formRef.value) return

      await formRef.value.validate(async (valid, fields) => {
        if (!valid) {
          return
        }
        
        submitting.value = true
        try {
          if (editingId.value) {
            // 更新
            await updateHTProperty(editingId.value, form)
            ElMessage.success('Updated successfully')
          } else {
            // 创建
            await createHTProperty(form)
            ElMessage.success('Added successfully')
          }
          dialogVisible.value = false
          fetchData()
        } catch (error) {
          ElMessage.error('Failed to save the property data')
        } finally {
          submitting.value = false
        }
      })
    }

    // Delete
    const handleDelete = async (row) => {
      try {
        await deleteHTProperty(row.htproperty_id)
        ElMessage.success('Deleted successfully')
        if (tableData.value.length === 1 && currentPage.value > 1) {
          currentPage.value--
        }
        fetchData()
      } catch (error) {
        ElMessage.error('Failed to delete the property data')
      }
    }

    // 表格选择
    const handleSelectionChange = (selection) => {
      multipleSelection.value = selection
    }

    // 分页
    const handleSizeChange = (size) => {
      pageSize.value = size
      fetchData()
    }

    const handleCurrentChange = (page) => {
      currentPage.value = page
      fetchData()
    }

    // Import Data
    const handleFileChange = (file) => {
      if (!file) return
      
      importing.value = true
      handleImport(file.raw)
    }

    const handleImport = async (file) => {
      const isExcel = file.type === 'application/vnd.ms-excel' || 
                     file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      const isLt10M = file.size / 1024 / 1024 < 10

      if (!isExcel) {
        ElMessage.error('Only Excel files are allowed!')
        importing.value = false
        return
      }

      if (!isLt10M) {
        ElMessage.error('File size cannot exceed 10MB!')
        importing.value = false
        return
      }

      try {
        const formData = new FormData()
        formData.append('file', file)
        const response = await importHTProperties(formData)
        importResult.value = response.data || response
        importResultVisible.value = true
      } catch (error) {
        console.error('Import error:')
        ElMessage.error('Import failed. Please check the file and try again.')
      } finally {
        importing.value = false
      }
    }

    const handleRefreshAfterImport = () => {
      importResultVisible.value = false
      fetchData()
    }

    // Export Data
    const handleExport = () => {
      handleExportCommand('current')
    }

    const handleExportCommand = async (command) => {
      let ids = []
      if (command === 'selected') {
        if (multipleSelection.value.length === 0) {
          ElMessage.warning('Please select at least one record')
          return
        }
        ids = multipleSelection.value.map(item => item.htproperty_id)
      }

      try {
        const response = await exportHTProperties({
          property_ids: command === 'all' ? [] : (command === 'selected' ? ids : tableData.value.map(item => item.htproperty_id)),
          format: 'excel'
        })

        // 处理下载
        const blob = new Blob(
          [response.data], 
          { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }
        )
        const link = document.createElement('a')
        link.href = URL.createObjectURL(blob)
        link.download = `high_temperature_properties_${new Date().toISOString().slice(0, 10)}.xlsx`
        link.click()
        URL.revokeObjectURL(link.href)
        
        ElMessage.success('Export successful')
      } catch (error) {
        console.error('Export error:')
        ElMessage.error('Export failed. Please try again.')
      }
    }

    onMounted(() => {
      fetchData()
    })

    return {
      loading,
      tableData,
      total,
      currentPage,
      pageSize,
      searchForm,
      formatTestType,
      activeCollapse,
      dialogVisible,
      dialogTitle,
      form,
      rules,
      formRef,
      submitting,
      importResult,
      importResultVisible,
      importing,
      uploadUrl,
      headers,
      hasSelection,
      fetchData,
      handleSearch,
      resetSearch,
      handleAdd,
      handleEdit,
      handleDelete,
      submitForm,
      handleSelectionChange,
      handleSizeChange,
      handleCurrentChange,
      handleFileChange,
      handleRefreshAfterImport,
      handleExport,
      handleExportCommand
    }
  }
}
</script>

<style scoped>
.property-list {
  padding: 20px;
}

.list-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.range-search-collapse {
  width: 100%;
  margin-bottom: 15px;
}

.range-search-content {
  padding: 10px 0;
}

.range-form-item {
  width: 100%;
  margin-bottom: 10px;
}

.range-input-group {
  display: flex;
  align-items: center;
}

.range-input {
  width: 100px;
}

.range-separator {
  margin: 0 5px;
}

.small-text {
  font-size: 12px;
  color: #606266;
  line-height: 1.2;
  margin-top: 3px;
}

.pagination-container {
  padding: 15px 0;
  text-align: right;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}

.import-stats {
  margin-top: 15px;
  display: flex;
  justify-content: space-around;
}

.import-errors {
  margin-top: 15px;
}

.error-item {
  padding: 5px 0;
  color: #f56c6c;
}
</style> 
