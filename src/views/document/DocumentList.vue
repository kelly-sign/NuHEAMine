<template>
  <div class="document-list">
    <page-header title="Reference Documents Table">
      <template #actions>
        <el-button type="primary" @click="handleAdd">
          Add Reference
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
          <span>Reference List</span>
        </div>
      </template>

      <!-- Search form -->
      <el-form :inline="true" :model="searchForm" class="search-form" @submit.prevent>
        <el-form-item label="Reference Title">
          <el-input v-model="searchForm.doc_name" placeholder="Keyword" clearable @keyup.enter="handleSearch"></el-input>
        </el-form-item>
        <el-form-item label="DOI">
          <el-input v-model="searchForm.doc_doi" placeholder="DOI" clearable @keyup.enter="handleSearch"></el-input>
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
        <el-table-column prop="document_id" label="Reference ID" width="80"></el-table-column>
        <el-table-column prop="doc_name" label="Reference Title" min-width="280" show-overflow-tooltip></el-table-column>
        <el-table-column prop="doc_doi" label="DOI" min-width="180" show-overflow-tooltip></el-table-column>
        <el-table-column label="Online Link" min-width="200">
          <template #default="scope">
            <el-link type="primary" :href="scope.row.doc_url" target="_blank" :underline="false">
              {{ scope.row.doc_url }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="entry_time" label="Entry Time" width="180"></el-table-column>
        <el-table-column prop="modify_time" label="Updated At" width="180"></el-table-column>
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
    <el-dialog v-model="formVisible" :title="formType === 'add' ? 'Add Reference' : 'Edit Reference'" width="50%">
      <el-form ref="formRef" :model="currentDocument" :rules="rules" label-width="100px">
        <el-form-item label="Reference Title" prop="doc_name">
          <el-input v-model="currentDocument.doc_name" placeholder="Enter the reference title"></el-input>
        </el-form-item>
        <el-form-item label="DOI" prop="doc_doi">
          <el-input v-model="currentDocument.doc_doi" placeholder="Enter the DOI"></el-input>
        </el-form-item>
        <el-form-item label="Online Link" prop="doc_url">
          <el-input v-model="currentDocument.doc_url" placeholder="Enter the reference URL"></el-input>
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
          :title="`Imported ${importResult.success_count} record(s); ${importResult.error_count} failed`"
          :type="importResult.error_count === 0 ? 'success' : 'warning'"
          :closable="false"
          show-icon
        ></el-alert>
        <div v-if="importResult.errors && importResult.errors.length > 0" class="error-list">
          <h4>Import Errors:</h4>
          <div v-for="(error, index) in importResult.errors" :key="index" class="error-item">
            <el-alert
              :title="`Import failed for item ${index + 1}`"
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
import { getDocuments, createDocument, updateDocument, deleteDocument, importDocuments, exportDocuments } from '@/api/document'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'DocumentList',
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
        doc_name: '',
        doc_doi: ''
      },

      // 表单对话框
      formVisible: false,
      formType: 'add',
      currentDocument: {
        doc_name: '',
        doc_doi: '',
        doc_url: ''
      },
      submitting: false,
      rules: {
        doc_name: [
          { required: true, message: 'Enter the reference title', trigger: 'blur' }
        ],
        doc_doi: [
          { required: true, message: 'Enter the DOI', trigger: 'blur' }
        ],
        doc_url: [
          { required: true, message: 'Enter the online link', trigger: 'blur' }
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
        const response = await getDocuments(params)
        
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
        ElMessage.error('Failed to load data. Please try again.')
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
        doc_name: '',
        doc_doi: ''
      }
      this.currentPage = 1
      this.fetchData()
    },

    // 分页处理
    handleSizeChange(size) {
      this.pageSize = size
      this.fetchData()
    },
    handleCurrentChange(page) {
      this.currentPage = page
      this.fetchData()
    },

    // 表格选择
    handleSelectionChange(selection) {
      this.multipleSelection = selection
    },

    // Add文献
    handleAdd() {
      this.formType = 'add'
      this.currentDocument = {
        doc_name: '',
        doc_doi: '',
        doc_url: ''
      }
      this.formVisible = true
    },

    // Edit文献
    handleEdit(row) {
      this.formType = 'edit'
      this.currentDocument = { ...row }
      this.formVisible = true
    },

    // Delete文献
    handleDelete(row) {
      ElMessageBox.confirm('Are you sure you want to delete this reference?', 'Confirm', {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }).then(async () => {
        try {
          await deleteDocument(row.document_id)
          ElMessage.success('Deleted successfully')
          this.fetchData()
        } catch (error) {
          console.error('Delete failed:')
          ElMessage.error('Delete failed. Please try again.')
        }
      }).catch(() => {
        ElMessage.info('Deletion canceled')
      })
    },

    // 提交表单
    async handleFormSubmit() {
      if (!this.$refs.formRef) return


      // 处理URL格式
      if (this.currentDocument.doc_url && 
          !this.currentDocument.doc_url.startsWith('http://') && 
          !this.currentDocument.doc_url.startsWith('https://')) {
        this.currentDocument.doc_url = 'https://' + this.currentDocument.doc_url
      }

      this.$refs.formRef.validate(async (valid) => {
        if (!valid) {
          console.error('Form validation failed')
          return
        }

        this.submitting = true
        try {
          if (this.formType === 'add') {
            // 创建文献
            const response = await createDocument(this.currentDocument)
            ElMessage.success('Added successfully')
          } else {
            // 更新文献
            const response = await updateDocument(this.currentDocument.document_id, this.currentDocument)
            ElMessage.success('Updated successfully')
          }
          this.formVisible = false
          this.fetchData()
        } catch (error) {
          console.error('Operation failed:')
          console.error('Submitted data:')
          ElMessage.error('Operation failed. Please check the submitted values and try again.')
        } finally {
          this.submitting = false
        }
      })
    },

    // 文件导入
    handleFileChange(file) {
      if (!file) return

      // 检查文件Type
      const isExcel = file.name.endsWith('.xlsx') || file.name.endsWith('.xls')
      if (!isExcel) {
        ElMessage.error('Only .xlsx and .xls Excel files are supported')
        return
      }

      // 检查文件大小，限制为10MB
      const isLt10M = file.size / 1024 / 1024 < 10
      if (!isLt10M) {
        ElMessage.error('File size cannot exceed 10MB')
        return
      }

      // 上传文件
      this.importing = true
      const formData = new FormData()
      formData.append('file', file.raw)

      importDocuments(formData).then(response => {
        this.importResult = response.data || response
        this.importResultVisible = true
        ElMessage.success('Import successful')
        this.fetchData()
      }).catch(error => {
        console.error('Import failed:')
        ElMessage.error('Import failed. Please check the file and try again.')
      }).finally(() => {
        this.importing = false
      })
    },

    // 处理导入完成
    handleImportFinish() {
      this.importResultVisible = false
      this.importResult = null
      this.fetchData()
    },

    // 导出文献数据
    async handleExport() {
      await this.exportData('all')
    },

    // 根据不同命令Export Data
    async handleExportCommand(command) {
      await this.exportData(command)
    },

    // Export Data方法
    async exportData(type) {
      try {
        let property_ids = []
        
        if (type === 'selected') {
          if (this.multipleSelection.length === 0) {
            ElMessage.warning('Select at least one record to export')
            return
          }
          property_ids = this.multipleSelection.map(item => item.document_id)
        } else if (type === 'current') {
          property_ids = this.tableData.map(item => item.document_id)
        }

        // 显示加载Confirm
        const loadingInstance = ElMessage({
          type: 'info',
          message: 'Exporting data. Please wait...',
          duration: 0
        })

        try {
          const response = await exportDocuments({
            format: 'excel',
            property_ids: type !== 'all' ? property_ids : []
          })
          
          // 关闭加载Confirm
          loadingInstance.close()
          
          // 处理二进制数据并下载
          if (response && response.data) {
            // response是axios响应对象，data属性包含Blob数据
            const blob = new Blob([response.data], { 
              type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
            })
            const link = document.createElement('a')
            link.href = URL.createObjectURL(blob)
            link.download = `reference_data_${new Date().toISOString().replace(/[-:.]/g, '')}.xlsx`
            link.click()
            URL.revokeObjectURL(link.href)
            ElMessage.success('Export successful')
          } else {
            console.error('Invalid export response format:')
            ElMessage.error('Export failed: Invalid response format')
          }
        } catch (error) {
          // 关闭加载Confirm
          loadingInstance.close()
          throw error
        }
      } catch (error) {
        console.error('Export failed:')
        ElMessage.error('Export failed. Please try again.')
      }
    }
  }
}
</script>

<style scoped>
.document-list {
  padding: 20px;
}

.list-card {
  margin-top: 20px;
}

.search-form {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.operation-buttons {
  display: flex;
  gap: 10px;
}

.error-list {
  margin-top: 15px;
}

.error-item {
  margin-bottom: 10px;
}

.el-link {
  display: block;
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style> 
