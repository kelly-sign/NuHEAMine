<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>User Login</h2>
        </div>
      </template>
      
      <el-form 
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-width="80px"
        class="login-form"
      >
        <el-form-item label="Username" prop="username">
          <el-input 
            v-model="loginForm.username"
            placeholder="Please enter username"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="Password" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="Please enter password"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="rememberMe">Remember me</el-checkbox>
          <el-link type="primary" class="forget-pwd" @click="handleForgetPassword">
            Forgot password?
          </el-link>
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            Login
          </el-button>
        </el-form-item>

        <div class="register-link">
          Don't have an account?
          <router-link to="/user/register">Register now</router-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const store = useStore()
const router = useRouter()
const route = useRoute()

const loginFormRef = ref(null)
const loading = ref(false)
const rememberMe = ref(false)

const loginForm = ref({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: 'Please enter username', trigger: 'blur' },
    { min: 3, max: 20, message: 'Username must be between 3 and 20 characters', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter password', trigger: 'blur' },
    { min: 6, max: 20, message: 'Password must be between 6 and 20 characters', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        loading.value = true
        await store.dispatch('login', loginForm.value)
        ElMessage.success('Login successful')
        
        const redirect = route.query.redirect || '/'
        router.push(redirect)
      } catch (error) {
        ElMessage.error('Login failed')
      } finally {
        loading.value = false
      }
    }
  })
}

const handleForgetPassword = () => {
  ElMessage.info('Please contact an administrator to reset your password')
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  padding: 40px 20px;
  background-image: url('@/assets/login-bg.png');
  background-repeat: no-repeat;
  background-position: center top;
  background-size: cover;
  box-sizing: border-box;
}

.login-card {
  width: 400px;
  background-color: rgba(255, 255, 255, 0.92);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
  border: none;
  border-radius: 8px;
}

.card-header {
  text-align: center;
}

.login-form {
  padding: 20px;
}

.login-button {
  width: 100%;
}

.forget-pwd {
  float: right;
}

.register-link {
  text-align: center;
  margin-top: 20px;
}
</style> 
