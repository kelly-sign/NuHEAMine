<template>
  <div class="login-container">
    <div class="login-box">
      <h2 class="title">Welcome to NuHEAMine</h2>
      <div class="form-container">
        <div class="form-item">
          <label for="username">Username</label>
          <input 
            id="username"
            v-model="loginForm.username" 
            type="text" 
            placeholder="Enter your username"
            @keyup.enter="handleLogin"
          >
        </div>
        <div class="form-item">
          <label for="password">Password</label>
          <input 
            id="password"
            v-model="loginForm.password" 
            type="password" 
            placeholder="Enter your password"
            @keyup.enter="handleLogin"
          >
        </div>
        <div class="error-message" v-if="errorMessage">{{ errorMessage }}</div>
        <button 
          class="login-button" 
          :disabled="loading" 
          @click="handleLogin"
        >
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
        <div class="register-link">
          <span>Don't have an account?</span>
          <router-link to="/register">Register now</router-link>
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
  name: 'Login',
  setup() {
    const store = useStore();
    const router = useRouter();
    
    const loginForm = reactive({
      username: '',
      password: ''
    });
    
    const loading = ref(false);
    const errorMessage = ref('');
    
    const handleLogin = async () => {
      // 表单验证
      if (!loginForm.username) {
        errorMessage.value = 'Please enter your username.';
        return;
      }
      if (!loginForm.password) {
        errorMessage.value = 'Please enter your password.';
        return;
      }
      
      loading.value = true;
      errorMessage.value = '';
      
      try {
        await store.dispatch('user/login', {
          username: loginForm.username,
          password: loginForm.password
        });
        
        // 登录成功，跳转到首页
        router.push({ path: '/' });
      } catch (error) {
        // 处理登录错误
        if (error.response && error.response.data) {
          errorMessage.value = 'Login failed. Check your username and password.';
        } else {
          errorMessage.value = 'Network error. Please check your connection.';
        }
      } finally {
        loading.value = false;
      }
    };
    
    return {
      loginForm,
      loading,
      errorMessage,
      handleLogin
    };
  }
};
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

.login-box {
  width: 1060px;
  padding: 60px;
  background-color: rgba(255, 255, 255, 0.92);
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.2);
}

.title {
  text-align: center;
  margin-bottom: 40px;
  color: #303133;
  font-size: 45px;
}

.form-container {
  margin-top: 28px;
}

.form-item {
  margin-bottom: 28px;
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

.login-button {
  width: 100%;
  padding: 17px;
  background-color: #409eff;
  border: none;
  border-radius: 4px;
  color: #fff;
  font-size: 30px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.login-button:hover {
  background-color: #66b1ff;
}

.login-button:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.register-link {
  margin-top: 28px;
  text-align: center;
  font-size: 20px;
  color: #606266;
}

.register-link a {
  color: #409eff;
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}
</style> 
