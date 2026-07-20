<template>
  <div class="property-list">
    <page-header 
      title="Room Temperature Structure Properties"
    >
      <template #actions>
        <el-button type="primary" @click="handleAdd">
          Add Property Data
        </el-button>
        <el-upload
          class="upload-demo"
          :action="uploadUrl"
          :headers="headers"
          :before-upload="handleBeforeUpload"
          :on-success="handleImportSuccess"
          :on-error="handleImportError"
          :show-file-list="false"
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
            <el-form-item label="Phase Structure">
              <el-input v-model="searchForm.phase_structure" placeholder="Phase structure"></el-input>
            </el-form-item>
            
            <!-- Range search form -->
            <el-collapse v-model="activeCollapse" class="range-search-collapse">
              <el-collapse-item title="Mechanical Property Range Search" name="1">
                <div class="range-search-content">
                  <el-row :gutter="24">
                    <el-col :span="8">
                      <el-form-item label="Hardness (HV)" class="range-form-item">
                        <div class="range-input-group">
                          <el-input-number 
                            v-model="searchForm.hardness_min" 
                            :precision="1" 
                            :step="0.1" 
                            :min="0"
                            :controls="false"
                            placeholder="Min"
                            class="range-input">
                          </el-input-number>
                          <span class="range-separator">-</span>
                          <el-input-number 
                            v-model="searchForm.hardness_max" 
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
                      <el-form-item label="Compressive Yield Strength (MPa)" class="range-form-item">
                        <div class="range-input-group">
                          <el-input-number 
                            v-model="searchForm.yield_strength_c_min" 
                            :precision="1" 
                            :step="0.1" 
                            :min="0"
                            :controls="false"
                            placeholder="Min"
                            class="range-input">
                          </el-input-number>
                          <span class="range-separator">-</span>
                          <el-input-number 
                            v-model="searchForm.yield_strength_c_max" 
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
                      <el-form-item label="Tensile Yield Strength (MPa)" class="range-form-item">
                        <div class="range-input-group">
                          <el-input-number 
                            v-model="searchForm.yield_strength_t_min" 
                            :precision="1" 
                            :step="0.1" 
                            :min="0"
                            :controls="false"
                            placeholder="Min"
                            class="range-input">
                          </el-input-number>
                          <span class="range-separator">-</span>
                          <el-input-number 
                            v-model="searchForm.yield_strength_t_max" 
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
                      <el-form-item label="Ultimate Compressive Strength (MPa)" class="range-form-item">
                        <div class="range-input-group">
                          <el-input-number 
                            v-model="searchForm.ultimate_strength_c_min" 
                            :precision="1" 
                            :step="0.1" 
                            :min="0"
                            :controls="false"
                            placeholder="Min"
                            class="range-input">
                          </el-input-number>
                          <span class="range-separator">-</span>
                          <el-input-number 
                            v-model="searchForm.ultimate_strength_c_max" 
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
                      <el-form-item label="Ultimate Tensile Strength (MPa)" class="range-form-item">
                        <div class="range-input-group">
                          <el-input-number 
                            v-model="searchForm.ultimate_strength_t_min" 
                            :precision="1" 
                            :step="0.1" 
                            :min="0"
                            :controls="false"
                            placeholder="Min"
                            class="range-input">
                          </el-input-number>
                          <span class="range-separator">-</span>
                          <el-input-number 
                            v-model="searchForm.ultimate_strength_t_max" 
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
                      <el-form-item label="Compressive Fracture Strain (%)" class="range-form-item">
                        <div class="range-input-group">
                          <el-input-number 
                            v-model="searchForm.fracture_strain_c_min" 
                            :precision="1" 
                            :step="0.1" 
                            :min="0"
                            :controls="false"
                            placeholder="Min"
                            class="range-input">
                          </el-input-number>
                          <span class="range-separator">-</span>
                          <el-input-number 
                            v-model="searchForm.fracture_strain_c_max" 
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
                      <el-form-item label="Tensile Fracture Strain (%)" class="range-form-item">
                        <div class="range-input-group">
                          <el-input-number 
                            v-model="searchForm.fracture_strain_t_min" 
                            :precision="1" 
                            :step="0.1" 
                            :min="0"
                            :controls="false"
                            placeholder="Min"
                            class="range-input">
                          </el-input-number>
                          <span class="range-separator">-</span>
                          <el-input-number 
                            v-model="searchForm.fracture_strain_t_max" 
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
        <el-table-column type="selection" width="55" />
        <el-table-column prop="rtproperty_id" label="ID" width="80"></el-table-column>
        <el-table-column label="Material Info" width="180">
          <template #default="scope">
            <div>ID: {{ scope.row.material?.material_id || scope.row.material_id }}</div>
            <div class="small-text">{{ scope.row.material?.material_name || '-' }}</div>
          </template>
        </el-table-column>
        <el-table-column label="Process Info" width="180">
          <template #default="scope">
            <div>ID: {{ scope.row.process?.process_id || scope.row.process_id }}</div>
            <div class="small-text">{{ scope.row.process?.fabrication || '-' }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="phase_structure" label="Phase Structure" width="150"></el-table-column>
        <el-table-column prop="hardness_value" label="Hardness" width="100"></el-table-column>
        <el-table-column prop="yield_strength_c" label="Compressive Yield Strength" width="120"></el-table-column>
        <el-table-column prop="yield_strength_t" label="Tensile Yield Strength" width="120"></el-table-column>
        <el-table-column prop="ultimate_strength_c" label="Ultimate Compressive Strength" width="120"></el-table-column>
        <el-table-column prop="ultimate_strength_t" label="Ultimate Tensile Strength" width="120"></el-table-column>
        <el-table-column prop="fracture_strain_c" label="Compressive Fracture Strain" width="120"></el-table-column>
        <el-table-column prop="fracture_strain_t" label="Tensile Fracture Strain" width="120"></el-table-column>
        <el-table-column prop="entry_time" label="Entry Time" width="180">
          <template #default="scope">
            {{ scope.row.entry_time ? new Date(scope.row.entry_time).toLocaleString() : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="modify_time" label="Update Time" width="180">
          <template #default="scope">
            {{ scope.row.modify_time ? new Date(scope.row.modify_time).toLocaleString() : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="scope">
            <el-button
              size="small"
              @click="handleEdit(scope.row)"
            >
              Edit
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(scope.row)"
            >
              Delete
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? 'Add Property Data' : 'Edit Property Data'"
      width="50%"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="Material ID" prop="material_id">
          <el-input v-model="form.material_id" placeholder="Please enter material ID"></el-input>
        </el-form-item>
        <el-form-item label="Process ID" prop="process_id">
          <el-input v-model="form.process_id" placeholder="Please enter process ID"></el-input>
        </el-form-item>
        <el-form-item label="Phase Structure" prop="phase_structure">
          <el-input v-model="form.phase_structure" placeholder="Please enter phase structure"></el-input>
        </el-form-item>
        <el-form-item label="Hardness" prop="hardness_value">
          <el-input v-model="form.hardness_value" placeholder="Please enter hardness"></el-input>
        </el-form-item>
        <el-form-item label="Compressive Yield Strength" prop="yield_strength_c">
          <el-input v-model="form.yield_strength_c" placeholder="Please enter compressive yield strength"></el-input>
        </el-form-item>
        <el-form-item label="Tensile Yield Strength" prop="yield_strength_t">
          <el-input v-model="form.yield_strength_t" placeholder="Please enter tensile yield strength"></el-input>
        </el-form-item>
        <el-form-item label="Ultimate Compressive Strength" prop="ultimate_strength_c">
          <el-input v-model="form.ultimate_strength_c" placeholder="Please enter ultimate compressive strength"></el-input>
        </el-form-item>
        <el-form-item label="Ultimate Tensile Strength" prop="ultimate_strength_t">
          <el-input v-model="form.ultimate_strength_t" placeholder="Please enter ultimate tensile strength"></el-input>
        </el-form-item>
        <el-form-item label="Compressive Fracture Strain" prop="fracture_strain_c">
          <el-input v-model="form.fracture_strain_c" placeholder="Please enter compressive fracture strain"></el-input>
        </el-form-item>
        <el-form-item label="Tensile Fracture Strain" prop="fracture_strain_t">
          <el-input v-model="form.fracture_strain_t" placeholder="Please enter tensile fracture strain"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="handleSubmit">Confirm</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Import Results对话框 -->
    <el-dialog
      v-model="importResultVisible"
      title="Import Results"
      width="50%"
      :close-on-click-modal="false"
    >
      <div v-if="importResult">
        <el-alert
          :title="importResult.success ? 'Import successful' : 'Import completed with errors'"
          :type="importResult.success ? 'success' : 'error'"
          :closable="false"
          show-icon
        />
        <div v-if="importResult.errors && importResult.errors.length > 0" class="error-list">
          <h4>Error Details:</h4>
          <el-alert
            v-for="(error, index) in importResult.errors"
            :key="index + String(error)"
            title="Import validation failed for this row."
            type="warning"
            :closable="false"
            show-icon
            class="error-item"
          />
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importResultVisible = false">Close</el-button>
          <el-button v-if="importResult && importResult.success" type="primary" @click="handleImportComplete">
            Confirm
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRoomTempProperties, createRoomTempProperty, updateRoomTempProperty, deleteRoomTempProperty, exportRoomTempProperties } from '@/api/property'
import PageHeader from '@/components/common/PageHeader.vue'
import { getToken } from '@/utils/auth'
import axios from 'axios'

const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const dialogType = ref('add')
const formRef = ref(null)
const importing = ref(false)
const importResultVisible = ref(false)
const importResult = ref(null)

// Add折叠面板的激活状态
const activeCollapse = ref(['1'])

// 修改Search form，Add范围查询字段
const searchForm = ref({
  material_id: '',
  process_id: '',
  phase_structure: '',
  // Add范围查询字段
  hardness_min: null,
  hardness_max: null,
  yield_strength_c_min: null,
  yield_strength_c_max: null,
  yield_strength_t_min: null,
  yield_strength_t_max: null,
  ultimate_strength_c_min: null,
  ultimate_strength_c_max: null,
  ultimate_strength_t_min: null,
  ultimate_strength_t_max: null,
  fracture_strain_c_min: null,
  fracture_strain_c_max: null,
  fracture_strain_t_min: null,
  fracture_strain_t_max: null
})

const form = ref({
  material_id: '',
  process_id: '',
  phase_structure: '',
  hardness_value: null,
  yield_strength_c: null,
  yield_strength_t: null,
  ultimate_strength_c: null,
  ultimate_strength_t: null,
  fracture_strain_c: null,
  fracture_strain_t: null
})

const rules = {
  material_id: [{ required: true, message: 'Please enter material ID', trigger: 'blur' }],
  process_id: [{ required: true, message: 'Please enter process ID', trigger: 'blur' }]
}

const apiBaseUrl = (process.env.VUE_APP_API_URL || '/api').replace(/\/$/, '')
const uploadUrl = `${apiBaseUrl}/room-temp-properties/import_data/`
const headers = {
  Authorization: `Bearer ${getToken()}`
}

const selectedRows = ref([])
const hasSelection = computed(() => selectedRows.value.length > 0)

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

const downloadFile = (data, filename) => {
  const blob = new Blob([data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
  const link = document.createElement('a')
  link.href = window.URL.createObjectURL(blob)
  link.download = filename
  link.click()
  window.URL.revokeObjectURL(link.href)
}

const handleExportCommand = async (command) => {
  try {
    let exportData = []
    let response

    switch (command) {
      case 'current':
        exportData = tableData.value
        break
      case 'selected':
        exportData = selectedRows.value
        break
      case 'all':
        response = await getRoomTempProperties({ page: 1, page_size: 999999 })
        exportData = response.data.results || response.data
        break
    }

    if (exportData.length === 0) {
      ElMessage.warning('No data available to export')
      return
    }

    const propertyIds = exportData.map(item => item.rtproperty_id)
    
    response = await axios({
      url: `${apiBaseUrl}/room-temp-properties/export_data/`,
      method: 'POST',
      data: { property_ids: propertyIds },
      responseType: 'blob',
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    })

    const now = new Date()
    const timestamp = now.toISOString().replace(/[^0-9]/g, '').slice(0, 14)
    const filename = `room_temp_properties_${timestamp}.xlsx`

    downloadFile(response.data, filename)
    ElMessage.success('Export successful')
  } catch (error) {
    console.error('Export error:')
    ElMessage.error('Export failed. Please try again.')
  }
}

const handleExport = () => {
  handleExportCommand('current')
}

const fetchData = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      material_id: searchForm.value.material_id || undefined,
      process_id: searchForm.value.process_id || undefined,
      // Add范围查询参数
      hardness_min: searchForm.value.hardness_min,
      hardness_max: searchForm.value.hardness_max,
      yield_strength_c_min: searchForm.value.yield_strength_c_min,
      yield_strength_c_max: searchForm.value.yield_strength_c_max,
      yield_strength_t_min: searchForm.value.yield_strength_t_min,
      yield_strength_t_max: searchForm.value.yield_strength_t_max,
      ultimate_strength_c_min: searchForm.value.ultimate_strength_c_min,
      ultimate_strength_c_max: searchForm.value.ultimate_strength_c_max,
      ultimate_strength_t_min: searchForm.value.ultimate_strength_t_min,
      ultimate_strength_t_max: searchForm.value.ultimate_strength_t_max,
      fracture_strain_c_min: searchForm.value.fracture_strain_c_min,
      fracture_strain_c_max: searchForm.value.fracture_strain_c_max,
      fracture_strain_t_min: searchForm.value.fracture_strain_t_min,
      fracture_strain_t_max: searchForm.value.fracture_strain_t_max
    }

    // 只有当相结构不为空时才Add到Search参数中
    if (searchForm.value.phase_structure && searchForm.value.phase_structure.trim()) {
      params.phase_structure = searchForm.value.phase_structure.trim()
    }
    
    // 移除未定义的参数
    Object.keys(params).forEach(key => {
      if (params[key] === undefined || params[key] === '' || params[key] === null) {
        delete params[key]
      }
    })
    
    const response = await getRoomTempProperties(params)
    
    // 处理响应数据
    if (response.data) {
      tableData.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
      total.value = response.data.count || response.data.length || 0
    } else {
      tableData.value = Array.isArray(response) ? response : (response.results || [])
      total.value = response.count || response.length || 0
    }
    
  } catch (error) {
    console.error('Error fetching data:')
    console.error('Error details:')
    ElMessage.error('Failed to load room-temperature property data')
    tableData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

const resetSearch = () => {
  Object.keys(searchForm.value).forEach(key => {
    searchForm.value[key] = key.includes('_min') || key.includes('_max') ? null : ''
  })
  handleSearch()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchData()
}

const handleAdd = () => {
  dialogType.value = 'add'
  form.value = {
    material_id: '',
    process_id: '',
    phase_structure: '',
    hardness_value: null,
    yield_strength_c: null,
    yield_strength_t: null,
    ultimate_strength_c: null,
    ultimate_strength_t: null,
    fracture_strain_c: null,
    fracture_strain_t: null
  }
  dialogVisible.value = true
}

const handleRowClick = (row) => {
}

const handleEdit = (row) => {
  dialogType.value = 'edit'
  form.value = {
    rtproperty_id: row.rtproperty_id,
    material_id: row.material?.material_id,
    process_id: row.process?.process_id,
    phase_structure: row.phase_structure,
    hardness_value: row.hardness_value,
    yield_strength_c: row.yield_strength_c,
    yield_strength_t: row.yield_strength_t,
    ultimate_strength_c: row.ultimate_strength_c,
    ultimate_strength_t: row.ultimate_strength_t,
    fracture_strain_c: row.fracture_strain_c,
    fracture_strain_t: row.fracture_strain_t
  }
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    'Are you sure you want to delete this property record?',
    'Warning',
    {
      confirmButtonText: 'Confirm',
      cancelButtonText: 'Cancel',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteRoomTempProperty(row.rtproperty_id)
      ElMessage.success('Deleted successfully')
      fetchData()
    } catch (error) {
      console.error('Delete failed:')
      ElMessage.error('Failed to delete the property record')
    }
  })
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const submitData = {
          material_id: parseInt(form.value.material_id),
          process_id: parseInt(form.value.process_id),
          phase_structure: form.value.phase_structure,
          hardness_value: form.value.hardness_value,
          yield_strength_c: form.value.yield_strength_c,
          yield_strength_t: form.value.yield_strength_t,
          ultimate_strength_c: form.value.ultimate_strength_c,
          ultimate_strength_t: form.value.ultimate_strength_t,
          fracture_strain_c: form.value.fracture_strain_c,
          fracture_strain_t: form.value.fracture_strain_t
        }

        if (form.value.rtproperty_id) {
          await updateRoomTempProperty(form.value.rtproperty_id, submitData)
          ElMessage.success('Updated successfully')
        } else {
          await createRoomTempProperty(submitData)
          ElMessage.success('Created successfully')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        console.error('Property operation failed:')
        ElMessage.error('Failed to save the property data')
      }
    }
  })
}

const handleBeforeUpload = (file) => {
  const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || 
                 file.type === 'application/vnd.ms-excel'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isExcel) {
    ElMessage.error('Only Excel files are allowed!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('File size cannot exceed 2MB!')
    return false
  }

  importing.value = true
  return true
}

const handleImportSuccess = (response) => {
  importing.value = false
  importResult.value = response
  importResultVisible.value = true
  
  if (response.success) {
    ElMessage.success('Import successful')
    if (response.success_count > 0) {
      fetchData() // 刷新数据
    }
  } else {
    ElMessage.warning('Import completed with errors')
  }

  if (response.errors && response.errors.length > 0) {
    console.error('Import errors:')
    importResult.value = {
      success: false,
      message: response.message,
      errors: response.errors
    }
  }
}

const handleImportError = (error) => {
  console.error('Import error:')
  importing.value = false
  
  const errorMessage = 'Import failed. Please check the file and try again.'
                      
  ElMessage.error({
    message: errorMessage,
    duration: 5000,
    showClose: true
  })

  importResult.value = {
    success: false,
    message: errorMessage,
    errors: error.response?.data?.errors || []
  }
  importResultVisible.value = true
}

const handleImportComplete = () => {
  importResultVisible.value = false
  importResult.value = null
  fetchData()
}

onMounted(() => {
  fetchData()
})
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

.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.upload-demo {
  display: inline-block;
  margin: 0 10px;
}

.error-list {
  margin-top: 20px;
  max-height: 300px;
  overflow-y: auto;
  
  .error-item {
    margin-bottom: 10px;
  }
}

.el-dropdown {
  margin-left: 10px;
}

.range-search-collapse {
  margin: 10px 0;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  width: 100%;
}

.range-search-content {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.range-form-item {
  margin-bottom: 18px;
}

.range-form-item :deep(.el-form-item__label) {
  line-height: 1.2;
  padding-right: 5px;
  white-space: normal;
  word-break: break-word;
  height: auto;
  font-size: 13px;
  font-weight: normal;
  color: #606266;
}

.range-input-group {
  display: flex;
  align-items: center;
  gap: 5px;
  flex-wrap: nowrap;
}

.range-input {
  width: 80px !important;
  flex-shrink: 0;
}

.range-input :deep(.el-input__wrapper) {
  padding: 0 8px;
}

.range-separator {
  color: #606266;
  font-weight: bold;
  flex-shrink: 0;
  padding: 0 2px;
}

.small-text {
  font-size: 12px;
  color: #606266;
  line-height: 1.2;
  margin-top: 3px;
}

:deep(.el-collapse-item__header) {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  padding: 0 15px;
}

:deep(.el-collapse-item__content) {
  padding-bottom: 15px;
}

:deep(.el-form--inline .el-form-item) {
  margin-right: 15px;
}

:deep(.el-collapse-item__wrap) {
  max-width: 100%;
  overflow: visible;
}

:deep(.el-row) {
  width: 100%;
}
</style> 
