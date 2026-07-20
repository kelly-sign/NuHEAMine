<template>
  <div class="page-container">
    <!-- Search区域 -->
    <div class="toolbar-container">
      <div class="search-container">
        <el-row :gutter="10">
          <el-col :span="8">
            <el-input
              v-model="searchQuery"
              placeholder="Search by microstructure ID"
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
        
        <!-- 范围查询控件 -->
        <el-row :gutter="10" style="margin-top: 10px;">
          <el-col :span="6">
            <div class="range-filter">
              <div class="filter-title">Helium Bubble Diameter (nm)</div>
              <div class="filter-inputs">
                <el-input-number 
                  v-model="heBubbleDiamMin" 
                  :min="0" 
                  :precision="2" 
                  size="small" 
                  placeholder="Min"
                  @change="handleSearch"
                  controls-position="right"
                  style="width: 120px"
                ></el-input-number>
                <span class="range-separator">-</span>
                <el-input-number 
                  v-model="heBubbleDiamMax" 
                  :min="0" 
                  :precision="2" 
                  size="small" 
                  placeholder="Max"
                  @change="handleSearch"
                  controls-position="right"
                  style="width: 120px"
                ></el-input-number>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="range-filter">
              <div class="filter-title">Helium Bubble Density (1×10²²/m³)</div>
              <div class="filter-inputs">
                <el-input-number 
                  v-model="heBubbleDensMin" 
                  :min="0" 
                  :precision="2" 
                  size="small" 
                  placeholder="Min"
                  @change="handleSearch"
                  controls-position="right"
                  style="width: 120px"
                ></el-input-number>
                <span class="range-separator">-</span>
                <el-input-number 
                  v-model="heBubbleDensMax" 
                  :min="0" 
                  :precision="2" 
                  size="small" 
                  placeholder="Max"
                  @change="handleSearch"
                  controls-position="right"
                  style="width: 120px"
                ></el-input-number>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="range-filter">
              <div class="filter-title">Swelling Rate (%)</div>
              <div class="filter-inputs">
                <el-input-number 
                  v-model="swellingRateMin" 
                  :min="0" 
                  :precision="2" 
                  size="small" 
                  placeholder="Min"
                  @change="handleSearch"
                  controls-position="right"
                  style="width: 120px"
                ></el-input-number>
                <span class="range-separator">-</span>
                <el-input-number 
                  v-model="swellingRateMax" 
                  :min="0" 
                  :precision="2" 
                  size="small" 
                  placeholder="Max"
                  @change="handleSearch"
                  controls-position="right"
                  style="width: 120px"
                ></el-input-number>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="range-filter">
              <div class="filter-title">Irradiation Hardening (MPa)</div>
              <div class="filter-inputs">
                <el-input-number 
                  v-model="irradiatHardMin" 
                  :min="0" 
                  :precision="2" 
                  size="small" 
                  placeholder="Min"
                  @change="handleSearch"
                  controls-position="right"
                  style="width: 120px"
                ></el-input-number>
                <span class="range-separator">-</span>
                <el-input-number 
                  v-model="irradiatHardMax" 
                  :min="0" 
                  :precision="2" 
                  size="small" 
                  placeholder="Max"
                  @change="handleSearch"
                  controls-position="right"
                  style="width: 120px"
                ></el-input-number>
              </div>
            </div>
          </el-col>
        </el-row>
        
        <!-- 清除筛选按钮 -->
        <el-row style="margin-top: 10px;">
          <el-col :span="24" style="text-align: right;">
            <el-button type="text" size="small" @click="clearFilters">
              <i class="el-icon-delete"></i> Clear All Filters
            </el-button>
          </el-col>
        </el-row>
      </div>
      <!-- 工具按钮 -->
      <div class="button-container">
        <el-button type="primary" @click="showAddDialog">Add</el-button>
        <el-button type="danger" :disabled="!selectedRows.length" @click="batchDelete">Delete Selected</el-button>
        <el-button type="success" @click.prevent="showImportDialog">Import</el-button>
        <el-button type="info" @click="exportData">Export</el-button>
        <!-- <el-button @click="testImportDialog">测试对话框</el-button> -->
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
      <el-table-column prop="microstructure_id" label="Microstructure ID" width="100" />
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
      <el-table-column label="Helium Bubble Diameter (nm)" width="120">
        <template #default="scope">
          {{ scope.row.he_bubble_diam }}
        </template>
      </el-table-column>
      <el-table-column label="Helium Bubble Density (1×10²²/m³)" width="160">
        <template #default="scope">
          {{ scope.row.he_bubble_dens }}
        </template>
      </el-table-column>
      <el-table-column label="Swelling Rate (%)" width="100">
        <template #default="scope">
          {{ scope.row.swelling_rate }}
        </template>
      </el-table-column>
      <el-table-column label="Irradiation Hardening (MPa)" width="140">
        <template #default="scope">
          {{ scope.row.irradiat_hard }}
        </template>
      </el-table-column>
      <el-table-column prop="entry_time" label="Entry Time" width="180" />
      <el-table-column label="Actions" width="150" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="showEditDialog(scope.row)">Edit</el-button>
          <el-button
            size="small"
            type="danger"
            @click="handleDelete(scope.row.microstructure_id)"
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
      :title="dialogType === 'add' ? 'Add Microstructure Evolution Record' : 'Edit Microstructure Evolution Record'"
      v-model="dialogVisible"
      :close-on-click-modal="false"
      :destroy-on-close="true"
      width="500px"
    >
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
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
        <el-form-item label="Helium Bubble Diameter" prop="he_bubble_diam">
          <el-input v-model="formData.he_bubble_diam" placeholder="Enter the helium bubble diameter">
            <template #append>nm</template>
          </el-input>
        </el-form-item>
        <el-form-item label="Helium Bubble Density" prop="he_bubble_dens">
          <el-input v-model="formData.he_bubble_dens" placeholder="Enter the helium bubble density">
            <template #append>1*1e22/m³</template>
          </el-input>
        </el-form-item>
        <el-form-item label="Swelling Rate" prop="swelling_rate">
          <el-input v-model="formData.swelling_rate" placeholder="Enter the swelling rate">
            <template #append>%</template>
          </el-input>
        </el-form-item>
        <el-form-item label="Irradiation Hardening" prop="irradiat_hard">
          <el-input v-model="formData.irradiat_hard" placeholder="Enter the irradiation hardening value">
            <template #append>MPa</template>
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="submitForm">Confirm</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- Import dialog -->
    <el-dialog
      title="Import Microstructure Evolution Data"
      v-model="importDialogVisible"
      :close-on-click-modal="false"
      destroy-on-close
      @closed="cancelImport"
    >
      <div class="import-container">
        <!-- 上传区域 -->
        <div class="upload-section">
          <el-upload
            ref="uploadRef"
            action=""
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-exceed="handleExceed"
            :file-list="uploadFileList"
            :accept="'.xlsx,.xls,.csv'"
          >
            <template #trigger>
              <el-button type="primary">Select File</el-button>
            </template>
            <template #tip>
              <div class="el-upload__tip">
                Upload an xlsx, xls, or csv file no larger than 10 MB.
              </div>
            </template>
          </el-upload>
          <el-button 
            type="success" 
            @click="downloadTemplate" 
            :loading="templateLoading"
          >
            Download Import Template
          </el-button>
        </div>

        <!-- 数据预览 -->
        <div v-if="showPreview && previewData.length > 0" class="preview-section">
          <h4>Data Preview (First 5 Rows)</h4>
          <el-table :data="previewData" border style="width: 100%">
            <el-table-column prop="material_id" label="Material ID" />
            <el-table-column prop="process_id" label="Process ID" />
            <el-table-column prop="irradiat_id" label="Irradiation ID" />
            <el-table-column prop="he_bubble_diam" label="Helium Bubble Diameter" />
            <el-table-column prop="he_bubble_dens" label="Helium Bubble Density" />
            <el-table-column prop="swelling_rate" label="Swelling Rate" />
            <el-table-column prop="irradiat_hard" label="Irradiation Hardening" />
          </el-table>
        </div>

        <!-- 错误信息 -->
        <div v-if="importErrors && importErrors.length > 0" class="error-section">
          <h4>Import Errors ({{ importErrors.length }})</h4>
          <el-alert
            v-for="(error, index) in importErrors"
            :key="index"
            :title="`Row ${error.row || 'Unknown'}: ${error.error || 'The row could not be imported'}`"
            type="error"
            :closable="false"
            show-icon
          />
        </div>

        <!-- 进度显示 -->
        <div v-if="importLoading" class="progress-section">
          <h4>Import Progress</h4>
          <el-progress :percentage="importProgress" :status="importProgress === 100 ? 'success' : null" />
        </div>
      </div>

      <template #footer>
        <el-button @click="cancelImport">Cancel</el-button>
        <el-button
          type="primary"
          @click="submitImport"
          :disabled="!uploadFile || importLoading"
          :loading="importLoading"
        >
          {{ importLoading ? 'Importing...' : 'Start Import' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  getMicrostructureList, 
  getMicrostructureDetail, 
  createMicrostructure, 
  updateMicrostructure, 
  deleteMicrostructure, 
  batchDeleteMicrostructures,
  exportMicrostructures,
  importMicrostructures,
  getMaterialList,
  getProcessList,
  getIrrConditionList as getIrrConditions
} from '@/api/microstructure'
import * as XLSX from 'xlsx'

export default {
  name: 'MicrostructureList',
  
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
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalItems = ref(0)
    
    // 范围查询参数
    const heBubbleDiamMin = ref(null)
    const heBubbleDiamMax = ref(null)
    const heBubbleDensMin = ref(null)
    const heBubbleDensMax = ref(null)
    const swellingRateMin = ref(null)
    const swellingRateMax = ref(null)
    const irradiatHardMin = ref(null)
    const irradiatHardMax = ref(null)
    
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
      he_bubble_diam: '',
      he_bubble_dens: '',
      swelling_rate: '',
      irradiat_hard: ''
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
      he_bubble_diam: [
        { required: false, trigger: 'blur' },
        { 
          validator: (rule, value, callback) => {
            if (value === '' || value === null || value === undefined) {
              callback()
            } else if (isNaN(Number(value))) {
              callback(new Error('Helium bubble diameter must be a number; decimals are supported'))
            } else {
              callback()
            }
          }, 
          trigger: 'blur' 
        }
      ],
      he_bubble_dens: [
        { required: false, trigger: 'blur' },
        { 
          validator: (rule, value, callback) => {
            if (value === '' || value === null || value === undefined) {
              callback()
            } else if (isNaN(Number(value))) {
              callback(new Error('Helium bubble density must be a number; decimals are supported'))
            } else {
              callback()
            }
          }, 
          trigger: 'blur' 
        }
      ],
      swelling_rate: [
        { required: false, trigger: 'blur' },
        { 
          validator: (rule, value, callback) => {
            if (value === '' || value === null || value === undefined) {
              callback()
            } else if (isNaN(Number(value))) {
              callback(new Error('Swelling rate must be a number; decimals are supported'))
            } else {
              callback()
            }
          }, 
          trigger: 'blur' 
        }
      ],
      irradiat_hard: [
        { required: false, trigger: 'blur' },
        { 
          validator: (rule, value, callback) => {
            if (value === '' || value === null || value === undefined) {
              callback()
            } else if (isNaN(Number(value))) {
              callback(new Error('Irradiation hardening must be a number; decimals are supported'))
            } else {
              callback()
            }
          }, 
          trigger: 'blur' 
        }
      ]
    }
    
    // 导入相关
    const importDialogVisible = ref(false)
    const uploadRef = ref(null)
    const uploadFileList = ref([])
    const uploadFile = ref(null)
    const previewData = ref([])
    const importLoading = ref(false)
    const importProgress = ref(0)
    const importErrors = ref([])
    const showPreview = ref(false)
    const templateLoading = ref(false)
    let progressInterval = null
    
    // 加载数据
    const loadData = async () => {
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          page_size: pageSize.value,
          search: searchQuery.value,
          material_id: materialIdFilter.value || undefined,
          process_id: processIdFilter.value || undefined,
          irradiat_id: irradiatIdFilter.value || undefined,
          he_bubble_diam_min: heBubbleDiamMin.value || undefined,
          he_bubble_diam_max: heBubbleDiamMax.value || undefined,
          he_bubble_dens_min: heBubbleDensMin.value || undefined,
          he_bubble_dens_max: heBubbleDensMax.value || undefined,
          swelling_rate_min: swellingRateMin.value || undefined,
          swelling_rate_max: swellingRateMax.value || undefined,
          irradiat_hard_min: irradiatHardMin.value || undefined,
          irradiat_hard_max: irradiatHardMax.value || undefined
        }
        const response = await getMicrostructureList(params)
        tableData.value = response.data.results
        totalItems.value = response.data.count
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
        const irradiatResponse = await getIrrConditions()
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
    const handleSelectionChange = (val) => {
      selectedRows.value = val
    }
    
    // 分页大小变更
    const handleSizeChange = (val) => {
      pageSize.value = val
      loadData()
    }
    
    // 页码变更
    const handleCurrentChange = (val) => {
      currentPage.value = val
      loadData()
    }
    
    // 显示Add对话框
    const showAddDialog = () => {
      dialogType.value = 'add'
      resetForm()
      dialogVisible.value = true
    }
    
    // 显示Edit对话框
    const showEditDialog = async (row) => {
      dialogType.value = 'edit'
      currentId.value = row.microstructure_id
      resetForm()
      
      try {
        const response = await getMicrostructureDetail(row.microstructure_id)
        const data = response.data
        
        // 确保所有字段都被正确设置，包括关联ID
        nextTick(() => {
          formData.material_id = data.material?.material_id || data.material_id
          formData.process_id = data.process?.process_id || data.process_id
          formData.irradiat_id = data.irradiat?.irradiat_id || data.irradiat_id
          formData.he_bubble_diam = data.he_bubble_diam
          formData.he_bubble_dens = data.he_bubble_dens
          formData.swelling_rate = data.swelling_rate
          formData.irradiat_hard = data.irradiat_hard
        })
        
        dialogVisible.value = true
      } catch (error) {
        console.error('Failed to load details:')
        ElMessage.error('Failed to load details. Please try again later.')
      }
    }
    
    // Reset表单
    const resetForm = () => {
      if (formRef.value) {
        formRef.value.resetFields()
      }
      
      Object.keys(formData).forEach(key => {
        formData[key] = ''
      })
    }
    
    // 提交表单
    const submitForm = async () => {
      if (!formRef.value) return
      
      await formRef.value.validate(async (valid) => {
        if (!valid) return

        try {
          // 转换数字字段
          const submitData = {
            ...formData,
            material_id: Number(formData.material_id) || undefined,
            process_id: Number(formData.process_id) || undefined,
            irradiat_id: Number(formData.irradiat_id) || undefined,
            he_bubble_diam: formData.he_bubble_diam === '' ? null : Number(formData.he_bubble_diam),
            he_bubble_dens: formData.he_bubble_dens === '' ? null : Number(formData.he_bubble_dens),
            swelling_rate: formData.swelling_rate === '' ? null : Number(formData.swelling_rate),
            irradiat_hard: formData.irradiat_hard === '' ? null : Number(formData.irradiat_hard)
          }
          
          if (dialogType.value === 'add') {
            await createMicrostructure(submitData)
            ElMessage.success('Added successfully')
          } else {
            await updateMicrostructure(currentId.value, submitData)
            ElMessage.success('Updated successfully')
          }
          dialogVisible.value = false
          loadData()
        } catch (error) {
          console.error('Save failed:')
          ElMessage.error('Save failed. Please check the submitted values and try again.')
        }
      })
    }
    
    // Delete记录
    const handleDelete = (id) => {
      ElMessageBox.confirm('Are you sure you want to delete this microstructure evolution record?', 'Confirm', {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }).then(async () => {
        try {
          await deleteMicrostructure(id)
          ElMessage.success('Deleted successfully')
          loadData()
        } catch (error) {
          console.error('Delete failed:')
          ElMessage.error('Delete failed. Please try again later.')
        }
      }).catch(() => {})
    }
    
    // 批量Delete
    const batchDelete = () => {
      if (!selectedRows.value.length) {
        ElMessage.warning('Select at least one record to delete')
        return
      }
      
      ElMessageBox.confirm(`Are you sure you want to delete the ${selectedRows.value.length} selected record(s)?`, 'Confirm', {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }).then(async () => {
        try {
          const ids = selectedRows.value.map(row => row.microstructure_id)
          await batchDeleteMicrostructures(ids)
          ElMessage.success('Selected records deleted successfully')
          loadData()
        } catch (error) {
          console.error('Batch delete failed:')
          ElMessage.error('Batch delete failed. Please try again later.')
        }
      }).catch(() => {})
    }
    
    // Export Data
    const exportData = async () => {
      try {
        const params = {
          format: 'excel',
          property_ids: selectedRows.value.length > 0 
            ? selectedRows.value.map(row => row.microstructure_id) 
            : []
        }
        
        const response = await exportMicrostructures(params)
        
        // 创建下载链接
        const blob = new Blob([response.data], {
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        const link = document.createElement('a')
        link.href = URL.createObjectURL(blob)
        link.download = `microstructure_evolution_data_${new Date().toISOString().slice(0, 10)}.xlsx`
        link.click()
        URL.revokeObjectURL(link.href)
        
        ElMessage.success('Export successful')
      } catch (error) {
        console.error('Export failed:')
        ElMessage.error('Export failed. Please try again later.')
      }
    }
    
    // 读取Excel文件内容
    const readExcelFile = (file) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          // 使用XLSX库读取文件内容
          const data = new Uint8Array(e.target.result);
          const workbook = XLSX.read(data, { type: 'array' });
          
          // 获取第一个工作表
          const firstSheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[firstSheetName];
          
          // 确保工作表存在
          if (!worksheet) {
            ElMessage.warning('No valid worksheet was found in the Excel file');
            showPreview.value = false;
            return;
          }
          
          // 先尝试保留原始数据Type
          const jsonData = XLSX.utils.sheet_to_json(worksheet, { 
            raw: true, // 允许自动检测数据Type
            defval: '', // 设置默认值为空字符串
            blankrows: false // 跳过空行
          });
          
          if (jsonData.length === 0) {
            ElMessage.warning('No data was found in the file');
            showPreview.value = false;
            return;
          }
          
          // 检查必要的列是否存在
          const requiredColumns = ['material_id', 'process_id', 'irradiat_id'];
          const missingColumns = requiredColumns.filter(col => 
            !Object.prototype.hasOwnProperty.call(jsonData[0], col)
          );
          
          if (missingColumns.length > 0) {
            ElMessage.error(`The file is missing required columns: ${missingColumns.join(', ')}`);
            showPreview.value = false;
            return;
          }
          
          
          // 标准化数据格式
          const processedData = jsonData.map(row => {
            const processedRow = { ...row };
            
            // 处理ID字段 - 确保是整数
            ['material_id', 'process_id', 'irradiat_id'].forEach(field => {
              if (processedRow[field] !== undefined && processedRow[field] !== '') {
                let idValue = processedRow[field];
                
                // 如果是字符串，尝试转换为数字
                if (typeof idValue === 'string') {
                  // 清理可能的空格
                  idValue = idValue.trim();
                  
                  // 尝试转换
                  const numValue = Number(idValue);
                  if (!isNaN(numValue)) {
                    idValue = numValue;
                  }
                }
                
                // 将所有数字ID转换为整数
                if (typeof idValue === 'number') {
                  processedRow[field] = Math.floor(idValue);
                } else {
                  // 保留非数字值，让验证步骤处理
                  processedRow[field] = idValue;
                }
              }
            });
            
            // 处理数值字段 - 确保是数字或null
            ['he_bubble_diam', 'he_bubble_dens', 'swelling_rate', 'irradiat_hard'].forEach(field => {
              if (processedRow[field] !== undefined && processedRow[field] !== '') {
                let numValue = processedRow[field];
                
                // 对于字符串Type，尝试将其转换为数字
                if (typeof numValue === 'string') {
                  numValue = numValue.trim();
                  const parsedNum = Number(numValue);
                  if (!isNaN(parsedNum)) {
                    numValue = parsedNum;
                  }
                }
                
                // 如果是数字，保留，否则设为null
                if (typeof numValue === 'number' && isFinite(numValue)) {
                  processedRow[field] = numValue;
                } else {
                  processedRow[field] = null;
                }
              } else {
                processedRow[field] = null;
              }
            });
            
            return processedRow;
          });
          
          // 显示预览数据（前5行）
          previewData.value = processedData.slice(0, 5);
          showPreview.value = true;
          
          // 验证数据格式
          validateImportData(processedData);
        } catch (error) {
          console.error('Failed to read the Excel file:');
          ElMessage.error('The file format is invalid and could not be read');
          showPreview.value = false;
          previewData.value = [];
        }
      };
      
      reader.onerror = () => {
        ElMessage.error('An error occurred while reading the file');
        showPreview.value = false;
        previewData.value = [];
      };
      
      reader.readAsArrayBuffer(file);
    };

    // 处理文件变更
    const handleFileChange = (file) => {
      if (file && file.raw) {
        // Reset状态
        uploadFile.value = file.raw;
        previewData.value = [];
        importErrors.value = [];
        showPreview.value = false;
        importProgress.value = 0;
        
        // 验证文件Type
        const validExtensions = ['.xlsx', '.xls', '.csv'];
        const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
        if (!validExtensions.includes(fileExtension)) {
          ElMessage.error('Only .xlsx, .xls, and .csv files are supported');
          uploadFileList.value = [];
          uploadFile.value = null;
          return;
        }
        
        // 验证文件大小
        if (file.size > 10 * 1024 * 1024) { // 10MB
          ElMessage.error('File size cannot exceed 10MB');
          uploadFileList.value = [];
          uploadFile.value = null;
          return;
        }
        
        // 读取并预览文件
        readExcelFile(file.raw);
      } else {
        uploadFile.value = null;
        showPreview.value = false;
        previewData.value = [];
      }
    };
    
    // 显示Import dialog
    const showImportDialog = () => {
      uploadFileList.value = [];
      uploadFile.value = null;
      previewData.value = [];
      importErrors.value = [];
      showPreview.value = false;
      importProgress.value = 0;
      importLoading.value = false;
      importDialogVisible.value = true;
    };

    // 验证Import Data
    const validateImportData = (data) => {
      importErrors.value = [];
      
      // 验证规则
      const requiredFields = ['material_id', 'process_id', 'irradiat_id'];
      const numericFields = ['he_bubble_diam', 'he_bubble_dens', 'swelling_rate', 'irradiat_hard'];
      
      // 仅验证前100行以避免性能问题
      const rowsToValidate = data.slice(0, 100);
      
      for (let i = 0; i < rowsToValidate.length; i++) {
        const row = rowsToValidate[i];
        const rowIndex = i + 2; // 表格行号从1开始，标题行占1行
        const rowErrors = [];
        
        // 检查必填字段
        for (const field of requiredFields) {
          if (row[field] === undefined || row[field] === null || row[field] === '') {
            rowErrors.push(`${field} is required`);
            continue;
          }
          
          // 检查是否为数字ID
          const idValue = row[field];
          if (typeof idValue !== 'number' || !Number.isInteger(idValue) || idValue <= 0) {
            rowErrors.push(`${field} must be a positive integer`);
          }
        }
        
        // 检查数值字段
        for (const field of numericFields) {
          if (row[field] !== undefined && row[field] !== null && row[field] !== '') {
            // 已经在处理阶段转换过，这里只检查负数
            if (row[field] < 0) {
              rowErrors.push(`${field} cannot be negative`);
            }
          }
        }
        
        // 如果该行有错误，Add到总错误列表
        if (rowErrors.length > 0) {
          importErrors.value.push({
            row: rowIndex,
            error: rowErrors.join('; ')
          });
        }
      }
      
      if (importErrors.value.length > 0) {
        ElMessage.warning(`Found ${importErrors.value.length} data format issue(s). Correct them and upload the file again.`);
      }
    };

    // 处理文件超出数量限制
    const handleExceed = () => {
      ElMessage.warning('Only one file can be uploaded');
    };

    // 提交导入
    const submitImport = () => {
      if (!uploadFile.value) {
        ElMessage.warning('Select a file first');
        return;
      }
      
      // 有验证错误时提醒User
      if (importErrors.value && importErrors.value.length > 0) {
        ElMessageBox.confirm(
          `${importErrors.value.length} data issue(s) were detected. Continue importing the valid records?`,
          'Confirm Import',
          {
            confirmButtonText: 'Continue Import',
            cancelButtonText: 'Cancel',
            type: 'warning'
          }
        ).then(() => {
          // User确认继续导入
          executeImport();
        }).catch(() => {
          // UserCancel导入
          ElMessage.info('Import canceled');
        });
      } else {
        // 没有验证错误，直接导入
        executeImport();
      }
    };

    // 执行导入Actions
    const executeImport = () => {
      if (!uploadFile.value) {
        ElMessage.warning('Select a file to import');
        return;
      }
      
      importLoading.value = true;
      importProgress.value = 0;
      
      const formData = new FormData();
      formData.append('file', uploadFile.value);
      
      // 模拟上传进度
      if (progressInterval) {
        clearInterval(progressInterval);
      }
      
      progressInterval = setInterval(() => {
        if (importProgress.value < 90) {
          importProgress.value += 10;
        }
      }, 300);
      
      // 发送导入请求
      importMicrostructures(formData)
        .then(response => {
          if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
          }
          importProgress.value = 100;
          
          // 处理Import Results
          const { success_count, error_count, errors } = response.data;
          
          if (success_count > 0) {
            ElMessage.success(`Imported ${success_count} record(s) successfully`);
            
            if (error_count > 0) {
              try {
                importErrors.value = Array.isArray(errors) ? errors.map(err => ({
                  row: err && typeof err === 'object' && Number.isInteger(Number(err.row))
                    ? Number(err.row)
                    : 'Unknown',
                  error: 'The server rejected this record.'
                })) : [];
              } catch (e) {
                console.error('Failed to process import errors:');
                importErrors.value = [{ row: 'Unknown', error: 'Import error details could not be processed.' }];
              }
              
              ElMessage.warning(`${error_count} record(s) could not be imported`);
            } else {
              // 全部成功，关闭对话框并刷新数据
              setTimeout(() => {
                importErrors.value = [];
                importDialogVisible.value = false;
                loadData(); // 刷新列表数据
              }, 1000);
            }
          } else {
            try {
              if (Array.isArray(errors) && errors.length > 0) {
                importErrors.value = errors.map(err => ({
                  row: err && typeof err === 'object' && Number.isInteger(Number(err.row))
                    ? Number(err.row)
                    : 'Unknown',
                  error: 'The server rejected this record.'
                }));
              } else {
                importErrors.value = [{ row: 'Unknown', error: 'No records could be imported.' }];
              }
            } catch (e) {
              console.error('Failed to process import errors:');
              importErrors.value = [{ row: 'Unknown', error: 'Import error details could not be processed.' }];
            }
            
            ElMessage.error('Import failed. Check the data format and try again.');
          }
        })
        .catch(error => {
          if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
          }
          importProgress.value = 0;
          console.error('Import failed:');
          
          // 处理错误响应
          try {
            if (error.response) {
              const errorData = error.response.data;
              
              // 尝试提取详细错误信息
              if (typeof errorData === 'string') {
                importErrors.value = [{ row: 'Unknown', error: 'The server rejected the import file.' }];
              } else if (errorData) {
                // 处理错误列表
                if (Array.isArray(errorData.errors) && errorData.errors.length > 0) {
                  importErrors.value = errorData.errors.map(err => ({
                    row: err && typeof err === 'object' && Number.isInteger(Number(err.row))
                      ? Number(err.row)
                      : 'Unknown',
                    error: 'The server rejected this record.'
                  }));
                } else {
                  importErrors.value = [{ row: 'Unknown', error: 'The server rejected the import file.' }];
                }
              } else {
                importErrors.value = [{ row: 'Unknown', error: 'The server rejected the import file.' }];
              }
            } else {
              importErrors.value = [{ row: 'Unknown', error: 'A network error interrupted the import.' }];
            }
          } catch (e) {
            console.error('Failed to process the import response:');
            importErrors.value = [{ row: 'Unknown', error: 'The import response could not be processed.' }];
          }
          
          ElMessage.error('Import failed. Check the file and try again.');
        })
        .finally(() => {
          setTimeout(() => {
            importLoading.value = false;
          }, 500);
        });
    };
    
    // 下载导入模板
    const downloadTemplate = () => {
      templateLoading.value = true;
      
      try {
        // 创建表头
        const headers = [
          'material_id', 'process_id', 'irradiat_id', 
          'he_bubble_diam', 'he_bubble_dens', 'swelling_rate', 'irradiat_hard'
        ];
        
        // 创建示例数据 - 确保示例数据使用的是数字Type，而非字符串
        const exampleData = [
          {
            material_id: 1,
            process_id: 1,
            irradiat_id: 1,
            he_bubble_diam: 10.5,
            he_bubble_dens: 2.3,
            swelling_rate: 1.2,
            irradiat_hard: 300
          },
          {
            material_id: 2,
            process_id: 2,
            irradiat_id: 2,
            he_bubble_diam: 12.1,
            he_bubble_dens: 3.2,
            swelling_rate: 2.1,
            irradiat_hard: 350
          }
        ];
        
        // 创建工作簿
        const wb = XLSX.utils.book_new();
        
        // 使用aoa_to_sheet以保留数值格式
        const ws_data = [
          headers,
          ...exampleData.map(row => [
            row.material_id,
            row.process_id,
            row.irradiat_id,
            row.he_bubble_diam,
            row.he_bubble_dens,
            row.swelling_rate,
            row.irradiat_hard
          ])
        ];
        const ws = XLSX.utils.aoa_to_sheet(ws_data);
        
        // 设置列宽
        const wscols = [
          { wch: 12 }, // material_id
          { wch: 12 }, // process_id
          { wch: 12 }, // irradiat_id
          { wch: 15 }, // he_bubble_diam
          { wch: 15 }, // he_bubble_dens
          { wch: 15 }, // swelling_rate
          { wch: 15 }  // irradiat_hard
        ];
        ws['!cols'] = wscols;
        
        // Add注释工作表
        const noteWs = XLSX.utils.aoa_to_sheet([
          ['Microstructure Evolution Data Import Instructions'],
          [''],
          ['1. Required fields: material_id, process_id, and irradiat_id (integers only).'],
          ['2. Numeric fields: he_bubble_diam (helium bubble diameter, nm), he_bubble_dens (helium bubble density, 1×10²²/m³), swelling_rate (%), and irradiat_hard (irradiation hardening, MPa).'],
          ['3. Numeric fields must be non-negative.'],
          ['4. material_id, process_id, and irradiat_id must already exist in the system.'],
          ['5. Do not modify the column headers.'],
          ['6. The sample data is for reference only; use IDs that exist in the system.'],
          ['7. Store ID fields as numbers, not text.'],
          ['8. If Excel displays an ID in scientific notation, change the cell format to Number or Text.']
        ]);
        
        // Add工作表到工作簿
        XLSX.utils.book_append_sheet(wb, ws, 'Data Template');
        XLSX.utils.book_append_sheet(wb, noteWs, 'Instructions');
        
        // 导出Excel文件
        XLSX.writeFile(wb, 'microstructure_evolution_import_template.xlsx');
        
        ElMessage.success('Template downloaded successfully');
      } catch (error) {
        console.error('Failed to download template:');
        ElMessage.error('Failed to download template');
      } finally {
        templateLoading.value = false;
      }
    };
    
    // Cancel导入
    const cancelImport = () => {
      if (progressInterval) {
        clearInterval(progressInterval)
        progressInterval = null
      }
      
      uploadFileList.value = []
      uploadFile.value = null
      previewData.value = []
      importErrors.value = []
      showPreview.value = false
      importProgress.value = 0
      importLoading.value = false
      importDialogVisible.value = false
    }
    
    // 测试函数 - 用于调试
    const testImportDialog = () => {
      const el = document.querySelector('.test-dialog')
      if (el) {
        el.style.display = 'block'
      }
    }
    
    // 清除筛选条件
    const clearFilters = () => {
      searchQuery.value = ''
      materialIdFilter.value = ''
      processIdFilter.value = ''
      irradiatIdFilter.value = ''
      heBubbleDiamMin.value = null
      heBubbleDiamMax.value = null
      heBubbleDensMin.value = null
      heBubbleDensMax.value = null
      swellingRateMin.value = null
      swellingRateMax.value = null
      irradiatHardMin.value = null
      irradiatHardMax.value = null
      currentPage.value = 1
      loadData()
    }
    
    // 组件挂载时加载数据
    onMounted(() => {
      loadData()
      loadOptions()
    })
    
    return {
      // 表格相关
      tableData,
      loading,
      selectedRows,
      
      // Search和分页
      searchQuery,
      materialIdFilter,
      processIdFilter,
      irradiatIdFilter,
      currentPage,
      pageSize,
      totalItems,
      handleSearch,
      handleSelectionChange,
      handleSizeChange,
      handleCurrentChange,
      
      // 范围查询参数
      heBubbleDiamMin,
      heBubbleDiamMax,
      heBubbleDensMin,
      heBubbleDensMax,
      swellingRateMin,
      swellingRateMax,
      irradiatHardMin,
      irradiatHardMax,
      clearFilters,
      
      // 对话框相关
      dialogVisible,
      dialogType,
      formRef,
      formData,
      rules,
      
      // 选项数据
      materialOptions,
      processOptions,
      irradiatOptions,
      
      // Actions
      showAddDialog,
      showEditDialog,
      submitForm,
      handleDelete,
      batchDelete,
      
      // 导入相关
      importDialogVisible,
      uploadFileList,
      uploadFile,
      previewData,
      importLoading,
      importProgress,
      importErrors,
      showPreview,
      templateLoading,
      showImportDialog,
      handleFileChange,
      handleExceed,
      readExcelFile,
      validateImportData,
      submitImport,
      exportData,
      downloadTemplate,
      testImportDialog,
      cancelImport
    }
  }
}
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.toolbar-container {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.search-container {
  flex: 1;
  margin-right: 20px;
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

/* 范围查询样式 */
.range-filter {
  border: 1px solid #EBEEF5;
  border-radius: 4px;
  padding: 8px;
  background-color: #F8F9FA;
}

.filter-title {
  font-size: 12px;
  color: #606266;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.filter-inputs {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.range-separator {
  margin: 0 5px;
  color: #909399;
  flex-shrink: 0;
}

.upload-container {
  width: 100%;
}

.el-upload__tip {
  line-height: 1.5;
  margin-top: 10px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.import-dialog-content {
  padding: 20px;
}

.preview-section {
  margin-top: 20px;
  margin-bottom: 20px;
}

.preview-section h4 {
  margin-bottom: 10px;
  color: #606266;
}

.error-section {
  margin-top: 20px;
  margin-bottom: 20px;
}

.error-section h4 {
  margin-bottom: 10px;
  color: #F56C6C;
}

.progress-section {
  margin-top: 20px;
  margin-bottom: 20px;
}

.progress-text {
  text-align: center;
  color: #606266;
  margin-top: 10px;
}

.el-upload__tip {
  line-height: 1.5;
  margin-top: 10px;
  color: #606266;
}

.el-upload__tip a {
  color: #409EFF;
  text-decoration: none;
}

.el-upload__tip a:hover {
  text-decoration: underline;
}
</style> 
