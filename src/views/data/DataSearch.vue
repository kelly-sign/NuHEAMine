<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getMaterials } from '@/api/material'
import { getProcesses } from '@/api/process'

const props = defineProps({
  type: {
    type: String,
    default: 'material'
  }
})

const loading = ref(false)
const materials = ref([])
const processes = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const activeTable = ref(props.type)
const searchForm = ref({
  material_name: '',
  fabrication: ''
})

const materialColumns = [
  { prop: 'id', label: 'ID', width: '80' },
  { prop: 'name', label: 'Material Name' },
  { prop: 'composition', label: 'Composition' },
  { prop: 'created_at', label: 'Creation Time', width: '180' },
  { prop: 'updated_at', label: 'Update Time', width: '180' }
]

const processColumns = [
  { prop: 'id', label: 'ID', width: '80' },
  { prop: 'method', label: 'Process Method' },
  { prop: 'temperature', label: 'Temperature' },
  { prop: 'duration', label: 'Duration' },
  { prop: 'cooling_method', label: 'Cooling Method' },
  { prop: 'created_at', label: 'Creation Time', width: '180' },
  { prop: 'updated_at', label: 'Update Time', width: '180' }
]

const fetchData = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      material_name: searchForm.value.material_name.trim(),
      fabrication: searchForm.value.fabrication.trim()
    }
    
    if (activeTable.value === 'material') {
      const response = await getMaterials(params)
      materials.value = response.data.results
      total.value = response.data.count
    } else {
      const response = await getProcesses(params)
      processes.value = response.data.results
      total.value = response.data.count
    }
  } catch (error) {
    console.error('Failed to fetch data:')
    ElMessage.error('Failed to load data')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

const handleReset = () => {
  searchForm.value.material_name = ''
  searchForm.value.fabrication = ''
  currentPage.value = 1
  fetchData()
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchData()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchData()
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="data-search">
    <el-card class="box-card">
      <template #header>
        <div class="clearfix">
          <span>{{ activeTable === 'material' ? 'Material Search' : 'Process Search' }}</span>
        </div>
      </template>
      
      <!-- Search form -->
      <el-form :model="searchForm" ref="searchForm" label-width="120px">
        <el-form-item label="Fabrication Process">
          <el-input v-model="searchForm.fabrication" placeholder="Please enter fabrication process"></el-input>
        </el-form-item>
        
        <!-- Homogenization -->
        <el-form-item label="Homogenization">
          <el-switch v-model="searchForm.homogenization"></el-switch>
          <template v-if="searchForm.homogenization">
            <el-form-item label="Homogenization Temperature">
              <el-input-number v-model="searchForm.homogenize_temp" :precision="1" :step="10"></el-input-number>
            </el-form-item>
            <el-form-item label="Homogenization Time">
              <el-input-number v-model="searchForm.homogenize_time" :precision="1" :step="0.5"></el-input-number>
            </el-form-item>
          </template>
        </el-form-item>

        <!-- Normalization -->
        <el-form-item label="Normalization">
          <el-switch v-model="searchForm.normalization"></el-switch>
          <template v-if="searchForm.normalization">
            <el-form-item label="Normalization Temperature">
              <el-input-number v-model="searchForm.normalize_temp" :precision="1" :step="10"></el-input-number>
            </el-form-item>
            <el-form-item label="Normalization Time">
              <el-input-number v-model="searchForm.normalize_time" :precision="1" :step="0.5"></el-input-number>
            </el-form-item>
          </template>
        </el-form-item>

        <!-- Annealing -->
        <el-form-item label="Annealing">
          <el-switch v-model="searchForm.annealing"></el-switch>
          <template v-if="searchForm.annealing">
            <el-form-item label="Annealing Temperature">
              <el-input-number v-model="searchForm.annealing_temp" :precision="1" :step="10"></el-input-number>
            </el-form-item>
            <el-form-item label="Annealing Time">
              <el-input-number v-model="searchForm.annealing_time" :precision="1" :step="0.5"></el-input-number>
            </el-form-item>
          </template>
        </el-form-item>

        <!-- Tempering -->
        <el-form-item label="Tempering">
          <el-switch v-model="searchForm.tempering"></el-switch>
          <template v-if="searchForm.tempering">
            <el-form-item label="Tempering Temperature">
              <el-input-number v-model="searchForm.tempering_temp" :precision="1" :step="10"></el-input-number>
            </el-form-item>
            <el-form-item label="Tempering Time">
              <el-input-number v-model="searchForm.tempering_time" :precision="1" :step="0.5"></el-input-number>
            </el-form-item>
          </template>
        </el-form-item>

        <!-- Quenching -->
        <el-form-item label="Quenching">
          <el-switch v-model="searchForm.quenching"></el-switch>
          <template v-if="searchForm.quenching">
            <el-form-item label="Quenching Type">
              <el-input v-model="searchForm.quenching_type"></el-input>
            </el-form-item>
            <el-form-item label="Quenching Temperature">
              <el-input-number v-model="searchForm.quenching_temp" :precision="1" :step="10"></el-input-number>
            </el-form-item>
          </template>
        </el-form-item>

        <!-- Rolling -->
        <el-form-item label="Rolling">
          <el-switch v-model="searchForm.rolling"></el-switch>
          <template v-if="searchForm.rolling">
            <el-form-item label="Rolling Temperature">
              <el-input-number v-model="searchForm.rolling_temp" :precision="1" :step="10"></el-input-number>
            </el-form-item>
            <el-form-item label="Reduction">
              <el-input-number v-model="searchForm.reduction" :precision="1" :step="0.5"></el-input-number>
            </el-form-item>
          </template>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleReset">Reset</el-button>
        </el-form-item>
      </el-form>

      <!-- Search结果表格 -->
      <el-table
        :data="activeTable === 'material' ? materials : processes"
        style="width: 100%"
        v-loading="loading"
        border
      >
        <el-table-column
          v-for="col in activeTable === 'material' ? materialColumns : processColumns"
          :key="col.prop"
          :prop="col.prop"
          :label="col.label"
          :width="col.width"
        />
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
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
  </div>
</template>

<style scoped>
.data-search {
  padding: 20px;
}
.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style> 
