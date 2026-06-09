<script setup>
import { ref, onMounted } from 'vue'

// 后端API地址
const API_BASE = 'http://localhost:8888'

// 用户状态
const currentUser = ref(null)
const loginForm = ref({
  username: '',
  password: ''
})

// 比价功能相关状态
const bijiaForm = ref({
  a_name: '',
  a_price: '',
  a_per: '',
  b_name: '',
  b_price: '',
  b_per: ''
})
const bijiaResult = ref('')

// 抽奖功能相关状态
const choukaForm = ref({
  times: 10
})
const choukaResult = ref([])

// 保底信息
const baodiInfo = ref({
  baodi: 0,
  dabaodi: 0
})

// 刮刮乐状态
const scratchStatus = ref({
  total_cards: 0,
  remaining_cards: 0,
  scratched_count: 0
})
const scratchResult = ref(null)
const scratchMessage = ref('')

// 当前页面状态
const currentPage = ref('home')

// 登录状态
const loginMessage = ref('')
const isLoginSuccess = ref(false)

// 比价计算函数
async function calculateBijia() {
  try {
    const formData = new FormData()
    Object.keys(bijiaForm.value).forEach(key => {
      formData.append(key, bijiaForm.value[key])
    })
    
    const response = await fetch(`${API_BASE}/bijia_calc`, {
      method: 'POST',
      body: formData
    })
    
    if (response.ok) {
      const html = await response.text()
      // 提取文本内容，去除HTML标签
      bijiaResult.value = html.replace(/<[^>]*>/g, '')
    } else {
      bijiaResult.value = '计算失败，请检查输入'
    }
  } catch (error) {
    bijiaResult.value = '网络错误，请检查后端服务是否启动'
  }
}

// 抽奖函数
async function doChouka() {
  try {
    const formData = new FormData()
    formData.append('times', choukaForm.value.times)
    
    // 如果用户已登录，传递用户名用于记录保底
    if (currentUser.value) {
      formData.append('username', currentUser.value.username)
    }
    
    const response = await fetch(`${API_BASE}/chouka_do`, {
      method: 'POST',
      body: formData
    })
    
    if (response.ok) {
      const html = await response.text()
      // 解析HTML结果
      const parser = new DOMParser()
      const doc = parser.parseFromString(html, 'text/html')
      const results = Array.from(doc.querySelectorAll('div')).map(div => div.textContent)
      choukaResult.value = results
      
      // 抽卡后刷新保底信息
      if (currentUser.value) {
        await loadBaodiInfo()
      }
    } else {
      choukaResult.value = ['抽奖失败，请检查输入']
    }
  } catch (error) {
    choukaResult.value = ['网络错误，请检查后端服务是否启动']
  }
}

// 清空结果函数
function clearResults() {
  bijiaResult.value = ''
  choukaResult.value = []
}

// 用户登录
async function doLogin() {
  if (!loginForm.value.username || !loginForm.value.password) {
    loginMessage.value = '请输入用户名和密码'
    isLoginSuccess.value = false
    return
  }

  try {
    const formData = new FormData()
    formData.append('username', loginForm.value.username)
    formData.append('password', loginForm.value.password)
    
    const response = await fetch(`${API_BASE}/login`, {
      method: 'POST',
      body: formData
    })
    
    const result = await response.json()
    
    if (result.success) {
      currentUser.value = result.user
      loginMessage.value = result.message
      isLoginSuccess.value = true
      await loadBaodiInfo()
      
      // 清空登录表单
      loginForm.value.username = ''
      loginForm.value.password = ''
      
      // 自动跳转到首页
      setTimeout(() => {
        currentPage.value = 'home'
        loginMessage.value = ''
      }, 1500)
    } else {
      loginMessage.value = result.message
      isLoginSuccess.value = false
    }
  } catch (error) {
    loginMessage.value = '登录失败，请检查后端服务是否启动'
    isLoginSuccess.value = false
  }
}

// 用户注册
async function doRegister() {
  if (!loginForm.value.username || !loginForm.value.password) {
    loginMessage.value = '请输入用户名和密码'
    isLoginSuccess.value = false
    return
  }

  try {
    const formData = new FormData()
    formData.append('username', loginForm.value.username)
    formData.append('password', loginForm.value.password)
    
    const response = await fetch(`${API_BASE}/register`, {
      method: 'POST',
      body: formData
    })
    
    const result = await response.json()
    
    if (result.success) {
      currentUser.value = result.user
      loginMessage.value = result.message
      isLoginSuccess.value = true
      await loadBaodiInfo()
      
      // 清空登录表单
      loginForm.value.username = ''
      loginForm.value.password = ''
      
      // 自动跳转到首页
      setTimeout(() => {
        currentPage.value = 'home'
        loginMessage.value = ''
      }, 1500)
    } else {
      loginMessage.value = result.message
      isLoginSuccess.value = false
    }
  } catch (error) {
    loginMessage.value = '注册失败，请检查后端服务是否启动'
    isLoginSuccess.value = false
  }
}

// 退出登录
function logout() {
  currentUser.value = null
  baodiInfo.value = { baodi: 0, dabaodi: 0 }
  currentPage.value = 'home'
}

// 加载保底信息
async function loadBaodiInfo() {
  if (!currentUser.value) return
  
  try {
    const response = await fetch(`${API_BASE}/baodi/${currentUser.value.username}`)
    const result = await response.json()
    
    if (result.success) {
      baodiInfo.value = {
        baodi: result.baodi,
        dabaodi: result.dabaodi
      }
    }
  } catch (error) {
    console.error('获取保底信息失败:', error)
  }
}

// 获取刮刮乐状态
async function loadScratchStatus() {
  try {
    const response = await fetch(`${API_BASE}/scratch/status`)
    const result = await response.json()
    if (result.success) {
      scratchStatus.value = {
        total_cards: result.total_cards,
        remaining_cards: result.remaining_cards,
        scratched_count: result.scratched_count
      }
    }
  } catch (error) {
    console.error('获取刮刮乐状态失败:', error)
  }
}

// 刮开卡片
async function doScratch() {
  try {
    const response = await fetch(`${API_BASE}/scratch/play`, {
      method: 'POST'
    })
    const result = await response.json()
    
    if (result.success) {
      scratchResult.value = result.prize
      scratchMessage.value = result.message
      scratchStatus.value.remaining_cards = result.remaining_cards
      scratchStatus.value.scratched_count++
    } else {
      scratchMessage.value = result.message
      scratchResult.value = null
    }
  } catch (error) {
    scratchMessage.value = '刮卡失败，请检查后端服务'
    scratchResult.value = null
  }
}

// 重置刮刮乐
async function resetScratch() {
  try {
    const response = await fetch(`${API_BASE}/scratch/reset`, {
      method: 'POST'
    })
    const result = await response.json()
    
    if (result.success) {
      scratchMessage.value = result.message
      await loadScratchStatus()
      scratchResult.value = null
    } else {
      scratchMessage.value = result.message
    }
  } catch (error) {
    scratchMessage.value = '重置失败，请检查后端服务'
  }
}

// 组件挂载时检查用户状态
onMounted(() => {
  // 这里可以添加自动登录逻辑，比如从localStorage读取token等
})
</script>

<template>
  <div class="app">
    <header>
      <h1>小助手网页版</h1>
      <div class="user-info">
        <span v-if="currentUser" class="welcome-text">
          欢迎，{{ currentUser.username }} 
          <button @click="logout" class="logout-btn">退出</button>
        </span>
        <button v-else @click="currentPage = 'login'" class="login-btn">登录/注册</button>
      </div>
      <nav>
        <button @click="currentPage = 'home'; clearResults()">首页</button>
        <button @click="currentPage = 'bijia'; clearResults()">商品比价</button>
        <button @click="currentPage = 'chouka'; clearResults()">抽奖</button>
        <button @click="currentPage = 'baodi'; clearResults()">保底查询</button>
        <button @click="currentPage = 'scratch'; clearResults(); loadScratchStatus()">武器刮刮乐</button>
      </nav>
    </header>

    <main>
      <!-- 首页 -->
      <div v-if="currentPage === 'home'" class="home-page">
        <h2>欢迎使用小助手</h2>
        <p v-if="!currentUser">请先登录以使用完整功能</p>
        <div v-if="currentUser" class="baodi-card">
          <h3>当前保底状态</h3>
          <div class="baodi-stats">
            <div class="stat-item">
              <span class="stat-label">保底计数:</span>
              <span class="stat-value">{{ baodiInfo.baodi }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">大保底计数:</span>
              <span class="stat-value">{{ baodiInfo.dabaodi }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 登录/注册页面 -->
      <div v-if="currentPage === 'login'" class="login-page">
        <h2>登录 / 注册</h2>
        <form @submit.prevent="doLogin" class="login-form">
          <div class="form-group">
            <label>用户名:</label>
            <input v-model="loginForm.username" type="text" placeholder="请输入用户名" required>
          </div>
          <div class="form-group">
            <label>密码:</label>
            <input v-model="loginForm.password" type="password" placeholder="请输入密码" required>
          </div>
          <div class="button-group">
            <button type="submit" class="btn-primary">登录</button>
            <button type="button" @click="doRegister" class="btn-secondary">注册</button>
          </div>
        </form>
        <div v-if="loginMessage" :class="['message', isLoginSuccess ? 'success' : 'error']">
          {{ loginMessage }}
        </div>
      </div>

      <!-- 比价页面 -->
      <div v-if="currentPage === 'bijia'" class="bijia-page">
        <h2>商品比价</h2>
        <form @submit.prevent="calculateBijia">
          <div class="form-group">
            <h3>商品1</h3>
            <input v-model="bijiaForm.a_name" placeholder="商品名称" required>
            <input v-model="bijiaForm.a_price" type="number" step="0.01" placeholder="总价" required>
            <input v-model="bijiaForm.a_per" type="number" step="0.01" placeholder="单位数量" required>
          </div>
          
          <div class="form-group">
            <h3>商品2</h3>
            <input v-model="bijiaForm.b_name" placeholder="商品名称" required>
            <input v-model="bijiaForm.b_price" type="number" step="0.01" placeholder="总价" required>
            <input v-model="bijiaForm.b_per" type="number" step="0.01" placeholder="单位数量" required>
          </div>
          
          <button type="submit">计算</button>
        </form>
        
        <div v-if="bijiaResult" class="result">
          <h3>比价结果：</h3>
          <p>{{ bijiaResult }}</p>
        </div>
      </div>

      <!-- 抽奖页面 -->
      <div v-if="currentPage === 'chouka'" class="chouka-page">
        <h2>抽奖</h2>
        <div v-if="!currentUser" class="login-prompt">
          <p>💡 请先登录以记录保底次数</p>
        </div>
        <form @submit.prevent="doChouka">
          <div class="form-group">
            <label>抽奖次数：</label>
            <input v-model="choukaForm.times" type="number" min="1" max="100" required>
          </div>
          <button type="submit">开始抽奖</button>
        </form>
        
        <div v-if="choukaResult.length > 0" class="result">
          <h3>抽奖结果：</h3>
          <div v-for="(item, index) in choukaResult" :key="index" class="chouka-item">
            <span v-if="item.includes('******')" class="star-6">{{ item }}</span>
            <span v-else-if="item.includes('*****')" class="star-5">{{ item }}</span>
            <span v-else class="star-4">{{ item }}</span>
          </div>
        </div>
      </div>

      <!-- 保底查询页面 -->
      <div v-if="currentPage === 'baodi'" class="baodi-page">
        <h2>保底查询</h2>
        <div v-if="!currentUser" class="login-prompt">
          <p>请先登录以查询保底信息</p>
        </div>
        <div v-else class="baodi-card">
          <h3>当前保底状态</h3>
          <div class="baodi-stats">
            <div class="stat-item">
              <span class="stat-label">保底计数:</span>
              <span class="stat-value">{{ baodiInfo.baodi }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">大保底计数:</span>
              <span class="stat-value">{{ baodiInfo.dabaodi }}</span>
            </div>
          </div>
          <button @click="loadBaodiInfo" class="refresh-btn">刷新保底信息</button>
        </div>
      </div>

      <!-- 刮刮乐页面 -->
      <div v-if="currentPage === 'scratch'" class="scratch-page">
        <h2>🎁 武器刮刮乐</h2>
        
        <!-- 状态信息 -->
        <div class="scratch-status">
          <div class="status-item">
            <span class="status-label">总卡片:</span>
            <span class="status-value">{{ scratchStatus.total_cards }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">已刮:</span>
            <span class="status-value">{{ scratchStatus.scratched_count }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">剩余:</span>
            <span class="status-value highlight">{{ scratchStatus.remaining_cards }}</span>
          </div>
        </div>
        
        <!-- 刮刮乐卡片 -->
        <div class="scratch-card-container">
          <div class="scratch-card" @click="doScratch" :class="{ disabled: scratchStatus.remaining_cards <= 0 }">
            <div class="scratch-cover" v-if="!scratchResult">
              <span class="scratch-text">🎯 点击刮开</span>
            </div>
            <div class="scratch-prize" v-else>
              <div class="prize-rarity" :class="`rarity-${scratchResult.rarity}`">
                {{ '*'.repeat(scratchResult.rarity) }}
              </div>
              <div class="prize-name">{{ scratchResult.name }}</div>
              <div class="prize-type">{{ scratchResult.weapon_type }}</div>
            </div>
          </div>
        </div>
        
        <!-- 结果消息 -->
        <div v-if="scratchMessage" :class="['message', scratchResult ? 'success' : 'error']">
          {{ scratchMessage }}
        </div>
        
        <!-- 重置按钮 -->
        <div class="scratch-actions">
          <button @click="resetScratch" class="btn-secondary">重新开始</button>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* 用户信息样式 */
.user-info {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  align-items: center;
}

.welcome-text {
  color: #333;
  font-weight: bold;
}

.logout-btn, .login-btn {
  background: #ff6b6b;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 10px;
  font-size: 12px;
}

.login-btn {
  background: #4ecdc4;
}

.logout-btn:hover, .login-btn:hover {
  opacity: 0.8;
}

/* 登录页面样式 */
.login-page {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
}

.login-form {
  background: #f8f9fa;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.login-form .form-group {
  margin-bottom: 20px;
}

.login-form label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

.login-form input {
  width: 100%;
  padding: 10px;
  border: 2px solid #e9ecef;
  border-radius: 5px;
  font-size: 16px;
}

.login-form input:focus {
  outline: none;
  border-color: #4ecdc4;
}

.button-group {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.btn-primary {
  background: #4ecdc4;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
}

.btn-secondary {
  background: #ff6b6b;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
}

.btn-primary:hover, .btn-secondary:hover {
  opacity: 0.8;
}

/* 消息样式 */
.message {
  margin-top: 15px;
  padding: 10px;
  border-radius: 5px;
  text-align: center;
  font-weight: bold;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

/* 保底卡片样式 */
.baodi-card {
  background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
  color: white;
  padding: 20px;
  border-radius: 10px;
  margin: 20px 0;
  text-align: center;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.baodi-stats {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin: 15px 0;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  margin-top: 5px;
}

.refresh-btn {
  background: rgba(255,255,255,0.2);
  color: white;
  border: 1px solid rgba(255,255,255,0.5);
  padding: 8px 16px;
  border-radius: 5px;
  cursor: pointer;
  margin-top: 10px;
}

.refresh-btn:hover {
  background: rgba(255,255,255,0.3);
}

/* 登录提示样式 */
.login-prompt {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  color: #856404;
  padding: 15px;
  border-radius: 5px;
  margin: 15px 0;
  text-align: center;
}

/* 刮刮乐页面样式 */
.scratch-page {
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
}

.scratch-status {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 30px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 10px;
}

.status-item {
  text-align: center;
}

.status-label {
  display: block;
  font-size: 14px;
  color: #666;
}

.status-value {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.status-value.highlight {
  color: #e74c3c;
}

.scratch-card-container {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.scratch-card {
  width: 200px;
  height: 250px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 15px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  transition: transform 0.3s, box-shadow 0.3s;
}

.scratch-card:hover:not(.disabled) {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0,0,0,0.3);
}

.scratch-card.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.scratch-cover {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.scratch-text {
  font-size: 20px;
  font-weight: bold;
  color: white;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.scratch-prize {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: white;
  padding: 20px;
}

.prize-rarity {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 10px;
}

.rarity-1 { color: #9e9e9e; }
.rarity-2 { color: #4caf50; }
.rarity-3 { color: #2196f3; }
.rarity-4 { color: #9c27b0; }
.rarity-5 { color: #ff9800; }

.prize-name {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.prize-type {
  font-size: 14px;
  color: #666;
}

.scratch-actions {
  text-align: center;
  margin-top: 20px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .user-info {
    position: static;
    justify-content: center;
    margin-bottom: 15px;
  }
  
  .baodi-stats {
    flex-direction: column;
    gap: 15px;
  }
  
  .button-group {
    flex-direction: column;
  }
}
.app {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

header {
  text-align: center;
  margin-bottom: 30px;
}

nav {
  margin-top: 20px;
}

nav button {
  margin: 0 10px;
  padding: 10px 20px;
  border: none;
  background: #007bff;
  color: white;
  cursor: pointer;
  border-radius: 5px;
}

nav button:hover {
  background: #0056b3;
}

.form-group {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

input {
  display: block;
  width: 100%;
  margin: 10px 0;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button[type="submit"] {
  padding: 10px 20px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button[type="submit"]:hover {
  background: #218838;
}

.result {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 5px;
}

.chouka-item {
  margin: 5px 0;
}

.star-6 {
  color: #e42e37ff;
  font-weight: bold;
  font-size: 28px;
}

.star-5 {
  color: #d4d800ff;
  font-weight: bold;
  font-size: 22px;
}

.star-4 {
  color: #5112e4ff;
  font-size: 16px;
}
</style>
