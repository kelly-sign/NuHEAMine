<template>
  <div class="process-list">
    <el-card class="box-card">
      <template #header>
        <div class="clearfix">
          <span>Process List</span>
          <el-button style="float: right; padding: 3px 0" type="text" @click="handleAdd">Add Process</el-button>
        </div>
      </template>
      
      <!-- Search bar -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="Fabrication Process">
          <el-input v-model="searchForm.fabrication" placeholder="Please enter fabrication process" clearable></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="resetSearch">Reset</el-button>
        </el-form-item>
      </el-form>

      <!-- Data table -->
      <el-table
        :data="tableData"
        style="width: 100%"
        v-loading="loading"
        border
      >
        <el-table-column prop="process_id" label="Process ID" width="80"></el-table-column>
        <el-table-column prop="fabrication" label="Fabrication Process" width="120"></el-table-column>
        <el-table-column label="Homogenization" width="100">
          <template #default="{ row }">
            <el-tag :type="row.homogenization ? 'success' : 'info'">
              {{ row.homogenization ? 'Yes' : 'No' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Normalization" width="100">
          <template #default="{ row }">
            <el-tag :type="row.normalization ? 'success' : 'info'">
              {{ row.normalization ? 'Yes' : 'No' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Annealing" width="100">
          <template #default="{ row }">
            <el-tag :type="row.annealing ? 'success' : 'info'">
              {{ row.annealing ? 'Yes' : 'No' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Tempering" width="100">
          <template #default="{ row }">
            <el-tag :type="row.tempering ? 'success' : 'info'">
              {{ row.tempering ? 'Yes' : 'No' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Quenching" width="100">
          <template #default="{ row }">
            <el-tag :type="row.quenching ? 'success' : 'info'">
              {{ row.quenching ? 'Yes' : 'No' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Rolling" width="100">
          <template #default="{ row }">
            <el-tag :type="row.rolling ? 'success' : 'info'">
              {{ row.rolling ? 'Yes' : 'No' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="entry_time" label="Entry Time" width="180">
          <template #default="{ row }">
            {{ formatDate(row.entry_time) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              size="mini"
              @click="handleEdit(row)"
            >Edit</el-button>
            <el-button
              size="mini"
              type="danger"
              @click="handleDelete(row)"
            >Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
        ></el-pagination>
      </div>
    </el-card>

    <!-- Add/Edit dialog -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="50%">
      <el-form :model="form" :rules="rules" ref="form" label-width="120px">
        <el-form-item label="Fabrication Process" prop="fabrication">
          <el-input v-model="form.fabrication"></el-input>
        </el-form-item>
        
        <!-- Homogenization -->
        <el-form-item label="Homogenization">
          <el-switch v-model="form.homogenization"></el-switch>
          <template v-if="form.homogenization">
            <el-form-item label="Homogenization Temperature" prop="homogenize_temp">
              <el-input-number v-model="form.homogenize_temp" :precision="1" :step="10"></el-input-number>
            </el-form-item>
            <el-form-item label="Homogenization Time" prop="homogenize_time">
              <el-input-number v-model="form.homogenize_time" :precision="1" :step="0.5"></el-input-number>
            </el-form-item>
          </template>
        </el-form-item>

        <!-- Normalization -->
        <el-form-item label="Normalization">
          <el-switch v-model="form.normalization"></el-switch>
          <template v-if="form.normalization">
            <el-form-item label="Normalization Temperature" prop="normalize_temp">
              <el-input-number v-model="form.normalize_temp" :precision="1" :step="10"></el-input-number>
            </el-form-item>
            <el-form-item label="Normalization Time" prop="normalize_time">
              <el-input-number v-model="form.normalize_time" :precision="1" :step="0.5"></el-input-number>
            </el-form-item>
          </template>
        </el-form-item>

        <!-- Annealing -->
        <el-form-item label="Annealing">
          <el-switch v-model="form.annealing"></el-switch>
          <template v-if="form.annealing">
            <el-form-item label="Annealing Temperature" prop="annealing_temp">
              <el-input-number v-model="form.annealing_temp" :precision="1" :step="10"></el-input-number>
            </el-form-item>
            <el-form-item label="Annealing Time" prop="annealing_time">
              <el-input-number v-model="form.annealing_time" :precision="1" :step="0.5"></el-input-number>
            </el-form-item>
          </template>
        </el-form-item>

        <!-- Tempering -->
        <el-form-item label="Tempering">
          <el-switch v-model="form.tempering"></el-switch>
          <template v-if="form.tempering">
            <el-form-item label="Tempering Temperature" prop="tempering_temp">
              <el-input-number v-model="form.tempering_temp" :precision="1" :step="10"></el-input-number>
            </el-form-item>
            <el-form-item label="Tempering Time" prop="tempering_time">
              <el-input-number v-model="form.tempering_time" :precision="1" :step="0.5"></el-input-number>
            </el-form-item>
          </template>
        </el-form-item>

        <!-- Quenching -->
        <el-form-item label="Quenching">
          <el-switch v-model="form.quenching"></el-switch>
          <template v-if="form.quenching">
            <el-form-item label="Quenching Type" prop="quenching_type">
              <el-input v-model="form.quenching_type"></el-input>
            </el-form-item>
            <el-form-item label="Quenching Temperature" prop="quenching_temp">
              <el-input-number v-model="form.quenching_temp" :precision="1" :step="10"></el-input-number>
            </el-form-item>
          </template>
        </el-form-item>

        <!-- Rolling -->
        <el-form-item label="Rolling">
          <el-switch v-model="form.rolling"></el-switch>
          <template v-if="form.rolling">
            <el-form-item label="Rolling Temperature" prop="rolling_temp">
              <el-input-number v-model="form.rolling_temp" :precision="1" :step="10"></el-input-number>
            </el-form-item>
            <el-form-item label="Reduction" prop="reduction">
              <el-input-number v-model="form.reduction" :precision="1" :step="0.5"></el-input-number>
            </el-form-item>
          </template>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="submitForm">Confirm</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { getProcesses, createProcess, updateProcess, deleteProcess } from '@/api/process'

export default {
  name: 'ProcessList',
  data() {
    return {
      loading: false,
      tableData: [],
      currentPage: 1,
      pageSize: 10,
      total: 0,
      searchForm: {
        fabrication: ''
      },
      dialogVisible: false,
      dialogTitle: 'Add Process',
      form: {
        process_id: null,
        fabrication: '',
        homogenization: false,
        homogenize_temp: null,
        homogenize_time: null,
        normalization: false,
        normalize_temp: null,
        normalize_time: null,
        annealing: false,
        annealing_temp: null,
        annealing_time: null,
        tempering: false,
        tempering_temp: null,
        tempering_time: null,
        quenching: false,
        quenching_type: '',
        quenching_temp: null,
        rolling: false,
        rolling_temp: null,
        reduction: null
      },
      rules: {
        fabrication: [
          { required: true, message: 'Please enter fabrication process', trigger: 'blur' }
        ]
      }
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize,
          ...this.searchForm
        }
        const response = await getProcesses(params)
        this.tableData = response.data.results
        this.total = response.data.count
      } catch (error) {
        console.error('Failed to load the process list:')
        this.$message.error('Failed to load process list')
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      this.currentPage = 1
      this.fetchData()
    },
    resetSearch() {
      this.searchForm = {
        fabrication: ''
      }
      this.handleSearch()
    },
    handleSizeChange(val) {
      this.pageSize = val
      this.fetchData()
    },
    handleCurrentChange(val) {
      this.currentPage = val
      this.fetchData()
    },
    handleAdd() {
      this.dialogTitle = 'Add Process'
      this.form = {
        process_id: null,
        fabrication: '',
        homogenization: false,
        homogenize_temp: null,
        homogenize_time: null,
        normalization: false,
        normalize_temp: null,
        normalize_time: null,
        annealing: false,
        annealing_temp: null,
        annealing_time: null,
        tempering: false,
        tempering_temp: null,
        tempering_time: null,
        quenching: false,
        quenching_type: '',
        quenching_temp: null,
        rolling: false,
        rolling_temp: null,
        reduction: null
      }
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.dialogTitle = 'Edit Process'
      this.form = { ...row }
      this.dialogVisible = true
    },
    async handleDelete(row) {
      try {
        await this.$confirm('Are you sure you want to delete this process record?', 'Confirm', {
          type: 'warning'
        })
        await deleteProcess(row.process_id)
        this.$message.success('Deleted successfully')
        this.fetchData()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to delete the process:')
          this.$message.error('Failed to delete process')
        }
      }
    },
    async submitForm() {
      this.$refs.form.validate(async (valid) => {
        if (valid) {
          try {
            if (this.form.process_id) {
              await updateProcess(this.form.process_id, this.form)
              this.$message.success('Updated successfully')
            } else {
              await createProcess(this.form)
              this.$message.success('Added successfully')
            }
            this.dialogVisible = false
            this.fetchData()
          } catch (error) {
            console.error('Submission failed:')
            this.$message.error('Submit failed')
          }
        }
      })
    },
    formatDate(date) {
      if (!date) return ''
      return new Date(date).toLocaleString()
    }
  }
}
</script>

<style scoped>
.process-list {
  padding: 20px;
}
.search-form {
  margin-bottom: 20px;
}
.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style> 
