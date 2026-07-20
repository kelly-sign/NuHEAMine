<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <el-col :span="8">
        <!-- 个人信息卡片 -->
        <el-card class="profile-card">
          <div class="profile-header">
            <el-avatar :size="100" :src="userInfo.avatar">
              {{ userInfo.username?.charAt(0).toUpperCase() }}
            </el-avatar>
            <h2>{{ userInfo.username }}</h2>
            <p>{{ getRoleName(userInfo.role) }}</p>
          </div>
          
          <el-divider />
          
          <div class="profile-info">
            <div class="info-item">
              <span class="label">Email:</span>
              <span>{{ userInfo.email }}</span>
            </div>
            <div class="info-item">
              <span class="label">Registered:</span>
              <span>{{ formatDate(userInfo.created_at) }}</span>
            </div>
            <div class="info-item">
              <span class="label">Last Login:</span>
              <span>{{ formatDate(userInfo.last_login) }}</span>
            </div>
          </div>
        </el-card>

        <!-- 统计信息卡片 -->
        <el-card class="stats-card">
          <template #header>
            <div class="card-header">
              <span>Activity Statistics</span>
            </div>
          </template>
          
          <div class="stats-list">
            <div class="stats-item">
              <div class="stats-value">{{ stats.materialCount }}</div>
              <div class="stats-label">Material Records</div>
            </div>
            <div class="stats-item">
              <div class="stats-value">{{ stats.predictionCount }}</div>
              <div class="stats-label">Predictions</div>
            </div>
            <div class="stats-item">
              <div class="stats-value">{{ stats.reportCount }}</div>
              <div class="stats-label">Reports Generated</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="16">
        <!-- 基本信息设置 -->
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <span>Basic Information</span>
            </div>
          </template>

          <el-form
            ref="basicFormRef"
            :model="basicForm"
            :rules="basicRules"
            label-width="100px"
          >
            <el-form-item label="Username" prop="username">
              <el-input v-model="basicForm.username" disabled />
            </el-form-item>
            
            <el-form-item label="Email" prop="email">
              <el-input v-model="basicForm.email" />
            </el-form-item>
            
            <el-form-item label="Avatar">
              <el-upload
                class="avatar-uploader"
                action="#"
                :show-file-list="false"
                :before-upload="beforeAvatarUpload"
                :http-request="handleAvatarUpload"
              >
                <img v-if="basicForm.avatar" :src="basicForm.avatar" class="avatar" />
                <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
              </el-upload>
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary"
                @click="handleUpdateBasic"
                :loading="updating"
              >
                Save Changes
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 密码修改 -->
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <span>Change Password</span>
            </div>
          </template>

          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="100px"
          >
            <el-form-item label="Current Password" prop="oldPassword">
              <el-input
                v-model="passwordForm.oldPassword"
                type="password"
                show-password
              />
            </el-form-item>
            
            <el-form-item label="New Password" prop="newPassword">
              <el-input
                v-model="passwordForm.newPassword"
                type="password"
                show-password
              />
            </el-form-item>
            
            <el-form-item label="Confirm Password" prop="confirmPassword">
              <el-input
                v-model="passwordForm.confirmPassword"
                type="password"
                show-password
              />
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary"
                @click="handleUpdatePassword"
                :loading="updating"
              >
                Change Password
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const userInfo = ref({
  username: 'admin',
  role: 'admin',
  email: 'admin@example.com',
  avatar: '',
  created_at: '2024-01-01T00:00:00Z',
  last_login: '2024-03-20T10:00:00Z'
})

const stats = ref({
  materialCount: 100,
  predictionCount: 500,
  reportCount: 50
})

const updating = ref(false)
const basicFormRef = ref(null)
const passwordFormRef = ref(null)

// 基本信息表单
const basicForm = reactive({
  username: '',
  email: '',
  avatar: ''
})

// 密码修改表单
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 基本信息验证规则
const basicRules = {
  email: [
    { required: true, message: 'Please enter an email address', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email address', trigger: 'blur' }
  ]
}

// 密码验证规则
const passwordRules = {
  oldPassword: [
    { required: true, message: 'Please enter your current password', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: 'Please enter a new password', trigger: 'blur' },
    { min: 6, max: 20, message: 'Password must be between 6 and 20 characters', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: 'Please enter the new password again', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('The passwords do not match'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 获取User信息
const fetchUserInfo = async () => {
  try {
    // TODO: 调用获取User信息API
    // const res = await getUserInfo()
    // userInfo.value = res.data
    Object.assign(basicForm, {
      username: userInfo.value.username,
      email: userInfo.value.email,
      avatar: userInfo.value.avatar
    })
  } catch (error) {
    ElMessage.error('Failed to load user information')
  }
}

// 更新基本信息
const handleUpdateBasic = async () => {
  if (!basicFormRef.value) return

  await basicFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        updating.value = true
        // TODO: 调用更新User信息API
        // await updateUserInfo(basicForm)
        ElMessage.success('Updated successfully')
      } catch (error) {
        ElMessage.error('Update failed')
      } finally {
        updating.value = false
      }
    }
  })
}

// 更新密码
const handleUpdatePassword = async () => {
  if (!passwordFormRef.value) return

  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        updating.value = true
        // TODO: 调用修改密码API
        // await updatePassword(passwordForm)
        ElMessage.success('Password changed successfully')
        passwordFormRef.value.resetFields()
      } catch (error) {
        ElMessage.error('Failed to change password')
      } finally {
        updating.value = false
      }
    }
  })
}

// 头像上传前的验证
const beforeAvatarUpload = (file) => {
  const isJPG = file.type === 'image/jpeg'
  const isPNG = file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isJPG && !isPNG) {
    ElMessage.error('The avatar must be a JPG or PNG image')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('The avatar must not exceed 2 MB')
    return false
  }
  return true
}

// 处理头像上传
const handleAvatarUpload = async ({ file }) => {
  try {
    // TODO: 调用上传头像API
    // const res = await uploadAvatar(file)
    // basicForm.avatar = res.data.url
    ElMessage.success('Avatar uploaded successfully')
  } catch (error) {
    ElMessage.error('Failed to upload avatar')
  }
}

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

onMounted(() => {
  fetchUserInfo()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.profile-card,
.stats-card,
.settings-card {
  margin-bottom: 20px;
}

.profile-header {
  text-align: center;
  padding: 20px 0;
}

.profile-header h2 {
  margin: 10px 0 5px;
}

.profile-info {
  padding: 0 20px;
}

.info-item {
  margin: 10px 0;
  display: flex;
}

.info-item .label {
  color: #666;
  width: 80px;
}

.stats-list {
  display: flex;
  justify-content: space-around;
  text-align: center;
}

.stats-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.stats-label {
  margin-top: 5px;
  color: #666;
}

.avatar-uploader {
  text-align: center;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 178px;
  height: 178px;
}

.avatar-uploader:hover {
  border-color: #409EFF;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  line-height: 178px;
  text-align: center;
}

.avatar {
  width: 178px;
  height: 178px;
  display: block;
}
</style> 
