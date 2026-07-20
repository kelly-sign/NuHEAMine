<template>
  <div class="report-container">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <span>Report Configuration</span>
            </div>
          </template>
          
          <el-form 
            ref="reportFormRef"
            :model="reportForm"
            :rules="reportRules"
            label-width="100px"
          >
            <el-form-item label="Report Title" prop="title">
              <el-input v-model="reportForm.title" placeholder="Enter a report title" />
            </el-form-item>

            <el-form-item label="Report Type" prop="reportType">
              <el-select v-model="reportForm.reportType" placeholder="Select a report type">
                <el-option label="Performance Analysis Report" value="performance" />
                <el-option label="Prediction Results Report" value="prediction" />
                <el-option label="Statistical Analysis Report" value="statistics" />
              </el-select>
            </el-form-item>

            <el-form-item label="Report Template" prop="templateId">
              <el-select v-model="reportForm.templateId" placeholder="Select a report template">
                <el-option
                  v-for="template in templates"
                  :key="template.id"
                  :label="template.name"
                  :value="template.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="Date Range" prop="dateRange">
              <el-date-picker
                v-model="reportForm.dateRange"
                type="daterange"
                range-separator="to"
                start-placeholder="Start date"
                end-placeholder="End date"
              />
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary"
                :loading="loading"
                @click="handleGenerate"
              >
                Generate Report
              </el-button>
              <el-button @click="handleReset">Reset</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card class="history-card">
          <template #header>
            <div class="card-header">
              <span>Report History</span>
              <el-input
                v-model="searchKeyword"
                placeholder="Search reports"
                class="search-input"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>
          </template>

          <el-table :data="filteredReports" style="width: 100%">
            <el-table-column prop="title" label="Report Title" />
            <el-table-column prop="report_type" label="Report Type">
              <template #default="scope">
                {{ getReportTypeName(scope.row.report_type) }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="Generated At">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="200">
              <template #default="scope">
                <el-button 
                  size="small"
                  @click="handlePreview(scope.row)"
                >
                  Preview
                </el-button>
                <el-button
                  size="small"
                  type="primary"
                  @click="handleDownload(scope.row)"
                >
                  Download
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination">
            <el-pagination
              :current-page="currentPage"
              :page-size="pageSize"
              :total="total"
              @current-change="handleCurrentChange"
              layout="total, prev, pager, next"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 报告预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="Report Preview"
      width="80%"
    >
      <div class="preview-content">
        <div v-if="selectedReport">
          <h2>{{ selectedReport.title }}</h2>
          <div v-for="(section, index) in selectedReport.content.sections" :key="index">
            <h3>{{ section.title }}</h3>
            <p v-if="section.text">{{ section.text }}</p>
            <el-table
              v-if="section.table"
              :data="section.table.data"
              :columns="section.table.headers"
              border
            />
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const reportFormRef = ref(null)
const loading = ref(false)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const previewDialogVisible = ref(false)
const selectedReport = ref(null)

// 模拟数据
const templates = ref([
  { id: 1, name: 'Standard Performance Analysis Template' },
  { id: 2, name: 'Prediction Results Report Template' },
  { id: 3, name: 'Statistical Analysis Report Template' }
])

const reports = ref([
  {
    id: 1,
    title: 'Q1 2024 Performance Analysis Report',
    report_type: 'performance',
    created_at: '2024-03-20T10:00:00Z',
    content: {
      sections: [
        {
          title: 'Overview',
          text: 'This is a performance analysis report...'
        },
        {
          title: 'Data Analysis',
          table: {
            headers: ['Metric', 'Value', 'Unit'],
            data: [
              ['Hardness', 500, 'HV'],
              ['Yield Strength', 800, 'MPa']
            ]
          }
        }
      ]
    }
  }
])

const reportForm = ref({
  title: '',
  reportType: '',
  templateId: '',
  dateRange: []
})

const reportRules = {
  title: [
    { required: true, message: 'Please enter a report title', trigger: 'blur' }
  ],
  reportType: [
    { required: true, message: 'Please select a report type', trigger: 'change' }
  ],
  templateId: [
    { required: true, message: 'Please select a report template', trigger: 'change' }
  ]
}

const filteredReports = computed(() => {
  if (!searchKeyword.value) return reports.value
  
  return reports.value.filter(report => 
    report.title.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

const handleGenerate = async () => {
  if (!reportFormRef.value) return

  await reportFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        loading.value = true
        // TODO: 调用生成报告API
        // const res = await generateReport(reportForm)
        
        ElMessage.success('Report generated successfully')
      } catch (error) {
        ElMessage.error('Failed to generate report')
      } finally {
        loading.value = false
      }
    }
  })
}

const handleReset = () => {
  reportFormRef.value?.resetFields()
}

const handlePreview = (report) => {
  selectedReport.value = report
  previewDialogVisible.value = true
}

const handleDownload = () => {
  // TODO: 实现下载功能
  ElMessage.success('Report download started')
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  // TODO: 加载对应页的数据
}

const getReportTypeName = (type) => {
  const types = {
    performance: 'Performance Analysis Report',
    prediction: 'Prediction Results Report',
    statistics: 'Statistical Analysis Report'
  }
  return types[type] || type
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}
</script>

<style scoped>
.report-container {
  padding: 20px;
}

.config-card,
.history-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-input {
  width: 200px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.preview-content {
  max-height: 60vh;
  overflow-y: auto;
  padding: 20px;
}
</style> 
