<template>
  <div class="page-container">
    <div class="toolbar-container">
      <div class="search-container">
        <el-row :gutter="10" class="filter-row">
          <el-col :span="4">
            <el-input
              v-model="filters.search"
              placeholder="Hardening ID / phase"
              clearable
              @keyup.enter="handleSearch"
              @clear="handleSearch"
            />
          </el-col>
          <el-col :span="4">
            <el-input
              v-model="filters.material_id"
              placeholder="Material ID"
              clearable
              @keyup.enter="handleSearch"
              @clear="handleSearch"
            />
          </el-col>
          <el-col :span="4">
            <el-input
              v-model="filters.process_id"
              placeholder="Process ID"
              clearable
              @keyup.enter="handleSearch"
              @clear="handleSearch"
            />
          </el-col>
          <el-col :span="4">
            <el-input
              v-model="filters.irradiat_id"
              placeholder="Irradiation ID"
              clearable
              @keyup.enter="handleSearch"
              @clear="handleSearch"
            />
          </el-col>
          <el-col :span="4">
            <el-input
              v-model="filters.document_id"
              placeholder="Document ID"
              clearable
              @keyup.enter="handleSearch"
              @clear="handleSearch"
            />
          </el-col>
          <el-col :span="4">
            <el-input
              v-model="filters.phase_structure"
              placeholder="Phase structure"
              clearable
              @keyup.enter="handleSearch"
              @clear="handleSearch"
            />
          </el-col>
        </el-row>

        <el-row :gutter="10" class="filter-row">
          <el-col :span="6">
            <div class="range-filter">
              <span class="range-label">Pre HV</span>
              <el-input v-model="filters.pre_hv_min" type="number" placeholder="Min" clearable />
              <span class="range-separator">-</span>
              <el-input v-model="filters.pre_hv_max" type="number" placeholder="Max" clearable />
            </div>
          </el-col>
          <el-col :span="6">
            <div class="range-filter">
              <span class="range-label">Post HV</span>
              <el-input v-model="filters.post_hv_min" type="number" placeholder="Min" clearable />
              <span class="range-separator">-</span>
              <el-input v-model="filters.post_hv_max" type="number" placeholder="Max" clearable />
            </div>
          </el-col>
          <el-col :span="6">
            <div class="range-filter">
              <span class="range-label">Delta HV</span>
              <el-input v-model="filters.delta_hv_min" type="number" placeholder="Min" clearable />
              <span class="range-separator">-</span>
              <el-input v-model="filters.delta_hv_max" type="number" placeholder="Max" clearable />
            </div>
          </el-col>
          <el-col :span="6" class="search-actions">
            <el-button type="primary" @click="handleSearch">Search</el-button>
            <el-button @click="resetFilters">Reset</el-button>
          </el-col>
        </el-row>
      </div>

      <div class="button-container">
        <el-button type="primary" @click="showAddDialog">Add</el-button>
        <el-button type="danger" :disabled="selectedRows.length === 0" @click="batchDelete">
          Batch Delete
        </el-button>
        <el-button type="success" @click="showImportDialog">Import</el-button>
        <el-button type="info" @click="exportData">Export</el-button>
      </div>
    </div>

    <el-table
      v-loading="loading"
      :data="tableData"
      row-key="hardening_id"
      border
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="hardening_id" label="Hardening ID" width="115" />
      <el-table-column label="Material" min-width="180">
        <template #default="scope">
          <div>ID: {{ scope.row.material?.material_id }}</div>
          <div>{{ scope.row.material?.material_name }}</div>
        </template>
      </el-table-column>
      <el-table-column label="Process" min-width="150">
        <template #default="scope">
          <div>ID: {{ scope.row.process?.process_id }}</div>
          <div>{{ scope.row.process?.fabrication }}</div>
        </template>
      </el-table-column>
      <el-table-column label="Irradiation" min-width="150">
        <template #default="scope">
          <div>ID: {{ scope.row.irradiat?.irradiat_id }}</div>
          <div>{{ scope.row.irradiat?.irradiat_type }}</div>
        </template>
      </el-table-column>
      <el-table-column label="Reference" min-width="210">
        <template #default="scope">
          <div>ID: {{ scope.row.document?.document_id }}</div>
          <div>{{ scope.row.document?.doc_name }}</div>
        </template>
      </el-table-column>
      <el-table-column prop="phase_structure" label="Phase Structure" min-width="130" />
      <el-table-column prop="pre_hv" label="Pre HV" width="100" />
      <el-table-column prop="post_hv" label="Post HV" width="100" />
      <el-table-column prop="delta_hv" label="Delta HV" width="105" />
      <el-table-column prop="entry_time" label="Entry Time" width="180" />
      <el-table-column prop="modify_time" label="Modify Time" width="180" />
      <el-table-column label="Actions" width="155" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="showEditDialog(scope.row)">Edit</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.row.hardening_id)">
            Delete
          </el-button>
        </template>
      </el-table-column>
    </el-table>

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

    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? 'Add Irradiation Hardening' : 'Edit Irradiation Hardening'"
      width="620px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="165px">
        <el-form-item label="Material" prop="material_id">
          <el-select v-model="formData.material_id" filterable placeholder="Select a material" class="full-width">
            <el-option
              v-for="item in materialOptions"
              :key="item.material_id"
              :label="`${item.material_id} - ${item.material_name}`"
              :value="item.material_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Process" prop="process_id">
          <el-select v-model="formData.process_id" filterable placeholder="Select a process" class="full-width">
            <el-option
              v-for="item in processOptions"
              :key="item.process_id"
              :label="`${item.process_id} - ${item.fabrication}`"
              :value="item.process_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Irradiation Condition" prop="irradiat_id">
          <el-select
            v-model="formData.irradiat_id"
            filterable
            placeholder="Select an irradiation condition"
            class="full-width"
          >
            <el-option
              v-for="item in irradiatOptions"
              :key="item.irradiat_id"
              :label="`${item.irradiat_id} - ${item.irradiat_type || 'No type'}`"
              :value="item.irradiat_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Reference Document" prop="document_id">
          <el-select v-model="formData.document_id" filterable placeholder="Select a document" class="full-width">
            <el-option
              v-for="item in documentOptions"
              :key="item.document_id"
              :label="`${item.document_id} - ${item.doc_name}`"
              :value="item.document_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Phase Structure" prop="phase_structure">
          <el-input
            v-model="formData.phase_structure"
            maxlength="100"
            show-word-limit
            placeholder="e.g. FCC, BCC"
          />
        </el-form-item>
        <el-form-item label="Pre-irradiation HV" prop="pre_hv">
          <el-input-number v-model="formData.pre_hv" :controls="false" class="full-width" />
        </el-form-item>
        <el-form-item label="Post-irradiation HV" prop="post_hv">
          <el-input-number v-model="formData.post_hv" :controls="false" class="full-width" />
        </el-form-item>
        <el-form-item label="Hardness Change (HV)" prop="delta_hv">
          <el-input-number v-model="formData.delta_hv" :controls="false" class="full-width" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">Confirm</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="importDialogVisible" title="Import Irradiation Hardening Data" width="560px">
      <el-upload
        action="#"
        drag
        accept=".csv,.xlsx,.xls"
        :auto-upload="false"
        :limit="1"
        :file-list="uploadFileList"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
      >
        <div class="upload-text">Drop a CSV or Excel file here, or click to select.</div>
        <template #tip>
          <div class="el-upload__tip">
            Required columns: material_id, process_id, irradiat_id and document_id.<br>
            Optional columns: phase_structure, pre_hv, post_hv and delta_hv.<br>
            <el-link type="primary" :underline="false" @click.stop="downloadTemplate">
              Download CSV template
            </el-link>
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">Cancel</el-button>
        <el-button type="primary" :loading="importing" @click="submitImport">Import</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  batchDeleteHardenings,
  createHardening,
  deleteHardening,
  exportHardenings,
  getHardeningDetail,
  getHardeningDocumentOptions,
  getHardeningIrradiationOptions,
  getHardeningList,
  getHardeningMaterialOptions,
  getHardeningProcessOptions,
  importHardenings,
  rangeQueryHardenings,
  updateHardening
} from '@/api/hardening'

const createEmptyForm = () => ({
  material_id: null,
  process_id: null,
  irradiat_id: null,
  document_id: null,
  phase_structure: '',
  pre_hv: null,
  post_hv: null,
  delta_hv: null
})

const createEmptyFilters = () => ({
  search: '',
  material_id: '',
  process_id: '',
  irradiat_id: '',
  document_id: '',
  phase_structure: '',
  pre_hv_min: '',
  pre_hv_max: '',
  post_hv_min: '',
  post_hv_max: '',
  delta_hv_min: '',
  delta_hv_max: ''
})

export default {
  name: 'HardeningList',
  setup() {
    const tableData = ref([])
    const loading = ref(false)
    const selectedRows = ref([])
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalItems = ref(0)
    const filters = reactive(createEmptyFilters())

    const dialogVisible = ref(false)
    const dialogType = ref('add')
    const currentId = ref(null)
    const formRef = ref(null)
    const formData = reactive(createEmptyForm())
    const submitting = ref(false)

    const materialOptions = ref([])
    const processOptions = ref([])
    const irradiatOptions = ref([])
    const documentOptions = ref([])

    const importDialogVisible = ref(false)
    const uploadFileList = ref([])
    const uploadFile = ref(null)
    const importing = ref(false)

    const validateNumber = (rule, value, callback) => {
      if (value === null || value === '') {
        callback()
        return
      }
      if (!Number.isFinite(Number(value))) {
        callback(new Error('Please enter a valid number'))
        return
      }
      callback()
    }

    const rules = {
      material_id: [{ required: true, message: 'Please select a material', trigger: 'change' }],
      process_id: [{ required: true, message: 'Please select a process', trigger: 'change' }],
      irradiat_id: [{ required: true, message: 'Please select an irradiation condition', trigger: 'change' }],
      document_id: [{ required: true, message: 'Please select a reference document', trigger: 'change' }],
      pre_hv: [{ validator: validateNumber, trigger: 'blur' }],
      post_hv: [{ validator: validateNumber, trigger: 'blur' }],
      delta_hv: [{ validator: validateNumber, trigger: 'blur' }]
    }

    const unpackPage = (data) => {
      if (Array.isArray(data)) {
        return { results: data, count: data.length }
      }
      return {
        results: data?.results || [],
        count: data?.count ?? data?.results?.length ?? 0
      }
    }

    const hasRangeFilter = () => [
      filters.pre_hv_min,
      filters.pre_hv_max,
      filters.post_hv_min,
      filters.post_hv_max,
      filters.delta_hv_min,
      filters.delta_hv_max
    ].some(value => value !== '' && value !== null)

    const loadData = async () => {
      loading.value = true
      try {
        let response
        if (hasRangeFilter()) {
          const payload = {
            material_id: filters.material_id || undefined,
            process_id: filters.process_id || undefined,
            irradiat_id: filters.irradiat_id || undefined,
            document_id: filters.document_id || undefined,
            phase_structure: filters.phase_structure || undefined,
            pre_hv_min: filters.pre_hv_min === '' ? undefined : filters.pre_hv_min,
            pre_hv_max: filters.pre_hv_max === '' ? undefined : filters.pre_hv_max,
            post_hv_min: filters.post_hv_min === '' ? undefined : filters.post_hv_min,
            post_hv_max: filters.post_hv_max === '' ? undefined : filters.post_hv_max,
            delta_hv_min: filters.delta_hv_min === '' ? undefined : filters.delta_hv_min,
            delta_hv_max: filters.delta_hv_max === '' ? undefined : filters.delta_hv_max
          }
          response = await rangeQueryHardenings(payload, {
            page: currentPage.value,
            page_size: pageSize.value
          })
        } else {
          response = await getHardeningList({
            page: currentPage.value,
            page_size: pageSize.value,
            search: filters.search || undefined,
            material_id: filters.material_id || undefined,
            process_id: filters.process_id || undefined,
            irradiat_id: filters.irradiat_id || undefined,
            document_id: filters.document_id || undefined,
            phase_structure: filters.phase_structure || undefined
          })
        }
        const page = unpackPage(response.data)
        tableData.value = page.results
        totalItems.value = page.count
      } catch {
        ElMessage.error('Failed to load irradiation hardening data')
      } finally {
        loading.value = false
      }
    }

    const fetchAllOptions = async (fetcher, idField) => {
      const firstResponse = await fetcher({ page: 1, page_size: 100 })
      const firstPage = unpackPage(firstResponse.data)
      let results = firstPage.results
      const totalPages = Math.ceil(firstPage.count / 100)
      if (totalPages > 1 && results.length < firstPage.count) {
        const requests = []
        for (let page = 2; page <= totalPages; page += 1) {
          requests.push(fetcher({ page, page_size: 100 }))
        }
        const responses = await Promise.all(requests)
        responses.forEach(response => {
          results = results.concat(unpackPage(response.data).results)
        })
      }
      const unique = new Map()
      results.forEach(item => unique.set(item[idField], item))
      return Array.from(unique.values())
    }

    const loadOptions = async () => {
      const loaders = [
        fetchAllOptions(getHardeningMaterialOptions, 'material_id'),
        fetchAllOptions(getHardeningProcessOptions, 'process_id'),
        fetchAllOptions(getHardeningIrradiationOptions, 'irradiat_id'),
        fetchAllOptions(getHardeningDocumentOptions, 'document_id')
      ]
      const results = await Promise.allSettled(loaders)
      if (results[0].status === 'fulfilled') materialOptions.value = results[0].value
      if (results[1].status === 'fulfilled') processOptions.value = results[1].value
      if (results[2].status === 'fulfilled') irradiatOptions.value = results[2].value
      if (results[3].status === 'fulfilled') documentOptions.value = results[3].value
      if (results.some(result => result.status === 'rejected')) {
        ElMessage.warning('Some form options could not be loaded')
      }
    }

    const handleSearch = () => {
      currentPage.value = 1
      loadData()
    }

    const resetFilters = () => {
      Object.assign(filters, createEmptyFilters())
      currentPage.value = 1
      loadData()
    }

    const handleSelectionChange = rows => {
      selectedRows.value = rows
    }

    const handleSizeChange = size => {
      pageSize.value = size
      currentPage.value = 1
      loadData()
    }

    const handleCurrentChange = page => {
      currentPage.value = page
      loadData()
    }

    const resetForm = () => {
      Object.assign(formData, createEmptyForm())
      if (formRef.value) formRef.value.clearValidate()
    }

    const showAddDialog = () => {
      dialogType.value = 'add'
      currentId.value = null
      resetForm()
      dialogVisible.value = true
    }

    const showEditDialog = async row => {
      dialogType.value = 'edit'
      currentId.value = row.hardening_id
      try {
        const response = await getHardeningDetail(row.hardening_id)
        const data = response.data
        Object.assign(formData, {
          material_id: data.material?.material_id ?? data.material_id,
          process_id: data.process?.process_id ?? data.process_id,
          irradiat_id: data.irradiat?.irradiat_id ?? data.irradiat_id,
          document_id: data.document?.document_id ?? data.document_id,
          phase_structure: data.phase_structure || '',
          pre_hv: data.pre_hv,
          post_hv: data.post_hv,
          delta_hv: data.delta_hv
        })
        dialogVisible.value = true
      } catch {
        ElMessage.error('Failed to load hardening details')
      }
    }

    const normalizeOptionalNumber = value => (
      value === null || value === '' ? null : Number(value)
    )

    const submitForm = async () => {
      if (!formRef.value) return
      const valid = await formRef.value.validate().catch(() => false)
      if (!valid) return

      submitting.value = true
      try {
        const payload = {
          material_id: Number(formData.material_id),
          process_id: Number(formData.process_id),
          irradiat_id: Number(formData.irradiat_id),
          document_id: Number(formData.document_id),
          phase_structure: formData.phase_structure?.trim() || null,
          pre_hv: normalizeOptionalNumber(formData.pre_hv),
          post_hv: normalizeOptionalNumber(formData.post_hv),
          delta_hv: normalizeOptionalNumber(formData.delta_hv)
        }
        if (dialogType.value === 'add') {
          await createHardening(payload)
          ElMessage.success('Irradiation hardening record added')
        } else {
          await updateHardening(currentId.value, payload)
          ElMessage.success('Irradiation hardening record updated')
        }
        dialogVisible.value = false
        await loadData()
      } catch {
        // The shared request interceptor displays the server validation error.
      } finally {
        submitting.value = false
      }
    }

    const handleDelete = async id => {
      try {
        await ElMessageBox.confirm('Delete this irradiation hardening record?', 'Confirm', {
          confirmButtonText: 'Delete',
          cancelButtonText: 'Cancel',
          type: 'warning'
        })
        await deleteHardening(id)
        ElMessage.success('Record deleted')
        await loadData()
      } catch {
        // Cancelling is expected; request failures are handled by the shared interceptor.
      }
    }

    const batchDelete = async () => {
      const ids = selectedRows.value.map(row => row.hardening_id)
      if (ids.length === 0) return
      try {
        await ElMessageBox.confirm(`Delete ${ids.length} selected record(s)?`, 'Confirm', {
          confirmButtonText: 'Delete',
          cancelButtonText: 'Cancel',
          type: 'warning'
        })
        await batchDeleteHardenings(ids)
        ElMessage.success('Selected records deleted')
        await loadData()
      } catch {
        // Cancelling is expected; request failures are handled by the shared interceptor.
      }
    }

    const downloadBlob = (blob, filename) => {
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    }

    const exportData = async () => {
      try {
        const propertyIds = selectedRows.value.map(row => row.hardening_id)
        const response = await exportHardenings({
          format: 'excel',
          property_ids: propertyIds
        })
        downloadBlob(
          new Blob([response.data], {
            type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
          }),
          `hardening_data_${new Date().toISOString().slice(0, 10)}.xlsx`
        )
        ElMessage.success('Export completed')
      } catch {
        // The shared request interceptor displays export errors.
      }
    }

    const showImportDialog = () => {
      uploadFile.value = null
      uploadFileList.value = []
      importDialogVisible.value = true
    }

    const handleFileChange = file => {
      uploadFile.value = file.raw
      uploadFileList.value = [file]
    }

    const handleFileRemove = () => {
      uploadFile.value = null
      uploadFileList.value = []
    }

    const downloadTemplate = () => {
      const headers = [
        'material_id',
        'process_id',
        'irradiat_id',
        'document_id',
        'phase_structure',
        'pre_hv',
        'post_hv',
        'delta_hv'
      ]
      downloadBlob(
        new Blob([`\uFEFF${headers.join(',')}\n`], { type: 'text/csv;charset=utf-8' }),
        'hardening_import_template.csv'
      )
    }

    const submitImport = async () => {
      if (!uploadFile.value) {
        ElMessage.warning('Please select a file first')
        return
      }
      importing.value = true
      try {
        const formDataPayload = new FormData()
        formDataPayload.append('file', uploadFile.value)
        const response = await importHardenings(formDataPayload)
        const result = response.data
        if (result.success_count > 0) {
          ElMessage.success(
            `Imported ${result.success_count} record(s); ${result.error_count || 0} failed`
          )
          importDialogVisible.value = false
          await loadData()
        } else {
          ElMessage.warning('No records were imported. Please check the file contents.')
        }
      } catch {
        // The shared request interceptor displays import errors.
      } finally {
        importing.value = false
      }
    }

    onMounted(() => {
      loadData()
      loadOptions()
    })

    return {
      tableData,
      loading,
      selectedRows,
      currentPage,
      pageSize,
      totalItems,
      filters,
      dialogVisible,
      dialogType,
      formRef,
      formData,
      rules,
      submitting,
      materialOptions,
      processOptions,
      irradiatOptions,
      documentOptions,
      importDialogVisible,
      uploadFileList,
      importing,
      handleSearch,
      resetFilters,
      handleSelectionChange,
      handleSizeChange,
      handleCurrentChange,
      showAddDialog,
      showEditDialog,
      submitForm,
      handleDelete,
      batchDelete,
      exportData,
      showImportDialog,
      handleFileChange,
      handleFileRemove,
      downloadTemplate,
      submitImport
    }
  }
}
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.toolbar-container {
  margin-bottom: 20px;
}

.filter-row {
  margin-bottom: 10px;
}

.button-container {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

.range-filter {
  display: flex;
  align-items: center;
  gap: 6px;
}

.range-label {
  min-width: 62px;
  white-space: nowrap;
}

.range-separator {
  color: #909399;
}

.search-actions {
  display: flex;
  justify-content: flex-end;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.full-width {
  width: 100%;
}

.upload-text {
  color: #606266;
}

.el-upload__tip {
  line-height: 1.7;
  margin-top: 10px;
}
</style>
