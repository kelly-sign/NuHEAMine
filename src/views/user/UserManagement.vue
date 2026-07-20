<template>
  <div class="user-management">
    <page-header 
      title="User Management"
      subtitle="Manage system users and permissions"
    >
      <template #actions>
        <el-button type="primary" @click="handleAdd">
          Add User
        </el-button>
      </template>
    </page-header>

    <el-card class="user-table-card">
      <!-- Search和筛选 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="Username">
          <el-input v-model="searchForm.username" placeholder="Please enter username" />
        </el-form-item>
        <el-form-item label="Role">
          <el-select v-model="searchForm.role" placeholder="Select a role" clearable>
            <el-option label="Administrator" value="admin" />
            <el-option label="User" value="user" />
            <el-option label="Guest" value="guest" />
          </el-select>
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="searchForm.status" placeholder="Select a status" clearable>
            <el-option label="Active" value="active" />
            <el-option label="Disabled" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleReset">Reset</el-button>
        </el-form-item>
      </el-form>

      <!-- User列表 -->
      <el-table :data="users" v-loading="loading" border>
        <el-table-column prop="username" label="Username" />
        <el-table-column prop="email" label="Email" />
        <el-table-column prop="role" label="Role">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)">
              {{ getRoleName(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? 'Active' : 'Disabled' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_login" label="Last Login">
          <template #default="{ row }">
            {{ formatDate(row.last_login) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="250">
          <template #default="{ row }">
            <el-button-group>
              <el-button 
                size="small"
                @click="handleEdit(row)"
              >
                Edit
              </el-button>
              <el-button
                size="small"
                :type="row.status === 'active' ? 'warning' : 'success'"
                @click="handleToggleStatus(row)"
              >
                {{ row.status === 'active' ? 'Disable' : 'Enable' }}
              </el-button>
              <el-button
                size="small"
                @click="handleResetPassword(row)"
              >
                Reset Password
              </el-button>
              <el-button
                size="small"
                type="danger"
                @click="handleDelete(row)"
              >
                Delete
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
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

    <!-- User表单对话框 -->
    <el-dialog
      :title="dialogType === 'create' ? 'Add User' : 'Edit User'"
      v-model="dialogVisible"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="Username" prop="username">
          <el-input v-model="form.username" :disabled="dialogType === 'edit'" />
        </el-form-item>
        <el-form-item label="Email" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="Role" prop="role">
          <el-select v-model="form.role">
            <el-option label="Administrator" value="admin" />
            <el-option label="User" value="user" />
            <el-option label="Guest" value="guest" />
          </el-select>
        </el-form-item>
        <el-form-item label="Password" prop="password" v-if="dialogType === 'create'">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          Confirm
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'

const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const dialogType = ref('create')
const submitting = ref(false)

// Search form
const searchForm = reactive({
  username: '',
  role: '',
  status: ''
})

// User表单
const formRef = ref(null)
const form = reactive({
  username: '',
  email: '',
  role: 'user',
  password: ''
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: 'Please enter username', trigger: 'blur' },
    { min: 3, max: 20, message: 'Username must be between 3 and 20 characters', trigger: 'blur' }
  ],
  email: [
    { required: true, message: 'Please enter an email address', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email address', trigger: 'blur' }
  ],
  role: [
    { required: true, message: 'Please select a role', trigger: 'change' }
  ],
  password: [
    { required: true, message: 'Please enter password', trigger: 'blur' },
    { min: 6, max: 20, message: 'Password must be between 6 and 20 characters', trigger: 'blur' }
  ]
}

// 模拟数据
const users = ref([
  {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    role: 'admin',
    status: 'active',
    last_login: '2024-03-20T10:00:00Z'
  }
])

// 处理Search
const handleSearch = () => {
  currentPage.value = 1
  fetchUsers()
}

// 处理Reset
const handleReset = () => {
  searchForm.username = ''
  searchForm.role = ''
  searchForm.status = ''
  handleSearch()
}

// 获取User列表
const fetchUsers = async () => {
  try {
    loading.value = true
    // TODO: 调用获取User列表API
    // const res = await getUserList({
    //   page: currentPage.value,
    //   ...searchForm
    // })
    // users.value = res.data.results
    // total.value = res.data.count
  } catch (error) {
    ElMessage.error('Failed to load users')
  } finally {
    loading.value = false
  }
}

// 处理AddUser
const handleAdd = () => {
  dialogType.value = 'create'
  dialogVisible.value = true
  form.username = ''
  form.email = ''
  form.role = 'user'
  form.password = ''
}

// 处理EditUser
const handleEdit = (row) => {
  dialogType.value = 'edit'
  dialogVisible.value = true
  Object.assign(form, row)
}

// 处理提交
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        submitting.value = true
        if (dialogType.value === 'create') {
          // TODO: 调用创建UserAPI
          ElMessage.success('Added successfully')
        } else {
          // TODO: 调用更新UserAPI
          ElMessage.success('Updated successfully')
        }
        dialogVisible.value = false
        fetchUsers()
      } catch (error) {
        ElMessage.error('Operation failed')
      } finally {
        submitting.value = false
      }
    }
  })
}

// 处理DeleteUser
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('Are you sure you want to delete this user?', 'Confirm', {
      type: 'warning'
    })
    // TODO: 调用DeleteUserAPI
    ElMessage.success('Deleted successfully')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Delete failed')
    }
  }
}

// 处理启用/禁用User
const handleToggleStatus = async (row) => {
  const action = row.status === 'active' ? 'Disable' : 'Enable'
  try {
    await ElMessageBox.confirm(`${action} this user?`, 'Confirm', {
      type: 'warning'
    })
    // TODO: 调用更新User状态API
    ElMessage.success(`${action} successful`)
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`${action} failed`)
    }
  }
}

// 处理Reset密码
const handleResetPassword = async (row) => {
  try {
    await ElMessageBox.confirm("Are you sure you want to reset this user's password?", 'Confirm', {
      type: 'warning'
    })
    // TODO: 调用Reset密码API
    ElMessage.success('Password reset successfully')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Password reset failed')
    }
  }
}

// 获取角色Type
const getRoleType = (role) => {
  const types = {
    admin: 'danger',
    user: '',
    guest: 'info'
  }
  return types[role] || ''
}

// 获取角色名称
const getRoleName = (role) => {
  const names = {
    admin: 'Administrator',
    user: 'User',
    guest: 'Guest'
  }
  return names[role] || role
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchUsers()
}
</script>

<style scoped>
.user-management {
  padding: 20px;
}

.search-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style> 
