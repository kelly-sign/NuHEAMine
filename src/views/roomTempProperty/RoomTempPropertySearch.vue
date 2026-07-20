<template>
  <div class="app-container">
    <!-- Search form -->
    <el-form :inline="true" :model="searchForm" class="demo-form-inline">
      <el-form-item label="Material ID">
        <el-input v-model="searchForm.material_id" placeholder="Please enter material ID" clearable></el-input>
      </el-form-item>
      <el-form-item label="Process ID">
        <el-input v-model="searchForm.process_id" placeholder="Please enter process ID" clearable></el-input>
      </el-form-item>
      <el-form-item label="Phase Structure">
        <el-input v-model="searchForm.phase_structure" placeholder="Please enter phase structure" clearable></el-input>
      </el-form-item>
      
      <!-- 范围查询表单 -->
      <el-collapse v-model="activeCollapse" class="range-search-collapse">
        <el-collapse-item title="Mechanical Property Range Search" name="1">
          <div class="range-search-content">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="Hardness (HV)" class="range-form-item">
                  <div class="range-input-group">
                    <el-input-number 
                      v-model="searchForm.hardness_min" 
                      :precision="1" 
                      :step="0.1" 
                      :min="0"
                      placeholder="Min"
                      class="range-input">
                    </el-input-number>
                    <span class="range-separator">-</span>
                    <el-input-number 
                      v-model="searchForm.hardness_max" 
                      :precision="1" 
                      :step="0.1" 
                      :min="0"
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
                      placeholder="Min"
                      class="range-input">
                    </el-input-number>
                    <span class="range-separator">-</span>
                    <el-input-number 
                      v-model="searchForm.yield_strength_c_max" 
                      :precision="1" 
                      :step="0.1" 
                      :min="0"
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
                      placeholder="Min"
                      class="range-input">
                    </el-input-number>
                    <span class="range-separator">-</span>
                    <el-input-number 
                      v-model="searchForm.yield_strength_t_max" 
                      :precision="1" 
                      :step="0.1" 
                      :min="0"
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
                      placeholder="Min"
                      class="range-input">
                    </el-input-number>
                    <span class="range-separator">-</span>
                    <el-input-number 
                      v-model="searchForm.ultimate_strength_c_max" 
                      :precision="1" 
                      :step="0.1" 
                      :min="0"
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
                      placeholder="Min"
                      class="range-input">
                    </el-input-number>
                    <span class="range-separator">-</span>
                    <el-input-number 
                      v-model="searchForm.ultimate_strength_t_max" 
                      :precision="1" 
                      :step="0.1" 
                      :min="0"
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
                      placeholder="Min"
                      class="range-input">
                    </el-input-number>
                    <span class="range-separator">-</span>
                    <el-input-number 
                      v-model="searchForm.fracture_strain_c_max" 
                      :precision="1" 
                      :step="0.1" 
                      :min="0"
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
                      placeholder="Min"
                      class="range-input">
                    </el-input-number>
                    <span class="range-separator">-</span>
                    <el-input-number 
                      v-model="searchForm.fracture_strain_t_max" 
                      :precision="1" 
                      :step="0.1" 
                      :min="0"
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

      <el-form-item class="search-buttons">
        <el-button type="primary" @click="handleSearch">Search</el-button>
        <el-button @click="resetForm">Reset</el-button>
      </el-form-item>
    </el-form>

    <!-- Data table -->
    <el-table
      v-loading="loading"
      :data="tableData"
      border
      style="width: 100%">
      <!-- 保持原有的表格列不变 -->
      <el-table-column prop="material.material_id" label="Material ID" width="120"></el-table-column>
      <el-table-column prop="process.process_id" label="Process ID" width="120"></el-table-column>
      <el-table-column prop="phase_structure" label="Phase Structure" width="120"></el-table-column>
      <el-table-column prop="hardness_value" label="Hardness (HV)" width="120"></el-table-column>
      <el-table-column prop="yield_strength_c" label="Compressive Yield Strength (MPa)" width="150"></el-table-column>
      <el-table-column prop="yield_strength_t" label="Tensile Yield Strength (MPa)" width="150"></el-table-column>
      <el-table-column prop="ultimate_strength_c" label="Ultimate Compressive Strength (MPa)" width="150"></el-table-column>
      <el-table-column prop="ultimate_strength_t" label="Ultimate Tensile Strength (MPa)" width="150"></el-table-column>
      <el-table-column prop="fracture_strain_c" label="Compressive Fracture Strain (%)" width="150"></el-table-column>
      <el-table-column prop="fracture_strain_t" label="Tensile Fracture Strain (%)" width="150"></el-table-column>
      <el-table-column prop="entry_time" label="Entry Time" width="180"></el-table-column>
      <el-table-column prop="modify_time" label="Modified Time" width="180"></el-table-column>
      <el-table-column label="Actions" width="150" fixed="right">
        <template #default="scope">
          <el-button type="text" size="small" @click="handleEdit(scope.row)">Edit</el-button>
          <el-button type="text" size="small" @click="handleDelete(scope.row)">Delete</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        background
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="currentPage"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total">
      </el-pagination>
    </div>

    <!-- Edit对话框 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="50%">
      <!-- 保持原有的Edit表单不变 -->
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRoomTempProperties, createRoomTempProperty, updateRoomTempProperty, deleteRoomTempProperty } from '@/api/roomTempProperty'

export default {
  name: 'RoomTempPropertySearch',
  setup() {
    // 表格数据
    const tableData = ref([])
    const loading = ref(false)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = ref(0)
    const dialogVisible = ref(false)
    const dialogTitle = ref('')

    // Search form数据
    const searchForm = reactive({
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

    // Add折叠面板的激活状态
    const activeCollapse = ref(['1'])

    // Reset表单
    const resetForm = () => {
      Object.keys(searchForm).forEach(key => {
        searchForm[key] = key.includes('_min') || key.includes('_max') ? null : ''
      })
      fetchData()
    }

    // 获取数据
    const fetchData = async () => {
      loading.value = true
      try {
        const response = await getRoomTempProperties({
          page: currentPage.value,
          page_size: pageSize.value,
          ...searchForm
        })
        tableData.value = response.results
        total.value = response.count
      } catch (error) {
        console.error('Failed to load data:')
        ElMessage.error('Failed to load data')
      } finally {
        loading.value = false
      }
    }

    // Search
    const handleSearch = () => {
      currentPage.value = 1
      fetchData()
    }

    // 分页处理
    const handleSizeChange = (val) => {
      pageSize.value = val
      fetchData()
    }

    const handleCurrentChange = (val) => {
      currentPage.value = val
      fetchData()
    }

    // Edit处理
    const handleEdit = (row) => {
      dialogTitle.value = 'Edit Room-Temperature Property Data'
      dialogVisible.value = true
      // 这里可以AddEdit表单的数据初始化
    }

    // Delete处理
    const handleDelete = (row) => {
      ElMessageBox.confirm('Are you sure you want to delete this record?', 'Confirm', {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }).then(async () => {
        try {
          await deleteRoomTempProperty(row.rtproperty_id)
          ElMessage.success('Deleted successfully')
          fetchData()
        } catch (error) {
          console.error('Delete failed:')
          ElMessage.error('Failed to delete the record')
        }
      }).catch(() => {})
    }

    // 初始化加载数据
    fetchData()

    return {
      tableData,
      loading,
      currentPage,
      pageSize,
      total,
      dialogVisible,
      dialogTitle,
      searchForm,
      resetForm,
      handleSearch,
      handleSizeChange,
      handleCurrentChange,
      handleEdit,
      handleDelete,
      activeCollapse
    }
  }
}
</script>

<style scoped>
.range-search-collapse {
  margin: 10px 0;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.range-search-content {
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.range-form-item {
  margin-bottom: 15px;
}

.range-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.range-input {
  width: 120px;
}

.range-separator {
  color: #606266;
  font-weight: bold;
}

.search-buttons {
  margin-top: 10px;
  margin-left: 0;
}

:deep(.el-collapse-item__header) {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-input-number .el-input__wrapper) {
  padding: 0 8px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style> 
