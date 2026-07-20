<template>
  <div class="data-list-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>Material List</span>
          <div class="header-buttons">
            <el-button type="success" @click="handleImport">Import Data</el-button>
            <el-button type="warning" @click="handleExport">Export Data</el-button>
            <el-button type="primary" @click="handleAdd">Add Material</el-button>
          </div>
        </div>
      </template>

      <!-- Search bar -->
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="Search by Material Name or ID"
          class="search-input"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch">Search</el-button>
          </template>
        </el-input>
        <el-button @click="handleReset" style="margin-left: 10px">Reset</el-button>
      </div>

      <!-- Data table -->
      <el-table
        v-loading="loading"
        :data="tableData"
        style="width: 100%"
        border
        stripe
        highlight-current-row
      >
        <el-table-column prop="material_id" label="Material ID" width="100" sortable />
        <el-table-column prop="material_name" label="Material Name" min-width="150" show-overflow-tooltip />
        <el-table-column label="Elemental Composition" min-width="200">
          <template #default="{ row }">
            <el-tooltip
              effect="dark"
              placement="top"
              :content="formatComposition(row)"
            >
              <el-tag size="small" type="info">
                {{ formatComposition(row, true) }}
              </el-tag>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="entry_time" label="Creation Time" width="180" sortable>
          <template #default="{ row }">
            {{ formatDate(row.entry_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="modify_time" label="Update Time" width="180" sortable>
          <template #default="{ row }">
            {{ formatDate(row.modify_time) }}
          </template>
        </el-table-column>
        <el-table-column label="Action" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">
              Edit
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              Delete
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Add/Edit dialog -->
    <el-dialog
      :title="dialogType === 'add' ? 'Add Material' : 'Edit Material'"
      v-model="dialogVisible"
      width="50%"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="material-form"
      >
        <el-form-item label="Material ID" prop="material_id">
          <el-input v-model="form.material_id" :disabled="dialogType === 'edit'" />
        </el-form-item>
        <el-form-item label="Material Name" prop="material_name">
          <el-input v-model="form.material_name" />
        </el-form-item>
        <el-form-item label="Elemental Composition">
          <div class="composition-grid">
            <div v-for="element in elements" :key="element" class="composition-item">
              <span class="element-label">{{ element.charAt(0).toUpperCase() + element.slice(1).toLowerCase() }}</span>
              <el-input-number
                v-model="form[`composition_${element}`]"
                :min="0"
                :max="100"
                :precision="2"
                :step="0.1"
                size="small"
              />
              <span class="unit">%</span>
            </div>
          </div>
          <div class="composition-total">
            Total: {{ calculateTotal().toFixed(2) }}%
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

    <!-- Import dialog -->
    <el-dialog
      title="Import Data"
      v-model="importDialogVisible"
      width="30%"
      :close-on-click-modal="false"
    >
      <el-upload
        class="upload-demo"
        drag
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        :before-upload="beforeUpload"
        :file-list="uploadFile ? [uploadFile] : []"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          Drop file here or <em>click to upload</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            Please upload an Excel file (.xlsx, .xls)
            <el-button type="text" @click="downloadTemplate">Download Template</el-button>
          </div>
        </template>
      </el-upload>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importDialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="submitImport">Confirm</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Export dialog -->
    <el-dialog
      title="Export Data"
      v-model="exportDialogVisible"
      width="30%"
    >
      <el-form :model="exportForm" label-width="100px">
        <el-form-item label="Export Format">
          <el-radio-group v-model="exportForm.format">
            <el-radio label="excel">Excel</el-radio>
            <el-radio label="csv">CSV</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Export Range">
          <el-radio-group v-model="exportForm.range">
            <el-radio label="all">All Data</el-radio>
            <el-radio label="current">Current Page</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="exportDialogVisible = false">Cancel</el-button>
          <el-button type="primary" :loading="exportLoading" @click="handleExport">Confirm</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { getMaterials, createMaterial, updateMaterial, deleteMaterial, exportData, importMaterials } from '@/api/material'
import * as XLSX from 'xlsx'

export default {
  name: 'MaterialSearch',
  setup() {
    // 基础数据
    const loading = ref(false)
    const tableData = ref([])
    const total = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const searchQuery = ref('')

    // 对话框控制
    const dialogVisible = ref(false)
    const dialogType = ref('add')
    const importDialogVisible = ref(false)
    const exportDialogVisible = ref(false)
    const exportLoading = ref(false)
    const formRef = ref(null)
    const uploadFile = ref(null)

    // 元素列表
    const elements = [
      'al', 'c', 'co', 'cr', 'cu', 'fe', 'hf', 'mg', 'mn', 'mo',
      'n', 'nb', 'ni', 'sc', 'si', 'sn', 'ta', 'ti', 'v', 'w',
      'y', 'zn', 'zr'
    ]

    // 表单数据
    const form = reactive({
      material_id: '',
      material_name: '',
      ...Object.fromEntries(elements.map(e => [`composition_${e}`, 0]))
    })

    // 表单验证规则
    const rules = {
      material_id: [
        { required: true, message: 'Please enter material ID', trigger: 'blur' },
        { pattern: /^[A-Za-z0-9-_]+$/, message: 'Material ID may only contain letters, numbers, underscores, and hyphens', trigger: 'blur' }
      ],
      material_name: [
        { required: true, message: 'Please enter material name', trigger: 'blur' },
        { min: 2, max: 50, message: 'Length must be between 2 and 50 characters', trigger: 'blur' }
      ]
    }

    // 导出表单
    const exportForm = reactive({
      format: 'excel',
      range: 'all'
    })

    // 获取数据列表
    const fetchData = async () => {
      try {
        loading.value = true
        const params = {
          page: currentPage.value,
          page_size: pageSize.value,
          search: searchQuery.value?.trim() || ''
        }
        
        const response = await getMaterials(params)
        
        // 详细的数据格式验证
        if (!response) {
          throw new Error('No response received from server')
        }

        if (!response.data) {
          throw new Error('Response is missing data field')
        }

        const responseData = response.data

        // 如果后端直接返回数组，则直接使用
        if (Array.isArray(responseData)) {
          tableData.value = responseData.map(processItem).filter(Boolean)
          total.value = responseData.length
          return
        }

        // 如果是分页格式，则解构分页数据
        const { results, count, page, page_size, total_pages } = responseData

        if (!results) {
          throw new Error('Response data is missing results field')
        }

        if (!Array.isArray(results)) {
          console.error('Invalid results format:')
          throw new Error('results field is not an array')
        }
        
        // 处理数据
        tableData.value = results.map(processItem).filter(Boolean)
        
        // 更新分页信息
        total.value = parseInt(count) || results.length
        if (page) {
          currentPage.value = parseInt(page)
        }
        if (page_size) {
          pageSize.value = parseInt(page_size)
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

    // 处理单个数据项
    const processItem = (item) => {
      if (!item) return null
      
      try {
        const processedItem = { ...item }
        
        // 确保所有composition字段都是数字
        elements.forEach(element => {
          const field = `composition_${element}`
          try {
            const value = parseFloat(processedItem[field])
            processedItem[field] = isNaN(value) ? 0 : value
          } catch (error) {
            console.warn('A numeric material field could not be processed.')
            processedItem[field] = 0
          }
        })
        
        // 确保必要的字段存在
        if (!processedItem.material_id) {
          console.warn('Material data is missing the material_id field.')
          return null
        }
        
        if (!processedItem.material_name) {
          processedItem.material_name = 'Unnamed material'
        }
        
        return processedItem
      } catch (error) {
        console.error('Error while processing a data item:')
        return null
      }
    }

    // Search处理
    const handleSearch = () => {
      currentPage.value = 1
      fetchData()
    }

    // ResetSearch
    const handleReset = () => {
      searchQuery.value = ''
      currentPage.value = 1
      fetchData()
    }

    // 分页大小改变
    const handleSizeChange = (val) => {
      pageSize.value = val
      currentPage.value = 1
      fetchData()
    }

    // 页码改变
    const handlePageChange = (val) => {
      currentPage.value = val
      fetchData()
    }

    // Add/Edit处理
    const handleAdd = () => {
      dialogType.value = 'add'
      Object.keys(form).forEach(key => {
        form[key] = key.startsWith('composition_') ? 0 : ''
      })
      dialogVisible.value = true
    }

    const handleEdit = (row) => {
      dialogType.value = 'edit'
      Object.keys(form).forEach(key => {
        form[key] = row[key]
      })
      dialogVisible.value = true
    }

    const calculateTotal = () => {
      const total = elements.reduce((sum, element) => {
        const value = form[`composition_${element}`] || 0
        return sum + value
      }, 0)
      return total
    }

    const handleSubmit = async () => {
      if (!formRef.value) return
      
      try {
        await formRef.value.validate()
        
        // 准备提交数据
        const submitData = {
          material_id: form.material_id,
          material_name: form.material_name
        }
        
        // Add元素组成数据
        elements.forEach(element => {
          const field = `composition_${element}`
          const value = form[field]
          // 确保值是数字，如果不是则设为0
          submitData[field] = typeof value === 'number' ? value : 0
        })
        
        // 检查是否有至少一个元素含量大于0
        const hasComposition = elements.some(element => submitData[`composition_${element}`] > 0)
        if (!hasComposition) {
          ElMessage.warning('Please enter at least one element composition value')
          return
        }
        
        if (dialogType.value === 'add') {
          await createMaterial(submitData)
          ElMessage.success('Added successfully')
        } else {
          await updateMaterial(submitData.material_id, submitData)
          ElMessage.success('Updated successfully')
        }
        
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        console.error('Submission failed:')
        ElMessage.error(`Failed to ${dialogType.value === 'add' ? 'add' : 'update'} the material`)
      }
    }

    // Delete处理
    const handleDelete = async (row) => {
      try {
        await ElMessageBox.confirm('Are you sure you want to delete this material?', 'Confirm', {
          type: 'warning',
          confirmButtonText: 'Confirm',
          cancelButtonText: 'Cancel'
        })
        
        await deleteMaterial(row.material_id)
        ElMessage.success('Deleted successfully')
        fetchData()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Delete failed:')
          ElMessage.error('Failed to delete the material')
        }
      }
    }

    // 导入导出处理
    const handleImport = () => {
      importDialogVisible.value = true
    }

    // 导出处理
    const handleExport = async () => {
      try {
        exportLoading.value = true
        const materialIds = exportForm.range === 'selected' ? 
          tableData.value.map(item => item.material_id) : []
        
        const response = await exportData({
          format: exportForm.format,
          material_ids: materialIds
        })
        
        if (!response || !response.data) {
          throw new Error('Export failed: invalid response data')
        }
        
        // 创建Blob对象
        const blob = new Blob([response.data], {
          type: exportForm.format === 'csv' ? 
            'text/csv;charset=utf-8' : 
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        
        // 创建下载链接
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `materials_${new Date().toISOString().split('T')[0]}.${exportForm.format === 'csv' ? 'csv' : 'xlsx'}`
        
        // 触发下载
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        ElMessage.success('Export successful')
        exportDialogVisible.value = false
      } catch (error) {
        console.error('Export failed:')
        ElMessage.error('Export failed. Please try again.')
      } finally {
        exportLoading.value = false
      }
    }

    const handleFileChange = async (file) => {
      try {
        loading.value = true
        const formData = new FormData()
        formData.append('file', file.raw)
        
        const response = await importMaterials(formData)
        
        if (response.data.success_count > 0) {
          ElMessage.success(`Import successful: ${response.data.success_count} of ${response.data.total_count} records imported`)
          
          if (response.data.error_count > 0) {
            // 显示错误记录
            ElMessageBox.alert(
              `<div style="max-height: 300px; overflow-y: auto;">
                <p>The following errors were found during import:</p>
                ${response.data.errors.map(err => 
                  `<p>Row ${err.row}: Import validation failed.</p>`
                ).join('')}
                ${response.data.error_count > response.data.errors.length ? 
                  `<p>... and ${response.data.error_count - response.data.errors.length} more errors not shown</p>` : 
                  ''}
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
        
        importDialogVisible.value = false
        uploadFile.value = null
        
        // 保持当前分页状态，只刷新Current Page数据
        await fetchData()
      } catch (error) {
        console.error('Import failed:')
        ElMessage.error('Import failed. Please check the file and try again.')
      } finally {
        loading.value = false
      }
    }

    const beforeUpload = (file) => {
      const isValidFormat = /\.(xlsx|xls)$/i.test(file.name)
      const isLt10M = file.size / 1024 / 1024 < 10

      if (!isValidFormat) {
        ElMessage.error('Only Excel files (.xlsx, .xls) are allowed!')
        return false
      }
      if (!isLt10M) {
        ElMessage.error('File size cannot exceed 10MB!')
        return false
      }
      return true
    }

    const downloadTemplate = () => {
      try {
        // 创建一个示例数据
        const templateData = [
          {
            material_name: 'Sample Material 1',
            composition_al: 5.5,
            composition_c: 0.2,
            composition_fe: 94.3
          },
          {
            material_name: 'Sample Material 2',
            composition_ti: 6.0,
            composition_al: 4.0,
            composition_v: 90.0
          }
        ]

        // 创建工作簿
        const wb = XLSX.utils.book_new()
        const ws = XLSX.utils.json_to_sheet(templateData)

        // Add列说明
        const headerRow = [
          'Material name (required)',
          'Al Content (%)',
          'C Content (%)',
          'Fe Content (%)',
          'Ti Content (%)',
          'V Content (%)'
        ]
        XLSX.utils.sheet_add_aoa(ws, [headerRow], { origin: 'A1' })

        // Add说明行
        const instructions = [
          'Notes:',
          '1. Material name is required and cannot be empty',
          '2. At least one element composition is required',
          '3. Element content must be a non-negative number',
          '4. Total element content cannot exceed 100%',
          '5. Material name must be unique',
          '6. File size cannot exceed 10MB',
          '7. Only .xlsx and .xls formats are supported'
        ]
        XLSX.utils.sheet_add_aoa(ws, instructions, { origin: 'A7' })

        // 设置列宽
        const colWidths = [
          { wch: 20 }, // 材料名称
          { wch: 12 }, // Al含量
          { wch: 12 }, // C含量
          { wch: 12 }, // Fe含量
          { wch: 12 }, // Ti含量
          { wch: 12 }  // V含量
        ]
        ws['!cols'] = colWidths

        // 将工作表Add到工作簿
        XLSX.utils.book_append_sheet(wb, ws, 'Material Import Template')

        // 导出文件
        XLSX.writeFile(wb, 'Material Import Template.xlsx')
      } catch (error) {
        console.error('Failed to download template:')
        ElMessage.error('Failed to download the template. Please try again.')
      }
    }

    // 格式化日期
    const formatDate = (date) => {
      if (!date) return 'No data'
      try {
        const d = new Date(date)
        if (isNaN(d.getTime())) return 'No data'
        return d.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false
        })
      } catch (error) {
        console.error('Date formatting failed:')
        return 'No data'
      }
    }

    // 格式化元素组成
    const formatComposition = (row, isShort = false) => {
      if (!row) return 'No data'
      
      try {
        const compositions = elements
          .map(element => {
            const field = `composition_${element}`
            const value = parseFloat(row[field])
            if (!isNaN(value) && value > 0) {
              // 修改元素显示格式：第一个字母大写，第二个字母小写
              const elementDisplay = element.charAt(0).toUpperCase() + element.slice(1).toLowerCase()
              return `${elementDisplay}: ${value.toFixed(2)}%`
            }
            return null
          })
          .filter(Boolean)

        if (compositions.length === 0) return 'No data'
        
        if (isShort) {
          // 只显示前三个元素，如果有更多则显示省略号
          return compositions.slice(0, 3).join(', ') + (compositions.length > 3 ? '...' : '')
        }
        
        // 完整显示所有元素
        return compositions.join(', ')
      } catch (error) {
        console.error('Composition formatting failed:')
        return 'Format error'
      }
    }

    // 在组件挂载时获取数据
    onMounted(async () => {
      await fetchData()
    })

    return {
      loading,
      tableData,
      total,
      currentPage,
      pageSize,
      searchQuery,
      dialogVisible,
      dialogType,
      importDialogVisible,
      exportDialogVisible,
      exportLoading,
      formRef,
      uploadFile,
      elements,
      form,
      rules,
      exportForm,
      handleSearch,
      handleReset,
      handleSizeChange,
      handlePageChange,
      handleAdd,
      handleEdit,
      calculateTotal,
      handleSubmit,
      handleDelete,
      handleImport,
      handleExport,
      handleFileChange,
      beforeUpload,
      formatDate,
      formatComposition,
      downloadTemplate
    }
  }
}
</script>

<style scoped>
.data-list-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-buttons {
  display: flex;
  gap: 10px;
}

.search-bar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.search-input {
  width: 300px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.material-form {
  max-height: 60vh;
  overflow-y: auto;
  padding-right: 20px;
}

.composition-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
}

.composition-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.element-label {
  width: 40px;
  text-align: right;
  font-weight: bold;
}

.unit {
  color: #909399;
}

.composition-total {
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px solid #EBEEF5;
  color: #606266;
}

:deep(.el-upload-dragger) {
  width: 100%;
}

:deep(.el-upload__tip) {
  margin-top: 10px;
  line-height: 1.4;
}
</style> 
