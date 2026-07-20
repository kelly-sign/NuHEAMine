<template>
  <el-dialog
    :title="dialogTitle"
    v-model="dialogVisible"
    width="60%"
    :close-on-click-modal="false"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
    >
      <el-form-item label="Material Name" prop="name">
        <el-input v-model="form.name" placeholder="Please enter material name" />
      </el-form-item>

      <el-form-item label="Material Type" prop="type">
        <el-select v-model="form.type" placeholder="Please select a material type">
          <el-option label="Type1" value="type1" />
          <el-option label="Type2" value="type2" />
        </el-select>
      </el-form-item>

      <el-form-item label="Composition" prop="composition">
        <div v-for="(element, index) in elements" :key="index" class="composition-item">
          <el-input-number
            v-model="form.composition[element]"
            :min="0"
            :max="100"
            :precision="5"
            :step="0.1"
            controls-position="right"
          />
          <span class="element-label">{{ element }} (%)</span>
        </div>
        <div class="composition-total">
          Total: {{ compositionTotal }}%
          <el-tag 
            :type="compositionTotal === 100 ? 'success' : 'warning'"
            size="small"
          >
            {{ compositionTotal === 100 ? 'Valid composition' : 'Total must equal 100%' }}
          </el-tag>
        </div>
      </el-form-item>

      <el-form-item label="Properties" prop="properties">
        <div class="properties-list">
          <div v-for="(prop, key) in propertyFields" :key="key" class="property-item">
            <el-input-number
              v-model="form.properties[key]"
              :min="0"
              :precision="2"
              :step="1"
              controls-position="right"
            />
            <span class="property-label">{{ prop.label }} ({{ prop.unit }})</span>
          </div>
        </div>
      </el-form-item>

      <el-form-item label="Notes" prop="remarks">
        <el-input
          v-model="form.remarks"
          type="textarea"
          rows="3"
          placeholder="Enter notes"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleCancel">Cancel</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        Confirm
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createMaterial, updateMaterial } from '@/api/material'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  type: {
    type: String,
    default: 'create'
  },
  material: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const dialogTitle = computed(() => {
  return props.type === 'create' ? 'Add Material' : 'Edit Material'
})

const elements = ['Fe', 'Cr', 'Ni', 'Mn', 'Co']
const propertyFields = {
  hardness: { label: 'Hardness', unit: 'HV' },
  yieldStrength: { label: 'Yield Strength', unit: 'MPa' },
  tensileStrength: { label: 'Tensile Strength', unit: 'MPa' },
  elongation: { label: 'Elongation', unit: '%' }
}

const formRef = ref(null)
const loading = ref(false)

const form = ref({
  name: '',
  type: '',
  composition: elements.reduce((acc, element) => {
    acc[element] = 0
    return acc
  }, {}),
  properties: Object.keys(propertyFields).reduce((acc, key) => {
    acc[key] = 0
    return acc
  }, {}),
  remarks: ''
})

const rules = {
  name: [
    { required: true, message: 'Please enter material name', trigger: 'blur' },
    { min: 2, max: 50, message: 'Length must be between 2 and 50 characters', trigger: 'blur' }
  ],
  type: [
    { required: true, message: 'Please select a material type', trigger: 'change' }
  ]
}

const compositionTotal = computed(() => {
  return Object.values(form.value.composition).reduce((sum, val) => sum + val, 0)
})

watch(() => props.material, (newVal) => {
  if (newVal && Object.keys(newVal).length > 0) {
    form.value = {
      ...newVal,
      composition: { ...newVal.composition },
      properties: { ...newVal.properties }
    }
  }
}, { immediate: true })

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      if (Math.abs(compositionTotal.value - 100) > 0.01) {
        ElMessage.warning('The composition total must equal 100%')
        return
      }

      try {
        loading.value = true
        if (props.type === 'create') {
          await createMaterial(form.value)
          ElMessage.success('Added successfully')
        } else {
          await updateMaterial(props.material.id, form.value)
          ElMessage.success('Updated successfully')
        }
        emit('success')
        dialogVisible.value = false
      } catch (error) {
        console.error('Material operation failed:')
        ElMessage.error('Operation failed')
      } finally {
        loading.value = false
      }
    }
  })
}

const handleCancel = () => {
  dialogVisible.value = false
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

watch(dialogVisible, (val) => {
  if (!val) {
    resetForm()
  }
})
</script>

<style scoped>
.composition-item,
.property-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.element-label,
.property-label {
  margin-left: 10px;
  width: 100px;
}

.composition-total {
  margin-top: 10px;
  color: #666;
}

.properties-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}
</style> 
