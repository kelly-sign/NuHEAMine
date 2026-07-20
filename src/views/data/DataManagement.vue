<template>
  <div class="data-management">
    <el-card class="search-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="Basic Search" name="basic">
          <el-form :inline="true" :model="searchForm" class="search-form">
            <el-form-item label="Material Name">
              <el-input v-model="searchForm.material_name" placeholder="Please enter material name"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleBasicSearch">Search</el-button>
              <el-button @click="resetSearch">Reset</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="Advanced Search" name="advanced">
          <advanced-search
            ref="advancedSearch"
            @search="handleAdvancedSearch"
          ></advanced-search>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-card class="data-card">
      <div class="operation-bar">
        <el-button type="primary" @click="handleAdd">Add Material</el-button>
        <el-upload
          class="upload-demo"
          action="#"
          :auto-upload="false"
          :on-change="handleFileChange"
          :before-upload="beforeUpload"
          :show-file-list="false"
        >
          <el-button type="success">Import Data</el-button>
        </el-upload>
        <el-button type="warning" @click="handleExport">Export Data</el-button>
      </div>

      <el-table
        :data="tableData"
        border
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="material_id" label="Material ID" width="100"></el-table-column>
        <el-table-column prop="material_name" label="Material Name" width="150"></el-table-column>
        <el-table-column label="Elemental Composition" min-width="300">
          <template #default="{ row }">
            <el-tooltip effect="dark" placement="top">
              <template #content>
                <div v-for="(value, element) in getComposition(row)" :key="element">
                  {{ element.toUpperCase() }}: {{ value }}%
                </div>
              </template>
              <el-tag>View Composition</el-tag>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="entry_time" label="Entry Time" width="180"></el-table-column>
        <el-table-column prop="modify_time" label="Modified Time" width="180"></el-table-column>
        <el-table-column label="Actions" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="text" @click="handleEdit(row)">Edit</el-button>
            <el-button type="text" @click="handleDelete(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
        ></el-pagination>
      </div>
    </el-card>

    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="50%"
    >
      <el-form :model="form" label-width="120px">
        <el-form-item label="Material Name">
          <el-input v-model="form.material_name"></el-input>
        </el-form-item>
        <el-form-item label="Elemental Composition">
          <div v-for="element in elements" :key="element" class="composition-item">
            <span class="element-label">{{ element.toUpperCase() }}:</span>
            <el-input-number
              v-model="form[`composition_${element}`]"
              :min="0"
              :max="100"
              :precision="5"
              :step="0.1"
              size="small"
            ></el-input-number>
            <span class="unit">%</span>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="handleSubmit">Confirm</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdvancedSearch from '@/views/data/AdvancedSearch.vue'
import { getMaterials, createMaterial, updateMaterial, deleteMaterial, exportMaterials, importMaterials } from '@/api/material'
import axios from 'axios'

export default {
  name: 'DataSearch',
  components: {
    AdvancedSearch
  },
  setup() {
    const activeTab = ref('basic')
    const loading = ref(false)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = ref(0)
    const dialogVisible = ref(false)
    const dialogTitle = ref('')
    const tableData = ref([])
    const advancedSearch = ref(null)

    const elements = [
      'al', 'c', 'co', 'cr', 'cu', 'fe', 'hf', 'mg', 'mn', 'mo',
      'n', 'nb', 'ni', 'sc', 'si', 'sn', 'ta', 'ti', 'v', 'w', 'y', 'zn', 'zr'
    ]

    const searchForm = reactive({
      material_name: ''
    })

    const form = reactive({
      material_name: '',
      ...Object.fromEntries(elements.map(e => [`composition_${e}`, 0]))
    })

    const fetchData = async (params = {}) => {
      loading.value = true
      try {
        const response = await getMaterials({
          page: params.page || currentPage.value,
          page_size: params.page_size || pageSize.value,
          material_name: params.material_name || searchForm.material_name,
          conditions: params.conditions || {}
        })
        
        if (response && typeof response === 'object') {
          tableData.value = response.results || []
          total.value = response.count || 0
          currentPage.value = parseInt(response.page) || 1
          pageSize.value = parseInt(response.page_size) || 10
        } else {
          console.warn('Invalid material-data response format.')
          tableData.value = []
          total.value = 0
        }
      } catch (error) {
        console.error('Failed to load data:')
        ElMessage.error('Failed to load material data')
        tableData.value = []
        total.value = 0
      } finally {
        loading.value = false
      }
    }

    const handleBasicSearch = () => {
      currentPage.value = 1
      fetchData({
        page: currentPage.value,
        page_size: pageSize.value,
        ...(activeTab.value === 'basic' ? searchForm : {})
      })
    }

    const handleAdvancedSearch = (conditions) => {
      currentPage.value = 1
      fetchData({
        page: currentPage.value,
        page_size: pageSize.value,
        conditions: conditions
      })
    }

    const resetSearch = () => {
      searchForm.material_name = ''
      if (advancedSearch.value) {
        advancedSearch.value.reset()
      }
      fetchData({
        page: currentPage.value,
        page_size: pageSize.value,
        ...(activeTab.value === 'basic' ? searchForm : {})
      })
    }

    const handleAdd = () => {
      dialogTitle.value = 'Add Material'
      Object.keys(form).forEach(key => {
        form[key] = key.startsWith('composition_') ? 0 : ''
      })
      dialogVisible.value = true
    }

    const handleEdit = (row) => {
      dialogTitle.value = 'Edit Material'
      Object.keys(form).forEach(key => {
        form[key] = row[key]
      })
      dialogVisible.value = true
    }

    const handleDelete = async (row) => {
      try {
        await ElMessageBox.confirm('Are you sure you want to delete this material?', 'Confirm', {
          type: 'warning'
        })
        await deleteMaterial(row.material_id)
        ElMessage.success('Deleted successfully')
        fetchData({
          page: currentPage.value,
          page_size: pageSize.value,
          ...(activeTab.value === 'basic' ? searchForm : {})
        })
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('Failed to delete the material')
        }
      }
    }

    const handleSubmit = async () => {
      try {
        if (dialogTitle.value === 'Add Material') {
          await createMaterial(form)
          ElMessage.success('Added successfully')
        } else {
          await updateMaterial(form.material_id, form)
          ElMessage.success('Updated successfully')
        }
        dialogVisible.value = false
        fetchData({
          page: currentPage.value,
          page_size: pageSize.value,
          ...(activeTab.value === 'basic' ? searchForm : {})
        })
      } catch (error) {
        ElMessage.error('Operation failed')
      }
    }

    const handleFileChange = async (file) => {
      try {
        loading.value = true
        const formData = new FormData()
        formData.append('file', file.raw)
        
        const response = await importMaterials(formData)
        
        if (response.data.success_count > 0) {
          ElMessage.success(`Import complete: ${response.data.success_count} of ${response.data.total_count} records imported`)
          
          if (response.data.error_count > 0) {
            // 显示错误记录
            ElMessageBox.alert(
              `<div style="max-height: 300px; overflow-y: auto;">
                <p>The following errors were found during import:</p>
                ${response.data.errors.map(err => 
                  `<p>Row ${err.row}: Validation failed for this row.</p>`
                ).join('')}
              </div>`,
              'Import Results',
              {
                dangerouslyUseHTMLString: true,
                confirmButtonText: 'Confirm'
              }
            )
          }
        } else {
          ElMessage.error('Import failed. Please check the file and try again.')
        }
        
        // 刷新数据
        await fetchData({
          page: currentPage.value,
          page_size: pageSize.value,
          ...(activeTab.value === 'basic' ? searchForm : {})
        })
      } catch (error) {
        console.error('Import failed:')
        ElMessage.error('Import failed. Please check the file and try again.')
      } finally {
        loading.value = false
      }
    }

    const beforeUpload = (file) => {
      const isValidFormat = /\.(xlsx|xls|csv)$/i.test(file.name)
      const isLt10M = file.size / 1024 / 1024 < 10

      if (!isValidFormat) {
        ElMessage.error('Only Excel or CSV files are allowed!')
        return false
      }
      if (!isLt10M) {
        ElMessage.error('File size cannot exceed 10MB!')
        return false
      }
      return true
    }

    const handleExport = async () => {
      try {
        const response = await exportMaterials()
        const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        const link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        link.download = 'materials.xlsx'
        link.click()
      } catch (error) {
        ElMessage.error('Export failed')
      }
    }

    const handlePageChange = (page) => {
      currentPage.value = page
      fetchData({
        page: currentPage.value,
        page_size: pageSize.value,
        ...(activeTab.value === 'basic' ? searchForm : {})
      })
    }

    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      fetchData({
        page: currentPage.value,
        page_size: pageSize.value,
        ...(activeTab.value === 'basic' ? searchForm : {})
      })
    }

    const getComposition = (row) => {
      const composition = {}
      elements.forEach(element => {
        composition[element] = row[`composition_${element}`]
      })
      return composition
    }

    onMounted(async () => {
      try {
        await fetchData({
          page: 1,
          page_size: 10,
          material_name: ''
        })
      } catch (error) {
        console.error('Initial data loading failed:')
      }
    })

    return {
      activeTab,
      loading,
      currentPage,
      pageSize,
      total,
      dialogVisible,
      dialogTitle,
      tableData,
      searchForm,
      form,
      elements,
      handleBasicSearch,
      handleAdvancedSearch,
      resetSearch,
      handleAdd,
      handleEdit,
      handleDelete,
      handleSubmit,
      handleFileChange,
      beforeUpload,
      handleExport,
      handlePageChange,
      handleSizeChange,
      getComposition
    }
  }
}
</script>

<style scoped>
.data-management {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.search-form {
  margin-top: 20px;
}

.data-card {
  margin-bottom: 20px;
}

.operation-bar {
  margin-bottom: 20px;
}

.operation-bar .el-button {
  margin-right: 10px;
}

.composition-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.element-label {
  width: 40px;
  text-align: right;
  margin-right: 10px;
}

.unit {
  margin-left: 10px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style> 
