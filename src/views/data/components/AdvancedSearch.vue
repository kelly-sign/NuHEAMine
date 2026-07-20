<template>
  <div class="advanced-search">
    <el-form :model="searchForm" label-width="100px">
      <el-form-item label="Search Conditions">
        <div v-for="(condition, index) in searchForm.conditions" :key="index" class="condition-item">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-select v-model="condition.field" placeholder="Select a field">
                <el-option label="Material Name" value="name" />
                <el-option label="Material Type" value="type" />
                <el-option label="Composition" value="composition" />
                <el-option label="Property" value="properties" />
              </el-select>
            </el-col>
            
            <el-col :span="6" v-if="condition.field === 'properties'">
              <el-select v-model="condition.property_name" placeholder="Select a property">
                <el-option 
                  v-for="prop in propertyNames" 
                  :key="prop" 
                  :label="prop" 
                  :value="prop" 
                />
              </el-select>
            </el-col>
            
            <el-col :span="6">
              <el-select v-model="condition.operator" placeholder="Select an operator">
                <el-option label="Contains" value="contains" v-if="condition.field === 'name'" />
                <el-option label="Equals" value="equals" v-if="condition.field === 'name'" />
                <el-option label="Range" value="range" v-if="condition.field === 'composition' || condition.field === 'properties'" />
              </el-select>
            </el-col>
            
            <el-col :span="6">
              <template v-if="condition.operator === 'range'">
                <el-input-number 
                  v-model="condition.value[0]" 
                  placeholder="Min" 
                  :min="0"
                />
                <el-input-number 
                  v-model="condition.value[1]" 
                  placeholder="Max" 
                  :min="0"
                />
              </template>
              <template v-else>
                <el-input v-model="condition.value" placeholder="Enter a value" />
              </template>
            </el-col>
            
            <el-col :span="2">
              <el-button type="danger" @click="removeCondition(index)">
                Delete
              </el-button>
            </el-col>
          </el-row>
        </div>
        
        <el-button type="primary" @click="addCondition">
          Add Condition
        </el-button>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="handleSearch">
          Search
        </el-button>
        <el-button @click="handleReset">
          Reset
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getPropertyNames } from '@/api/material'

const searchForm = ref({
  conditions: []
})

const propertyNames = ref([])

// 获取性能指标列表
const fetchPropertyNames = async () => {
  try {
    const res = await getPropertyNames()
    propertyNames.value = res.data
  } catch (error) {
    ElMessage.error('Failed to load the property list')
  }
}

// AddSearch条件
const addCondition = () => {
  searchForm.value.conditions.push({
    field: '',
    operator: '',
    value: '',
    property_name: ''
  })
}

// DeleteSearch条件
const removeCondition = (index) => {
  searchForm.value.conditions.splice(index, 1)
}

// 处理Search
const handleSearch = () => {
  // 验证Search条件
  const validConditions = searchForm.value.conditions.filter(condition => {
    if (!condition.field || !condition.operator) return false
    if (condition.field === 'properties' && !condition.property_name) return false
    if (!condition.value) return false
    if (condition.operator === 'range' && (!condition.value[0] || !condition.value[1])) return false
    return true
  })
  
  if (validConditions.length === 0) {
    ElMessage.warning('Please add at least one valid search condition')
    return
  }
  
  // 触发Search事件
  emit('search', {
    conditions: validConditions
  })
}

// 处理Reset
const handleReset = () => {
  searchForm.value.conditions = []
  emit('reset')
}

// 定义事件
const emit = defineEmits(['search', 'reset'])

onMounted(() => {
  fetchPropertyNames()
})
</script>

<style scoped>
.advanced-search {
  padding: 20px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.condition-item {
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.el-input-number {
  width: 100px;
  margin-right: 10px;
}
</style> 
