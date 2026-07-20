<script setup>
import { ref } from 'vue'
import { ElMessage, ElLoading } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { importMaterials } from '@/api/material'

const dialogVisible = ref(false)
const errorList = ref([])

const emit = defineEmits(['success'])

const validateData = (data) => {
  const errors = []
  data.forEach((row, index) => {
    if (!row.material_name) {
      errors.push(`Row ${index + 1}: Material name is required`)
    }
    
    // 检查成分数据格式
    const compositions = {}
    let hasComposition = false
    
    Object.keys(row).forEach(key => {
      if (key !== 'material_name' && key !== 'properties') {
        const value = parseFloat(row[key])
        if (isNaN(value)) {
          errors.push(`Row ${index + 1}: ${key.replace('composition_', '').toUpperCase()} content must be numeric`)
        } else if (value < 0) {
          errors.push(`Row ${index + 1}: ${key.replace('composition_', '').toUpperCase()} content cannot be less than 0%`)
        } else {
          compositions[key] = value
          if (value > 0) {
            hasComposition = true
          }
        }
      }
    })
    
    if (!hasComposition) {
      errors.push(`Row ${index + 1}: Enter a content value for at least one element`)
    }
  })
  
  return errors
}

const handleImport = async (uploadFile) => {
  try {
    // 检查文件是否存在
    if (!uploadFile || !uploadFile.raw) {
      ElMessage.error('Please select a file to import')
      return
    }

    const formData = new FormData()
    formData.append('file', uploadFile.raw)

    // 显示加载Confirm
    const loading = ElLoading.service({
      lock: true,
      text: 'Importing data, please wait...',
      background: 'rgba(0, 0, 0, 0.7)'
    })

    try {
      const response = await importMaterials(formData)
      if (response && typeof response === 'object') {
        const { success_count = 0, error_count = 0, errors = [] } = response
        
        if (success_count > 0) {
          ElMessage.success(`Import complete: ${success_count} succeeded and ${error_count} failed`)
        } else {
          ElMessage.warning(`Import complete: ${success_count} succeeded and ${error_count} failed`)
        }
        
        // 显示错误详情
        errorList.value = errors.map(err => ({
          ...err,
          error: err.error.replace(/\[ErrorDetail\(string='(.+?)', code='(.+?)'\)\]/, '$1')
        }))
        
        if (success_count > 0) {
          emit('success')
        }
      } else {
        throw new Error('Invalid server response format')
      }
    } finally {
      loading.close()
    }
  } catch (error) {
    console.error('Import failed:')
    ElMessage.error('Import failed. Please check the file and try again.')
  }
}

const beforeUpload = (file) => {
  // 检查文件Type
  const validTypes = ['.xlsx', '.xls', '.csv']
  const isValidType = validTypes.some(type => file.name.toLowerCase().endsWith(type))
  if (!isValidType) {
    ElMessage.error('Only .xlsx, .xls, and .csv files are supported')
    return false
  }

  // 检查文件大小（10MB）
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('File size cannot exceed 10MB')
    return false
  }

  return true
}

// Reset上传状态
const resetUpload = () => {
  errorList.value = []
}

// 关闭对话框时Reset状态
const handleClose = () => {
  resetUpload()
}

// 模板下载
const downloadTemplate = () => {
  const link = document.createElement('a')
  link.href = '/template/materials_template.xlsx'  // 确保模板文件存在于public目录
  link.download = 'Material Import Template.xlsx'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

defineExpose({
  dialogVisible
})
</script>

<template>
  <el-dialog
    title="Import Material Data"
    v-model="dialogVisible"
    width="500px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="import-dialog">
      <el-upload
        class="upload-demo"
        drag
        :action="null"
        :auto-upload="false"
        :show-file-list="true"
        :on-change="handleImport"
        :before-upload="beforeUpload"
        :on-remove="resetUpload"
        accept=".xlsx,.xls,.csv"
        :limit="1"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          Drop file here or <em>click to upload</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            Only xlsx, xls, and csv files up to 10 MB are supported
            <el-button type="text" @click="downloadTemplate">Download Template</el-button>
          </div>
        </template>
      </el-upload>

      <!-- 错误信息展示 -->
      <div v-if="errorList.length > 0" class="error-list">
        <h4>Import Errors:</h4>
        <el-scrollbar height="200px">
          <ul>
            <li v-for="(error, index) in errorList" :key="index" class="error-item">
              <el-tag type="danger" size="small">Row {{ error.row }}</el-tag>
              Import validation failed for this row.
            </li>
          </ul>
        </el-scrollbar>
      </div>
    </div>
  </el-dialog>
</template>

<style scoped>
.import-dialog {
  .error-list {
    margin-top: 20px;
    border-top: 1px solid #eee;
    padding-top: 10px;

    h4 {
      margin: 0 0 10px 0;
      color: #f56c6c;
    }

    .error-item {
      margin: 5px 0;
      list-style: none;
      
      .el-tag {
        margin-right: 8px;
      }
    }
  }

  .el-upload__tip {
    .el-button {
      margin-left: 10px;
    }
  }
}
</style> 
