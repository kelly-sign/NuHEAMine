<template>
  <div class="register-container">
    <div class="register-box">
      <h2 class="title">Register Account</h2>
      <div class="form-container">
        <div class="form-item">
          <label for="username">Username</label>
          <input 
            id="username"
            v-model="registerForm.username" 
            type="text" 
            placeholder="Enter a username"
          >
        </div>
        <div class="form-item">
          <label for="password">Password</label>
          <input 
            id="password"
            v-model="registerForm.password" 
            type="password" 
            placeholder="Enter a password"
          >
        </div>
        <div class="form-item">
          <label for="confirmPassword">Confirm Password</label>
          <input 
            id="confirmPassword"
            v-model="registerForm.confirmPassword" 
            type="password" 
            placeholder="Enter the password again"
            @keyup.enter="handleRegister"
          >
        </div>
        <div class="error-message" v-if="errorMessage">{{ errorMessage }}</div>
        <button 
          class="register-button" 
          :disabled="loading" 
          @click="handleRegister"
        >
          {{ loading ? 'Registering...' : 'Register' }}
        </button>
        <div class="login-link">
          <span>Already have an account?</span>
          <router-link to="/login">Login Now</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

export default {
  name: 'Register',
  setup() {
    const store = useStore();
    const router = useRouter();
    
    const registerForm = reactive({
      username: '',
      password: '',
      confirmPassword: ''
    });
    
    const loading = ref(false);
    const errorMessage = ref('');
    
    const handleRegister = async () => {
      // 表单验证
      if (!registerForm.username) {
        errorMessage.value = 'Please enter a username.';
        return;
      }
      if (!registerForm.password) {
        errorMessage.value = 'Please enter a password.';
        return;
      }
      if (!registerForm.confirmPassword) {
        errorMessage.value = 'Please confirm your password.';
        return;
      }
      if (registerForm.password !== registerForm.confirmPassword) {
        errorMessage.value = 'The passwords do not match.';
        return;
      }
      
      loading.value = true;
      errorMessage.value = '';
      
      try {
        await store.dispatch('user/register', {
          username: registerForm.username,
          password: registerForm.password,
          confirmPassword: registerForm.confirmPassword
        });
        
        // 注册成功，跳转到首页
        router.push({ path: '/' });
      } catch (error) {
        // 处理注册错误
        if (error.response && error.response.data) {
          errorMessage.value = 'Registration failed. Please check the form and try again.';
        } else {
          errorMessage.value = 'Network error. Please check your connection.';
        }
      } finally {
        loading.value = false;
      }
    };
    
    return {
      registerForm,
      loading,
      errorMessage,
      handleRegister
    };
  }
};
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100vh;
  padding: 40px 20px;
  background-image: url('@/assets/login-bg.png');
  background-repeat: no-repeat;
  background-position: center top;
  background-size: cover;
  box-sizing: border-box;
}

.register-box {
  width: 1060px;
  margin: 0 auto;
  padding: 44px 60px;
  background-color: rgba(255, 255, 255, 0.92);
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.2);
}

.title {
  text-align: center;
  margin-bottom: 28px;
  color: #303133;
  font-size: 45px;
}

.form-container {
  margin-top: 18px;
}

.form-item {
  margin-bottom: 20px;
}

.form-item label {
  display: block;
  margin-bottom: 12px;
  color: #606266;
  font-size: 25px;
}

.form-item input {
  width: 100%;
  padding: 17px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 25px;
  color: #606266;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-item input:focus {
  outline: none;
  border-color: #409eff;
}

.error-message {
  color: #f56c6c;
  font-size: 20px;
  margin-bottom: 24px;
}

.register-button {
  width: 100%;
  padding: 14px 17px;
  background-color: #409eff;
  border: none;
  border-radius: 4px;
  color: #fff;
  font-size: 30px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.register-button:hover {
  background-color: #66b1ff;
}

.register-button:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.login-link {
  margin-top: 18px;
  text-align: center;
  font-size: 20px;
  color: #606266;
}

.login-link a {
  color: #409eff;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style> 
