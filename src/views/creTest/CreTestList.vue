<template>
  <div class="cretest-list">
    <page-header title="Creep Test Table">
      <template #actions>
        <el-button type="primary" @click="handleAdd">
          Add Creep Test Data
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
              <el-dropdown-item command="selected">Export Selected</el-dropdown-item>
              <el-dropdown-item command="all">Export All</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
    </page-header>

    <el-card class="list-card">
      <template #header>
        <div class="card-header">
          <span>Creep Test Data</span>
        </div>
      </template>

      <!-- Search form -->
      <el-form :inline="true" :model="searchForm" class="search-form" @submit.prevent>
        <el-form-item label="Material ID">
          <el-input v-model="searchForm.material_id" placeholder="Material ID" clearable @keyup.enter="handleSearch"></el-input>
        </el-form-item>
        <el-form-item label="Process ID">
          <el-input v-model="searchForm.process_id" placeholder="Process ID" clearable @keyup.enter="handleSearch"></el-input>
        </el-form-item>
        <el-form-item label="Test Temperature (℃)">
          <div class="range-input">
            <el-input v-model="searchForm.creep_temp_min" placeholder="Min" @keyup.enter="handleSearch" class="range-input-min"></el-input>
            <span class="range-separator">-</span>
            <el-input v-model="searchForm.creep_temp_max" placeholder="Max" @keyup.enter="handleSearch" class="range-input-max"></el-input>
          </div>
        </el-form-item>
        <el-form-item label="Test Duration (h)">
          <div class="range-input">
            <el-input v-model="searchForm.creep_time_min" placeholder="Min" @keyup.enter="handleSearch" class="range-input-min"></el-input>
            <span class="range-separator">-</span>
            <el-input v-model="searchForm.creep_time_max" placeholder="Max" @keyup.enter="handleSearch" class="range-input-max"></el-input>
          </div>
        </el-form-item>
        <el-form-item label="Initial Stress (MPa)">
          <div class="range-input">
            <el-input v-model="searchForm.initial_stress_min" placeholder="Min" @keyup.enter="handleSearch" class="range-input-min"></el-input>
            <span class="range-separator">-</span>
            <el-input v-model="searchForm.initial_stress_max" placeholder="Max" @keyup.enter="handleSearch" class="range-input-max"></el-input>
          </div>
        </el-form-item>
        <el-form-item label="Steady-State Creep Rate">
          <div class="range-input">
            <el-input v-model="searchForm.creep_rate_min" placeholder="Min" @keyup.enter="handleSearch" class="range-input-min"></el-input>
            <span class="range-separator">-</span>
            <el-input v-model="searchForm.creep_rate_max" placeholder="Max" @keyup.enter="handleSearch" class="range-input-max"></el-input>
          </div>
        </el-form-item>
        <el-form-item label="Creep Limit (MPa)">
          <div class="range-input">
            <el-input v-model="searchForm.creep_limit_min" placeholder="Min" @keyup.enter="handleSearch" class="range-input-min"></el-input>
            <span class="range-separator">-</span>
            <el-input v-model="searchForm.creep_limit_max" placeholder="Max" @keyup.enter="handleSearch" class="range-input-max"></el-input>
          </div>
        </el-form-item>
        <el-form-item label="Creep Rupture Strength (MPa)">
          <div class="range-input">
            <el-input v-model="searchForm.creep_rupture_strength_min" placeholder="Min" @keyup.enter="handleSearch" class="range-input-min"></el-input>
            <span class="range-separator">-</span>
            <el-input v-model="searchForm.creep_rupture_strength_max" placeholder="Max" @keyup.enter="handleSearch" class="range-input-max"></el-input>
          </div>
        </el-form-item>
        <el-form-item label="Rupture Time (h)">
          <div class="range-input">
            <el-input v-model="searchForm.rupture_time_min" placeholder="Min" @keyup.enter="handleSearch" class="range-input-min"></el-input>
            <span class="range-separator">-</span>
            <el-input v-model="searchForm.rupture_time_max" placeholder="Max" @keyup.enter="handleSearch" class="range-input-max"></el-input>
          </div>
        </el-form-item>
        <el-form-item label="Rupture Strength Limit (MPa)">
          <div class="range-input">
            <el-input v-model="searchForm.rupture_strength_limit_min" placeholder="Min" @keyup.enter="handleSearch" class="range-input-min"></el-input>
            <span class="range-separator">-</span>
            <el-input v-model="searchForm.rupture_strength_limit_max" placeholder="Max" @keyup.enter="handleSearch" class="range-input-max"></el-input>
          </div>
        </el-form-item>
        <el-form-item label="Elongation After Fracture (%)">
          <div class="range-input">
            <el-input v-model="searchForm.percentage_elongation_min" placeholder="Min" @keyup.enter="handleSearch" class="range-input-min"></el-input>
            <span class="range-separator">-</span>
            <el-input v-model="searchForm.percentage_elongation_max" placeholder="Max" @keyup.enter="handleSearch" class="range-input-max"></el-input>
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="resetSearch">Reset</el-button>
        </el-form-item>
      </el-form>

      <!-- Data table -->
      <el-table
        v-loading="loading"
        :data="tableData"
        border
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="creep_id" label="ID" width="80"></el-table-column>
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
        <el-table-column prop="creep_temp" label="Test Temperature (℃)" width="120"></el-table-column>
        <el-table-column prop="creep_time" label="Test Duration (h)" width="120"></el-table-column>
        <el-table-column prop="initial_stress" label="Initial Stress (MPa)" width="120"></el-table-column>
        <el-table-column prop="creep_rate" label="Steady-State Creep Rate" width="120"></el-table-column>
        <el-table-column prop="creep_limit" label="Creep Limit (MPa)" width="120"></el-table-column>
        <el-table-column prop="creep_rupture_strength" label="Creep Rupture Strength (MPa)" width="150"></el-table-column>
        <el-table-column prop="rupture_time" label="Rupture Time (h)" width="120"></el-table-column>
        <el-table-column prop="rupture_strength_limit" label="Rupture Strength Limit (MPa)" width="150"></el-table-column>
        <el-table-column prop="percentage_elongation" label="Elongation After Fracture (%)" width="140"></el-table-column>
        <el-table-column prop="entry_time" label="Entry Time" width="180"></el-table-column>
        <el-table-column prop="modify_time" label="Update Time" width="180"></el-table-column>
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="scope">
            <div class="operation-buttons">
              <el-button
                size="small"
                type="primary"
                plain
                @click="handleEdit(scope.row)"
              >Edit</el-button>
              <el-button
                size="small"
                type="danger"
                plain
                @click="handleDelete(scope.row)"
              >Delete</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          :current-page="currentPage"
          @update:current-page="currentPage = $event"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          @update:page-size="pageSize = $event"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        ></el-pagination>
      </div>
    </el-card>

    <!-- 表单对话框 -->
    <el-dialog v-model="formVisible" :title="formType === 'add' ? 'Add Creep Test Data' : 'Edit Creep Test Data'" width="50%">
      <el-form ref="formRef" :model="currentCreTest" :rules="rules" label-width="120px">
        <el-form-item label="Material ID" prop="material_id">
          <el-input v-model="currentCreTest.material_id" placeholder="Please enter material ID"></el-input>
        </el-form-item>
        <el-form-item label="Process ID" prop="process_id">
          <el-input v-model="currentCreTest.process_id" placeholder="Please enter process ID"></el-input>
        </el-form-item>
        <el-form-item label="Test Temperature (℃)" prop="creep_temp">
          <el-input-number v-model="currentCreTest.creep_temp" :precision="1" :step="0.1" :min="0" style="width: 100%"></el-input-number>
        </el-form-item>
        <el-form-item label="Test Duration (h)" prop="creep_time">
          <el-input-number v-model="currentCreTest.creep_time" :precision="2" :step="0.1" :min="0" style="width: 100%"></el-input-number>
        </el-form-item>
        <el-form-item label="Initial Stress (MPa)" prop="initial_stress">
          <el-input-number v-model="currentCreTest.initial_stress" :precision="2" :step="0.1" :min="0" style="width: 100%"></el-input-number>
        </el-form-item>
        <el-form-item label="Steady-State Creep Rate" prop="creep_rate">
          <el-input-number v-model="currentCreTest.creep_rate" :precision="6" :step="0.000001" :min="0" style="width: 100%"></el-input-number>
        </el-form-item>
        <el-form-item label="Creep Limit (MPa)" prop="creep_limit">
          <el-input-number v-model="currentCreTest.creep_limit" :precision="2" :step="0.1" :min="0" style="width: 100%"></el-input-number>
        </el-form-item>
        <el-form-item label="Creep Rupture Strength (MPa)" prop="creep_rupture_strength">
          <el-input-number v-model="currentCreTest.creep_rupture_strength" :precision="2" :step="0.1" :min="0" style="width: 100%"></el-input-number>
        </el-form-item>
        <el-form-item label="Rupture Time (h)" prop="rupture_time">
          <el-input-number v-model="currentCreTest.rupture_time" :precision="2" :step="0.1" :min="0" style="width: 100%"></el-input-number>
        </el-form-item>
        <el-form-item label="Rupture Strength Limit (MPa)" prop="rupture_strength_limit">
          <el-input-number v-model="currentCreTest.rupture_strength_limit" :precision="2" :step="0.1" :min="0" style="width: 100%"></el-input-number>
        </el-form-item>
        <el-form-item label="Elongation After Fracture (%)" prop="percentage_elongation">
          <el-input-number v-model="currentCreTest.percentage_elongation" :precision="2" :step="0.1" :min="0" :max="100" style="width: 100%"></el-input-number>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="formVisible = false">Cancel</el-button>
          <el-button type="primary" @click="handleFormSubmit" :loading="submitting">Confirm</el-button>
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
          :title="`Imported ${importResult.success_count} records; ${importResult.error_count} failed`"
          :type="importResult.error_count === 0 ? 'success' : 'warning'"
          :closable="false"
          show-icon
        ></el-alert>
        <div v-if="importResult.errors && importResult.errors.length > 0" class="error-list">
          <h4>Error Details:</h4>
          <div v-for="(error, index) in importResult.errors" :key="index + String(error)" class="error-item">
            <el-alert
              title="Import validation failed for this row."
              type="error"
              show-icon
            ></el-alert>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="importResultVisible = false">Close</el-button>
          <el-button type="primary" @click="handleImportFinish">Done</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import PageHeader from '@/components/common/PageHeader.vue'
import { getCreTests, createCreTest, updateCreTest, deleteCreTest, importCreTests, exportCreTests } from '@/api/creTest'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getToken } from '@/utils/auth'

export default {
  name: 'CreTestList',
  components: {
    PageHeader
  },
  data() {
    return {
      // 表格数据
      tableData: [],
      loading: false,
      total: 0,
      currentPage: 1,
      pageSize: 10,
      multipleSelection: [],

      // Search条件
      searchForm: {
        material_id: '',
        process_id: '',
        creep_temp_min: '',
        creep_temp_max: '',
        creep_time_min: '',
        creep_time_max: '',
        initial_stress_min: '',
        initial_stress_max: '',
        creep_rate_min: '',
        creep_rate_max: '',
        creep_limit_min: '',
        creep_limit_max: '',
        creep_rupture_strength_min: '',
        creep_rupture_strength_max: '',
        rupture_time_min: '',
        rupture_time_max: '',
        rupture_strength_limit_min: '',
        rupture_strength_limit_max: '',
        percentage_elongation_min: '',
        percentage_elongation_max: ''
      },

      // 表单对话框
      formVisible: false,
      formType: 'add',
      currentCreTest: {
        material_id: '',
        process_id: '',
        creep_temp: null,
        creep_time: null,
        initial_stress: null,
        creep_rate: null,
        creep_limit: null,
        creep_rupture_strength: null,
        rupture_time: null,
        rupture_strength_limit: null,
        percentage_elongation: null
      },
      submitting: false,
      rules: {
        material_id: [
          { required: true, message: 'Please enter material ID', trigger: 'blur' }
        ],
        process_id: [
          { required: true, message: 'Please enter process ID', trigger: 'blur' }
        ],
        creep_temp: [
          { required: true, message: 'Please enter the test temperature', trigger: 'blur' }
        ]
      },

      // 导入导出
      importing: false,
      importResultVisible: false,
      importResult: null
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    // 初始化获取数据
    async fetchData() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize,
          ...this.searchForm
        }
        const response = await getCreTests(params)
        
        // 处理响应数据
        if (response.data) {
          this.tableData = Array.isArray(response.data) ? response.data : (response.data.results || [])
          this.total = response.data.count || response.data.length || 0
        } else {
          this.tableData = Array.isArray(response) ? response : (response.results || [])
          this.total = response.count || response.length || 0
        }
      } catch (error) {
        console.error('Failed to load data:')
        ElMessage.error('Failed to load creep test data')
      } finally {
        this.loading = false
      }
    },

    // Search和Reset
    handleSearch() {
      this.currentPage = 1
      this.fetchData()
    },
    resetSearch() {
      this.searchForm = {
        material_id: '',
        process_id: '',
        creep_temp_min: '',
        creep_temp_max: '',
        creep_time_min: '',
        creep_time_max: '',
        initial_stress_min: '',
        initial_stress_max: '',
        creep_rate_min: '',
        creep_rate_max: '',
        creep_limit_min: '',
        creep_limit_max: '',
        creep_rupture_strength_min: '',
        creep_rupture_strength_max: '',
        rupture_time_min: '',
        rupture_time_max: '',
        rupture_strength_limit_min: '',
        rupture_strength_limit_max: '',
        percentage_elongation_min: '',
        percentage_elongation_max: ''
      }
      this.handleSearch()
    },

    // 分页处理
    handleSizeChange() {
      this.fetchData()
    },
    handleCurrentChange() {
      this.fetchData()
    },

    // 表格选择
    handleSelectionChange(val) {
      this.multipleSelection = val
    },

    // 增删改查Actions
    handleAdd() {
      this.formType = 'add'
      this.currentCreTest = {
        material_id: '',
        process_id: '',
        creep_temp: null,
        creep_time: null,
        initial_stress: null,
        creep_rate: null,
        creep_limit: null,
        creep_rupture_strength: null,
        rupture_time: null,
        rupture_strength_limit: null,
        percentage_elongation: null
      }
      this.formVisible = true
    },
    handleEdit(row) {
      this.formType = 'edit'
      
      // 深拷贝避免直接修改表格数据
      this.currentCreTest = JSON.parse(JSON.stringify({
        creep_id: row.creep_id,
        material_id: row.material?.material_id || row.material_id,
        process_id: row.process?.process_id || row.process_id,
        creep_temp: row.creep_temp,
        creep_time: row.creep_time,
        initial_stress: row.initial_stress,
        creep_rate: row.creep_rate,
        creep_limit: row.creep_limit,
        creep_rupture_strength: row.creep_rupture_strength,
        rupture_time: row.rupture_time,
        rupture_strength_limit: row.rupture_strength_limit,
        percentage_elongation: row.percentage_elongation
      }))
      
      this.formVisible = true
    },
    async handleFormSubmit() {
      if (!this.$refs.formRef) return
      
      try {
        await this.$refs.formRef.validate()
        
        this.submitting = true
        if (this.formType === 'add') {
          await createCreTest(this.currentCreTest)
          ElMessage.success('Added successfully')
        } else {
          await updateCreTest(this.currentCreTest.creep_id, this.currentCreTest)
          ElMessage.success('Updated successfully')
        }
        
        this.formVisible = false
        this.fetchData()
      } catch (error) {
        console.error('Form submission failed:')
        ElMessage.error('Failed to save the creep test data')
      } finally {
        this.submitting = false
      }
    },
    async handleDelete(row) {
      try {
        await ElMessageBox.confirm(
          `Are you sure you want to delete creep test record ${row.creep_id}?`,
          'Confirm',
          {
            confirmButtonText: 'Confirm',
            cancelButtonText: 'Cancel',
            type: 'warning'
          }
        )
        
        await deleteCreTest(row.creep_id)
        ElMessage.success('Deleted successfully')
        this.fetchData()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Delete failed:')
          ElMessage.error('Failed to delete the creep test record')
        }
      }
    },

    // Import Data
    handleFileChange(file) {
      if (!file) return
      
      this.importing = true
      this.handleImport(file.raw)
    },

    async handleImport(file) {
      const isExcel = file.type === 'application/vnd.ms-excel' || 
                     file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      const isLt10M = file.size / 1024 / 1024 < 10

      if (!isExcel) {
        ElMessage.error('Only Excel files are allowed!')
        this.importing = false
        return
      }

      if (!isLt10M) {
        ElMessage.error('File size cannot exceed 10MB!')
        this.importing = false
        return
      }

      try {
        const formData = new FormData()
        formData.append('file', file)
        const response = await importCreTests(formData)
        this.importResult = response.data || response
        this.importResultVisible = true
      } catch (error) {
        console.error('Import failed:')
        ElMessage.error('Import failed. Please check the file and try again.')
      } finally {
        this.importing = false
      }
    },

    handleImportFinish() {
      this.importResultVisible = false
      this.fetchData()
    },

    // Export Data
    async handleExport() {
      this.handleExportCommand('current')
    },

    async handleExportCommand(command) {
      let ids = []
      if (command === 'selected') {
        if (this.multipleSelection.length === 0) {
          ElMessage.warning('Please select at least one record')
          return
        }
        ids = this.multipleSelection.map(item => item.creep_id)
      }

      try {
        const response = await exportCreTests({
          property_ids: command === 'all' ? [] : (command === 'selected' ? ids : this.tableData.map(item => item.creep_id)),
          format: 'excel'
        })

        // 处理下载
        const blob = new Blob(
          [response.data], 
          { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }
        )
        const link = document.createElement('a')
        link.href = URL.createObjectURL(blob)
        link.download = `creep_test_data_${new Date().toISOString().split('T')[0]}.xlsx`
        link.click()
        URL.revokeObjectURL(link.href)
        
        ElMessage.success('Export successful')
      } catch (error) {
        console.error('Export failed:')
        ElMessage.error('Export failed. Please try again.')
      }
    }
  }
}
</script>

<style scoped>
.cretest-list {
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
}

.error-item {
  margin-bottom: 10px;
}

.small-text {
  font-size: 12px;
  color: #909399;
}

.operation-buttons {
  display: flex;
  gap: 5px;
}

.range-input {
  display: flex;
  align-items: center;
}

.range-input-min,
.range-input-max {
  width: 100px;
  margin-right: 10px;
}

.range-separator {
  margin: 0 10px;
}
</style> 
