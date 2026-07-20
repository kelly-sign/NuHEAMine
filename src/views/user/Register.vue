<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <h2>User Registration</h2>
        </div>
      </template>
      
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-width="100px"
        class="register-form"
      >
        <el-form-item label="Username" prop="username">
          <el-input 
            v-model="registerForm.username"
            placeholder="Please enter username"
          />
        </el-form-item>

        <el-form-item label="Email" prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="Enter your email address"
          />
        </el-form-item>

        <el-form-item label="Password" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="Please enter password"
            show-password
          />
        </el-form-item>

        <el-form-item label="Confirm Password" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="Please confirm password"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary"
            class="register-button"
            :loading="loading"
            @click="handleRegister"
          >
            Register
          </el-button>
        </el-form-item>

        <div class="login-link">
          Already have an account?
          <router-link to="/user/login">Login now</router-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const registerFormRef = ref(null)
const loading = ref(false)

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('Please enter password again'))
  } else if (value !== registerForm.password) {
    callback(new Error('The passwords do not match'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { required: true, message: 'Please enter username', trigger: 'blur' },
    { min: 3, max: 20, message: 'Username must be between 3 and 20 characters', trigger: 'blur' }
  ],
  email: [
    { required: true, message: 'Please enter an email address', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email address', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter password', trigger: 'blur' },
    { min: 6, max: 20, message: 'Password must be between 6 and 20 characters', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: 'Please enter password again', trigger: 'blur' },
    { validator: validatePass2, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return

  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        loading.value = true
        // TODO: 调用注册API
        // const res = await register(registerForm)
        
        ElMessage.success('Registration successful')
        router.push('/user/login')
      } catch (error) {
        ElMessage.error('Registration failed')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.register-container {
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

.register-card {
  width: 500px;
  background-color: rgba(255, 255, 255, 0.92);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
  border: none;
  border-radius: 8px;
}

.card-header {
  text-align: center;
}

.register-form {
  padding: 20px;
}

.register-button {
  width: 100%;
}

.login-link {
  text-align: center;
  margin-top: 20px;
}
</style> 
