<template>
  <el-form :inline="true" :model="form" class="search-form">
    <slot :form="form"></slot>
    
    <el-form-item>
      <el-button type="primary" @click="handleSearch">
        Search
      </el-button>
      <el-button @click="handleReset">
        Reset
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { reactive } from 'vue'

const props = defineProps({
  initialValues: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['search', 'reset'])

const form = reactive({
  ...props.initialValues
})

const handleSearch = () => {
  emit('search', { ...form })
}

const handleReset = () => {
  Object.keys(form).forEach(key => {
    form[key] = props.initialValues[key] || ''
  })
  emit('reset')
}
</script>

<style scoped>
.search-form {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}
</style> 