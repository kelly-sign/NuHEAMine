<template>
  <div class="advanced-search">
    <el-form :model="searchForm" label-width="120px">
      <div v-for="(condition, index) in searchForm.conditions" :key="index" class="condition-item">
        <el-form-item :label="'Condition ' + (index + 1)">
          <div class="condition-content">
            <el-select v-model="condition.field" placeholder="Select a field" style="width: 150px">
              <el-option label="Material Name" value="material_name"></el-option>
              <el-option v-for="element in elements" :key="element" 
                :label="'Element ' + element.toUpperCase()" 
                :value="'composition_' + element">
              </el-option>
            </el-select>
            
            <el-select v-model="condition.operator" placeholder="Select an operator" style="width: 120px; margin-left: 10px">
              <el-option label="Contains" value="contains"></el-option>
              <el-option label="Equals" value="equals"></el-option>
              <el-option label="Range" value="range"></el-option>
            </el-select>

            <template v-if="condition.operator === 'range'">
              <el-input-number
                v-model="condition.value[0]"
                :min="0"
                :max="100"
                :precision="2"
                :step="0.1"
                style="width: 120px; margin-left: 10px"
              ></el-input-number>
              <span style="margin: 0 10px">to</span>
              <el-input-number
                v-model="condition.value[1]"
                :min="0"
                :max="100"
                :precision="2"
                :step="0.1"
                style="width: 120px"
              ></el-input-number>
              <span style="margin-left: 10px">%</span>
            </template>
            
            <template v-else>
              <el-input
                v-model="condition.value"
                :placeholder="condition.operator === 'contains' ? 'Enter a keyword' : 'Enter a value'"
                style="width: 200px; margin-left: 10px"
              ></el-input>
            </template>

            <el-button
              type="danger"
              icon="el-icon-delete"
              circle
              @click="removeCondition(index)"
              style="margin-left: 10px"
            ></el-button>
          </div>
        </el-form-item>
      </div>

      <el-form-item>
        <el-button type="primary" @click="addCondition">Add Condition</el-button>
        <el-button @click="reset">Reset</el-button>
        <el-button type="success" @click="handleSearch">Search</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { reactive } from 'vue'

export default {
  name: 'AdvancedSearch',
  setup(props, { emit }) {
    const elements = [
      'al', 'c', 'co', 'cr', 'cu', 'fe', 'hf', 'mg', 'mn', 'mo',
      'n', 'nb', 'ni', 'sc', 'si', 'sn', 'ta', 'ti', 'v', 'w', 'y', 'zn', 'zr'
    ]

    const searchForm = reactive({
      conditions: []
    })

    const addCondition = () => {
      searchForm.conditions.push({
        field: '',
        operator: '',
        value: ''
      })
    }

    const removeCondition = (index) => {
      searchForm.conditions.splice(index, 1)
    }

    const reset = () => {
      searchForm.conditions = []
    }

    const handleSearch = () => {
      emit('search', searchForm.conditions)
    }

    return {
      elements,
      searchForm,
      addCondition,
      removeCondition,
      reset,
      handleSearch
    }
  }
}
</script>

<style scoped>
.advanced-search {
  padding: 20px;
}

.condition-item {
  margin-bottom: 20px;
}

.condition-content {
  display: flex;
  align-items: center;
}
</style> 
