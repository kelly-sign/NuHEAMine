<template>
  <div class="help-container">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="menu-card">
          <el-menu
            :default-active="activeMenu"
            class="help-menu"
            @select="handleMenuSelect"
          >
            <el-menu-item index="overview">
              <el-icon><Document /></el-icon>
              <span>System Overview</span>
            </el-menu-item>
            
            <el-sub-menu index="features">
              <template #title>
                <el-icon><List /></el-icon>
                <span>Feature Guide</span>
              </template>
              <el-menu-item index="data-management">Data Management</el-menu-item>
              <el-menu-item index="performance-prediction">Performance Prediction</el-menu-item>
              <el-menu-item index="data-visualization">Data Visualization</el-menu-item>
              <el-menu-item index="report-generation">Report Generation</el-menu-item>
            </el-sub-menu>

            <el-menu-item index="faq">
              <el-icon><QuestionFilled /></el-icon>
              <span>FAQ</span>
            </el-menu-item>

            <el-menu-item index="contact">
              <el-icon><Message /></el-icon>
              <span>Contact Us</span>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>

      <el-col :span="18">
        <el-card class="content-card">
          <div class="help-content">
            <!-- 系统概述 -->
            <div v-if="activeMenu === 'overview'" class="section">
              <h2>System Overview</h2>
              <p>The High-Entropy Alloy Performance Prediction Platform is a machine-learning-based materials prediction system. It integrates data management, performance prediction, data visualization, and report generation to support materials research.</p>
              <h3>Main Features</h3>
              <ul>
                <li>Manage and maintain materials data</li>
                <li>Machine-learning-based performance prediction</li>
                <li>Data analysis and visualization</li>
                <li>Automated report generation</li>
              </ul>
            </div>

            <!-- 数据管理指南 -->
            <div v-if="activeMenu === 'data-management'" class="section">
              <h2>Data Management Guide</h2>
              <el-steps :active="1" simple>
                <el-step title="Data Entry" description="Enter materials data manually or import it in bulk" />
                <el-step title="Data Editing" description="Modify and update existing data" />
                <el-step title="Data Export" description="Export data in Excel or CSV format" />
              </el-steps>
              <div class="guide-content">
                <h3>Instructions</h3>
                <p>1. Click "Add Material" to add a record.</p>
                <p>2. Use search and filters to find data.</p>
                <p>3. Use the buttons in the Actions column to edit or delete a record.</p>
              </div>
            </div>

            <!-- Performance Prediction指南 -->
            <div v-if="activeMenu === 'performance-prediction'" class="section">
              <h2>Performance Prediction Guide</h2>
              <el-timeline>
                <el-timeline-item>
                  <h3>Enter Parameters</h3>
                  <p>Set the material composition and processing parameters.</p>
                </el-timeline-item>
                <el-timeline-item>
                  <h3>Select a Model</h3>
                  <p>Select an appropriate prediction model.</p>
                </el-timeline-item>
                <el-timeline-item>
                  <h3>View Results</h3>
                  <p>Review the prediction results and confidence analysis.</p>
                </el-timeline-item>
              </el-timeline>
            </div>

            <!-- FAQ -->
            <div v-if="activeMenu === 'faq'" class="section">
              <h2>Frequently Asked Questions</h2>
              <el-collapse>
                <el-collapse-item title="How do I reset my password?" name="1">
                  <p>Contact a system administrator to reset your password.</p>
                </el-collapse-item>
                <el-collapse-item title="How do I import data?" name="2">
                  <p>On the Data Management page, click "Import Data" and select an Excel file that follows the template.</p>
                </el-collapse-item>
                <el-collapse-item title="How reliable are the prediction results?" name="3">
                  <p>The system reports a confidence value that can be used to assess each prediction.</p>
                </el-collapse-item>
              </el-collapse>
            </div>

            <!-- 联系我们 -->
            <div v-if="activeMenu === 'contact'" class="section">
              <h2>Contact Us</h2>
              <el-form :model="contactForm" label-width="100px">
                <el-form-item label="Issue Type">
                  <el-select v-model="contactForm.type" placeholder="Select an issue type">
                    <el-option label="Feature Inquiry" value="function" />
                    <el-option label="Technical Support" value="support" />
                    <el-option label="Bug Report" value="bug" />
                    <el-option label="Other" value="other" />
                  </el-select>
                </el-form-item>
                <el-form-item label="Description">
                  <el-input
                    v-model="contactForm.description"
                    type="textarea"
                    rows="4"
                    placeholder="Describe your issue in detail"
                  />
                </el-form-item>
                <el-form-item label="Contact">
                  <el-input v-model="contactForm.contact" placeholder="Enter your contact information" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleSubmitFeedback">Submit</el-button>
                </el-form-item>
              </el-form>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, List, QuestionFilled, Message } from '@element-plus/icons-vue'

const activeMenu = ref('overview')
const contactForm = ref({
  type: '',
  description: '',
  contact: ''
})

const handleMenuSelect = (index) => {
  activeMenu.value = index
}

const handleSubmitFeedback = () => {
  // TODO: 实现提交反馈的逻辑
  ElMessage.success('Feedback submitted successfully. We will respond as soon as possible.')
  contactForm.value = {
    type: '',
    description: '',
    contact: ''
  }
}
</script>

<style scoped>
.help-container {
  padding: 20px;
}

.menu-card,
.content-card {
  min-height: calc(100vh - 120px);
}

.help-menu {
  border-right: none;
}

.section {
  padding: 20px;
}

.section h2 {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.guide-content {
  margin-top: 30px;
}

.el-steps {
  margin: 20px 0;
}

.el-timeline {
  margin: 20px 0;
}

.el-collapse {
  margin: 20px 0;
}
</style> 
