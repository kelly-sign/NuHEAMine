<template>
  <div class="imp-test-list">
    <page-header title="Impact Test Table">
      <template #actions>
        <el-button type="primary" @click="handleAdd">
          Add Impact Test Data
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
          <span>Impact Test Data</span>
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
        <el-form-item label="Impact Type">
          <el-select v-model="searchForm.impact_type" placeholder="Impact type" clearable>
            <el-option label="Charpy Impact" value="夏比冲击"></el-option>
            <el-option label="Izod Impact" value="悬臂梁冲击"></el-option>
            <el-option label="Drop-Weight Impact" value="落锤冲击"></el-option>
            <el-option label="Other" value="其他"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="Fracture Type">
          <el-select v-model="searchForm.fracture_type" placeholder="Fracture type" clearable>
            <el-option label="Ductile Fracture" value="韧性断裂"></el-option>
            <el-option label="Brittle Fracture" value="脆性断裂"></el-option>
            <el-option label="Mixed Fracture" value="混合断裂"></el-option>
            <el-option label="Other" value="其他"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="Impact Energy (J)">
          <div class="range-input">
            <el-input v-model="searchForm.impact_energy_min" placeholder="Min" @keyup.enter="handleSearch" class="range-input-min"></el-input>
            <span class="range-separator">-</span>
            <el-input v-model="searchForm.impact_energy_max" placeholder="Max" @keyup.enter="handleSearch" class="range-input-max"></el-input>
          </div>
        </el-form-item>
        <el-form-item label="Absorbed Energy (J)">
          <div class="range-input">
            <el-input v-model="searchForm.absorbed_energy_min" placeholder="Min" @keyup.enter="handleSearch" class="range-input-min"></el-input>
            <span class="range-separator">-</span>
            <el-input v-model="searchForm.absorbed_energy_max" placeholder="Max" @keyup.enter="handleSearch" class="range-input-max"></el-input>
          </div>
        </el-form-item>
        <el-form-item label="Impact Toughness (J/cm²)">
          <div class="range-input">
            <el-input v-model="searchForm.impact_tough_value_min" placeholder="Min" @keyup.enter="handleSearch" class="range-input-min"></el-input>
            <span class="range-separator">-</span>
            <el-input v-model="searchForm.impact_tough_value_max" placeholder="Max" @keyup.enter="handleSearch" class="range-input-max"></el-input>
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
        <el-table-column prop="impact_id" label="ID" width="80"></el-table-column>
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
        <el-table-column prop="impact_temp" label="Test Temperature (℃)" width="100"></el-table-column>
        <el-table-column prop="impact_type" label="Impact Type" width="150">
          <template #default="scope">
            {{ formatImpactType(scope.row.impact_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="impact_energy" label="Impact Energy (J)" width="120"></el-table-column>
        <el-table-column prop="absorbed_energy" label="Absorbed Energy (J)" width="100"></el-table-column>
        <el-table-column prop="impact_tough_value" label="Impact Toughness (J/cm²)" width="150"></el-table-column>
        <el-table-column prop="fracture_type" label="Fracture Type" width="140">
          <template #default="scope">
            {{ formatFractureType(scope.row.fracture_type) }}
          </template>
        </el-table-column>
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
    <imp-test-form
      v-model:visible="formVisible"
      :type="formType"
      :imp-test="currentImpTest"
      @success="handleFormSuccess"
    ></imp-test-form>

    <!-- Import Results对话框 -->
    <el-dialog
      title="Import Results"
      :modelValue="importResultVisible"
      @update:modelValue="importResultVisible = $event"
      width="600px"
    >
      <div v-if="importResult">
        <el-alert
          :title="`Imported ${importResult.success} records; ${importResult.failure} failed`"
          :type="importResult.failure === 0 ? 'success' : 'warning'"
          :closable="false"
          show-icon
        ></el-alert>
        <div v-if="importResult.errors && importResult.errors.length > 0" class="error-list">
          <h4>Error Details:</h4>
          <div v-for="(error, index) in importResult.errors" :key="index" class="error-item">
            <el-alert
              :title="`Row ${error.row}`"
              description="Import validation failed for this row."
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
import PageHeader from '@/components/common/PageHeader'
import ImpTestForm from './ImpTestForm'
import { getImpTests, deleteImpTest, importImpTests, exportImpTests } from '@/api/impTest'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getToken } from '@/utils/auth'

const impactTypeLabels = {
  '夏比冲击': 'Charpy Impact',
  '悬臂梁冲击': 'Izod Impact',
  '落锤冲击': 'Drop-Weight Impact',
  '其他': 'Other'
}

const fractureTypeLabels = {
  '韧性断裂': 'Ductile Fracture',
  '脆性断裂': 'Brittle Fracture',
  '混合断裂': 'Mixed Fracture',
  '其他': 'Other'
}

export default {
  name: 'ImpTestList',
  components: {
    PageHeader,
    ImpTestForm
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
        impact_type: '',
        fracture_type: '',
        impact_energy_min: '',
        impact_energy_max: '',
        absorbed_energy_min: '',
        absorbed_energy_max: '',
        impact_tough_value_min: '',
        impact_tough_value_max: ''
      },

      // 表单对话框
      formVisible: false,
      formType: 'add',
      currentImpTest: null,

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
    formatImpactType(value) {
      return impactTypeLabels[value] || value || '-'
    },
    formatFractureType(value) {
      return fractureTypeLabels[value] || value || '-'
    },
    // 初始化获取数据
    async fetchData() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize,
          ...this.searchForm
        }
        const response = await getImpTests(params)
        
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
        ElMessage.error('Failed to load data')
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
        impact_type: '',
        fracture_type: '',
        impact_energy_min: '',
        impact_energy_max: '',
        absorbed_energy_min: '',
        absorbed_energy_max: '',
        impact_tough_value_min: '',
        impact_tough_value_max: ''
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
      this.currentImpTest = null
      this.formVisible = true
    },
    handleEdit(row) {
      this.formType = 'edit'
      this.currentImpTest = row
      this.formVisible = true
    },
    async handleDelete(row) {
      try {
        await ElMessageBox.confirm(
          `Are you sure you want to delete impact test record ${row.impact_id}?`,
          'Confirm',
          {
            confirmButtonText: 'Confirm',
            cancelButtonText: 'Cancel',
            type: 'warning'
          }
        )
        
        await deleteImpTest(row.impact_id)
        ElMessage.success('Deleted successfully')
        this.fetchData()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Delete failed:')
          ElMessage.error('Failed to delete the impact test record')
        }
      }
    },
    handleFormSuccess() {
      this.fetchData()
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
        const response = await importImpTests(formData)
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
        ids = this.multipleSelection.map(item => item.impact_id)
      }

      try {
        const response = await exportImpTests({
          property_ids: command === 'all' ? [] : (command === 'selected' ? ids : this.tableData.map(item => item.impact_id)),
          format: 'excel'
        })

        // 处理下载
        const blob = new Blob(
          [response.data], 
          { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }
        )
        const link = document.createElement('a')
        link.href = URL.createObjectURL(blob)
        link.download = `impact_test_data_${new Date().toISOString().split('T')[0]}.xlsx`
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
.imp-test-list {
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
