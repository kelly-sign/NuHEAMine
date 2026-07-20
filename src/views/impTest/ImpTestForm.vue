<template>
  <el-dialog
    :title="dialogTitle"
    :modelValue="visible"
    @update:modelValue="$emit('update:visible', $event)"
    width="500px"
    :close-on-click-modal="false"
    :before-close="handleClose"
  >
    <el-form
      ref="form"
      :model="form"
      :rules="rules"
      label-width="110px"
      size="small"
    >
      <el-form-item label="Material ID" prop="material_id">
        <el-input v-model="form.material_id" placeholder="Please enter material ID"></el-input>
      </el-form-item>
      <el-form-item label="Process ID" prop="process_id">
        <el-input v-model="form.process_id" placeholder="Please enter process ID"></el-input>
      </el-form-item>
      <el-form-item label="Test Temperature" prop="impact_temp">
        <el-input-number v-model="form.impact_temp" :controls="false" :precision="2" placeholder="Enter the test temperature"></el-input-number>
        <span class="unit">℃</span>
      </el-form-item>
      <el-form-item label="Impact Type" prop="impact_type">
        <el-select v-model="form.impact_type" placeholder="Select an impact type" style="width: 100%">
          <el-option label="Charpy Impact" value="夏比冲击"></el-option>
          <el-option label="Izod Impact" value="悬臂梁冲击"></el-option>
          <el-option label="Drop-Weight Impact" value="落锤冲击"></el-option>
          <el-option label="Other" value="其他"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="Impact Energy" prop="impact_energy">
        <el-input-number v-model="form.impact_energy" :controls="false" :precision="2" placeholder="Enter the impact energy"></el-input-number>
        <span class="unit">J</span>
      </el-form-item>
      <el-form-item label="Absorbed Energy" prop="absorbed_energy">
        <el-input-number v-model="form.absorbed_energy" :controls="false" :precision="2" placeholder="Enter the absorbed energy"></el-input-number>
        <span class="unit">J</span>
      </el-form-item>
      <el-form-item label="Impact Toughness" prop="impact_tough_value">
        <el-input-number v-model="form.impact_tough_value" :controls="false" :precision="2" placeholder="Enter the impact toughness"></el-input-number>
        <span class="unit">J/cm²</span>
      </el-form-item>
      <el-form-item label="Fracture Type" prop="fracture_type">
        <el-select v-model="form.fracture_type" placeholder="Select a fracture type" style="width: 100%">
          <el-option label="Ductile Fracture" value="韧性断裂"></el-option>
          <el-option label="Brittle Fracture" value="脆性断裂"></el-option>
          <el-option label="Mixed Fracture" value="混合断裂"></el-option>
          <el-option label="Other" value="其他"></el-option>
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">Cancel</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">Confirm</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script>
import { addImpTest, updateImpTest } from '@/api/impTest'
import { ElMessage } from 'element-plus'

export default {
  name: 'ImpTestForm',
  props: {
    visible: {
      type: Boolean,
      required: true
    },
    type: {
      type: String,
      default: 'add'
    },
    impTest: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      loading: false,
      form: {
        material_id: '',
        process_id: '',
        impact_temp: null,
        impact_type: '',
        impact_energy: null,
        absorbed_energy: null,
        impact_tough_value: null,
        fracture_type: ''
      },
      rules: {
        material_id: [
          { required: true, message: 'Please enter material ID', trigger: 'blur' },
          { pattern: /^\d+$/, message: 'Material ID must be numeric', trigger: 'blur' }
        ],
        process_id: [
          { required: true, message: 'Please enter process ID', trigger: 'blur' },
          { pattern: /^\d+$/, message: 'Process ID must be numeric', trigger: 'blur' }
        ],
        impact_temp: [
          { required: false, message: 'Please enter the test temperature', trigger: 'blur' }
        ],
        impact_type: [
          { required: false, message: 'Please select an impact type', trigger: 'change' }
        ],
        impact_energy: [
          { required: false, message: 'Please enter the impact energy', trigger: 'blur' }
        ]
      }
    }
  },
  computed: {
    dialogTitle() {
      return this.type === 'add' ? 'Add Impact Test Data' : 'Edit Impact Test Data'
    }
  },
  watch: {
    impTest: {
      handler(val) {
        if (this.type === 'edit' && val) {
          this.form = {
            material_id: val.material_id || (val.material && val.material.material_id) || '',
            process_id: val.process_id || (val.process && val.process.process_id) || '',
            impact_temp: val.impact_temp,
            impact_type: val.impact_type,
            impact_energy: val.impact_energy,
            absorbed_energy: val.absorbed_energy,
            impact_tough_value: val.impact_tough_value,
            fracture_type: val.fracture_type
          }
        }
      },
      immediate: true
    },
    visible(val) {
      if (!val) {
        this.resetForm()
      }
    }
  },
  methods: {
    async handleSubmit() {
      this.$refs.form.validate(async valid => {
        if (!valid) return

        try {
          this.loading = true
          const formData = { ...this.form }
          
          // 确保字段Type正确
          if (formData.material_id) {
            formData.material_id = parseInt(formData.material_id)
          }
          if (formData.process_id) {
            formData.process_id = parseInt(formData.process_id)
          }

          let response
          if (this.type === 'add') {
            response = await addImpTest(formData)
          } else {
            response = await updateImpTest(this.impTest.impact_id, formData)
          }

          ElMessage.success(`${this.type === 'add' ? 'Added' : 'Updated'} successfully`)
          this.$emit('success', response.data)
          this.handleClose()
        } catch (error) {
          console.error('Submission failed:')
          ElMessage.error(`Failed to ${this.type === 'add' ? 'add' : 'update'} the impact test data`)
        } finally {
          this.loading = false
        }
      })
    },
    handleClose() {
      this.$emit('update:visible', false)
    },
    resetForm() {
      if (this.$refs.form) {
        this.$refs.form.resetFields()
      }
      this.form = {
        material_id: '',
        process_id: '',
        impact_temp: null,
        impact_type: '',
        impact_energy: null,
        absorbed_energy: null,
        impact_tough_value: null,
        fracture_type: ''
      }
    }
  }
}
</script>

<style scoped>
.unit {
  margin-left: 5px;
  color: #606266;
}
</style> 
