<script setup>
import { ref, onMounted } from 'vue'

// 后端API地址 - 适配main_api.py
const API_BASE = 'http://localhost:8888/api'

// 用户状态
const currentUser = ref(null)
const loginForm = ref({
  username: '',
  password: ''
})



// 抽奖功能相关状态
const choukaForm = ref({
  times: 10
})
const choukaResult = ref([])
const choukaStats = ref(null)

// 保底信息
const baodiInfo = ref({
  baodi: 0,
  dabaodi: 0
})

//<!-- 刮刮乐状态 -->
const scratchStatus = ref({
  total_cards: 0,
  remaining_cards: 0,
  scratched_count: 0,
  current_cards_count: 0
})
const scratchMessage = ref('')
const scratchSlots = ref([null, null, null, null])  // 四个刮刮乐槽位
const allScratched = ref(false)  // 是否全部刮完

// 当前页面状态
const currentPage = ref('home')

// 导航项目
const navItems = ref([
  { name: '首页', icon: '🏠', page: 'home' },
  { name: '抽奖', icon: '🎰', page: 'chouka' },
  { name: '保底查询', icon: '📊', page: 'baodi' },
  { name: '武器刮刮乐', icon: '🎁', page: 'scratch', onClick: loadScratchStatus }
])

// 登录状态
const loginMessage = ref('')
const isLoginSuccess = ref(false)



// 抽奖函数
async function doChouka() {
  console.log('🎰 开始抽奖，次数:', choukaForm.value.times)
  
  try {
    const formData = new FormData()
    formData.append('times', choukaForm.value.times)
    
    // 如果用户已登录，传递用户名用于记录保底
    if (currentUser.value) {
      formData.append('username', currentUser.value.username)
    }
    
    const response = await fetch(`${API_BASE}/chouka/do`, {
      method: 'POST',
      body: formData
    })
    
    const result = await response.json()
    console.log('📡 抽奖响应:', result)
    
    if (result.success) {
      choukaResult.value = result.data.results
      choukaStats.value = result.data.statistics
      loginMessage.value = result.message
      
      // 更新保底信息
      if (result.data.baodi_info) {
        baodiInfo.value = {
          baodi: result.data.baodi_info.current_baodi,
          dabaodi: result.data.baodi_info.current_dabaodi
        }
      }
    } else {
      loginMessage.value = result.message
      choukaResult.value = []
      choukaStats.value = null
    }
  } catch (error) {
    loginMessage.value = '网络错误，请检查后端服务是否启动'
    choukaResult.value = []
    choukaStats.value = null
  }
}

// 清空结果函数
function clearResults() {
  choukaResult.value = []
  choukaStats.value = null
  scratchMessage.value = ''
}

// 用户登录
async function doLogin() {
  console.log('🔐 尝试登录:', loginForm.value.username)
  
  if (!loginForm.value.username || !loginForm.value.password) {
    console.log('❌ 登录失败：用户名或密码为空')
    loginMessage.value = '请输入用户名和密码'
    isLoginSuccess.value = false
    return
  }

  try {
    const formData = new FormData()
    formData.append('username', loginForm.value.username)
    formData.append('password', loginForm.value.password)
    
    const response = await fetch(`${API_BASE}/user/login`, {
      method: 'POST',
      body: formData
    })
    
    const result = await response.json()
    console.log('📡 登录响应:', result)
    
    if (result.success) {
      currentUser.value = result.data.user
      loginMessage.value = result.message
      isLoginSuccess.value = true
      
      // 更新保底信息
      if (result.data.user) {
        baodiInfo.value = {
          baodi: result.data.user.baodi,
          dabaodi: result.data.user.dabaodi
        }
      }
      
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
    
    const response = await fetch(`${API_BASE}/user/register`, {
      method: 'POST',
      body: formData
    })
    
    const result = await response.json()
    
    if (result.success) {
      currentUser.value = result.data.user
      loginMessage.value = result.message
      isLoginSuccess.value = true
      
      // 更新保底信息
      if (result.data.user) {
        baodiInfo.value = {
          baodi: result.data.user.baodi,
          dabaodi: result.data.user.dabaodi
        }
      }
      
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
  clearResults()
}

// 加载保底信息
async function loadBaodiInfo() {
  if (!currentUser.value) return
  
  try {
    const response = await fetch(`${API_BASE}/user/baodi/${currentUser.value.username}`)
    const result = await response.json()
    
    if (result.success) {
      baodiInfo.value = {
        baodi: result.data.baodi,
        dabaodi: result.data.dabaodi
      }
    }
  } catch (error) {
    console.error('获取保底信息失败:', error)
  }
}

// 获取刮刮乐状态
async function loadScratchStatus() {
  console.log('🎁 加载刮刮乐状态...')
  try {
    const response = await fetch(`${API_BASE}/scratch/status`)
    const result = await response.json()
    console.log('📡 刮刮乐状态:', result)
    if (result.success) {
      scratchStatus.value = result.data
    }
  } catch (error) {
    console.error('❌ 获取刮刮乐状态失败:', error)
  }
}

// 刮开指定槽位的卡片
async function doScratch(slotIndex) {
  console.log('🎁 刮开槽位:', slotIndex + 1)
  
  // 如果该槽位已刮开或全部已刮完，则不执行
  if (scratchSlots.value[slotIndex] !== null || allScratched.value) {
    console.log('⏭️ 槽位已刮开或全部已刮完')
    return
  }
  
  try {
    const response = await fetch(`${API_BASE}/scratch/play`, {
      method: 'POST'
    })
    const result = await response.json()
    console.log('📡 刮卡响应:', result)
    
    if (result.success) {
      scratchSlots.value[slotIndex] = result.data.prize
      scratchStatus.value.remaining_cards = result.data.remaining_cards
      scratchStatus.value.scratched_count++
      
      // 检查是否全部刮完
      const allDone = scratchSlots.value.every(slot => slot !== null)
      allScratched.value = allDone
      
      console.log('✨ 获得武器:', result.data.prize?.name, '-', result.data.prize?.weapon_type)
    }
  } catch (error) {
    console.error('❌ 刮卡失败:', error)
  }
}

// 重置刮刮乐
async function resetScratch() {
  console.log('🔄 重置刮刮乐...')
  try {
    const response = await fetch(`${API_BASE}/scratch/reset`, {
      method: 'POST'
    })
    const result = await response.json()
    console.log('📡 重置响应:', result)
    
    if (result.success) {
      scratchMessage.value = result.message
      await loadScratchStatus()
      scratchSlots.value = [null, null, null, null]  // 清空四个槽位
      allScratched.value = false  // 重置全部刮完状态
    } else {
      scratchMessage.value = result.message
    }
  } catch (error) {
    console.error('❌ 重置失败:', error)
    scratchMessage.value = '重置失败，请检查后端服务'
  }
}

// 获取稀有度样式类
function getRarityClass(star) {
  const starNum = parseInt(star) || 4
  if (starNum >= 6) return 'rarity-legendary'
  if (starNum === 5) return 'rarity-epic'
  if (starNum === 4) return 'rarity-rare'
  return 'rarity-common'
}

// 组件挂载时检查用户状态
onMounted(() => {
  // 加载初始状态
  loadScratchStatus()
})
</script>

<template>
  <div class="app-container">
    <!-- 左侧侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <h1>🎮 小助手</h1>
      </div>
      <nav class="sidebar-nav">
        <button 
          v-for="item in navItems" 
          :key="item.page"
          @click="currentPage = item.page; clearResults(); item.onClick && item.onClick()"
          class="nav-btn"
          :class="{ active: currentPage === item.page }"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-text">{{ item.name }}</span>
        </button>
      </nav>
      <div class="sidebar-footer">
        <span v-if="currentUser" class="welcome-text">欢迎，{{ currentUser.username }}</span>
        <button v-if="currentUser" @click="logout" class="logout-btn">退出</button>
        <button v-else @click="currentPage = 'login'" class="login-btn">登录/注册</button>
      </div>
    </aside>

    <!-- 右侧主内容区域 -->
    <main class="main-content">
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
        
        <!-- 抽奖统计 -->
        <div v-if="choukaStats" class="chouka-stats">
          <div class="stats-grid">
            <div class="stat-card star-6">
              <div class="stat-number">{{ choukaStats.star_6 }}</div>
              <div class="stat-label">6星物品</div>
            </div>
            <div class="stat-card star-5">
              <div class="stat-number">{{ choukaStats.star_5 }}</div>
              <div class="stat-label">5星物品</div>
            </div>
            <div class="stat-card star-4">
              <div class="stat-number">{{ choukaStats.star_4 }}</div>
              <div class="stat-label">4星物品</div>
            </div>
            <div class="stat-card total">
              <div class="stat-number">{{ choukaStats.total }}</div>
              <div class="stat-label">总抽奖次数</div>
            </div>
          </div>
        </div>
        
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
        <h2>每日商店</h2>
        
        <!-- 状态信息 -->
        <div class="scratch-status-bar">
          <button @click="resetScratch" class="reset-btn">重新开始</button>
        </div>
        
        <!-- 四个刮刮乐槽位 -->
        <div class="scratch-slots-container">
          <div 
            v-for="(slot, index) in scratchSlots" 
            :key="index"
            class="scratch-slot"
            :class="[
              getRarityClass(slot?.star || 4),
              { scratched: slot !== null, disabled: allScratched && slot === null }
            ]"
            @click="doScratch(index)"
          >
            <!-- 武器图片区域 -->
            <div class="slot-image-area">
              <div v-if="slot === null" class="slot-placeholder">
                <div class="slot-animation">
                  <span>🎯</span>
                </div>
              </div>
              <div v-else class="slot-reveal-container">
                <img :src="`http://localhost:8888${slot.image_url}`" 
                     :alt="slot.name" class="slot-image slot-reveal" />
              </div>
            </div>
            
            <!-- 武器信息 -->
            <div class="slot-info" :class="{ 'slot-reveal': slot !== null }">
              <div class="slot-name">{{ slot?.name || '???' }}</div>
              <div class="slot-type">{{ slot?.weapon_type || '点击刮开' }}</div>
            </div>
          </div>
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
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 30px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.scratch-page h2 {
  text-align: center;
  margin-bottom: 20px;
  color: #fff;
  font-size: 26px;
  font-weight: 600;
  letter-spacing: 2px;
}

/* 刮刮乐状态栏 */
.scratch-status-bar {
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  padding: 14px 40px;
  border-radius: 30px;
  margin-bottom: 25px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.reset-btn {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  border: none;
  padding: 12px 32px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
}

.reset-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
}

.reset-btn:active {
  transform: translateY(0);
}

/* 四个刮刮乐槽位容器 */
.scratch-slots-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 28px;
  width: 100%;
}

/* 单个槽位样式 - 扑克牌比例 5:7 */
.scratch-slot {
  background: linear-gradient(145deg, #1e1e2e 0%, #141420 100%);
  border-radius: 22px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
  aspect-ratio: 5 / 7;
  min-width: 225px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.scratch-slot:hover:not(.disabled):not(.scratched) {
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5);
}

.scratch-slot.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.scratch-slot.scratched {
  cursor: default;
}

/* 稀有度底色 - 刮开后显示 */
.scratch-slot.rarity-legendary {
  background: linear-gradient(145deg, #4a3728 0%, #2d1f14 100%);
  box-shadow: 0 0 30px rgba(255, 215, 0, 0.25), 0 4px 20px rgba(0, 0, 0, 0.4);
  border-color: rgba(255, 215, 0, 0.3);
}

.scratch-slot.rarity-epic {
  background: linear-gradient(145deg, #3d2d5a 0%, #2a1f3d 100%);
  box-shadow: 0 0 30px rgba(153, 102, 255, 0.25), 0 4px 20px rgba(0, 0, 0, 0.4);
  border-color: rgba(153, 102, 255, 0.3);
}

.scratch-slot.rarity-rare {
  background: linear-gradient(145deg, #2d4a6e 0%, #1f3452 100%);
  box-shadow: 0 0 30px rgba(102, 179, 255, 0.2), 0 4px 20px rgba(0, 0, 0, 0.4);
  border-color: rgba(102, 179, 255, 0.3);
}

.scratch-slot.rarity-common {
  background: linear-gradient(145deg, #3d3d3d 0%, #2a2a2a 100%);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.35);
  border-color: rgba(153, 153, 153, 0.2);
}

/* 槽位图片区域 */
.slot-image-area {
  width: 100%;
  height: 70%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.25);
  position: relative;
}

.slot-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, rgba(255, 255, 255, 0.08) 0%, transparent 70%);
}

.slot-animation {
  text-align: center;
  animation: slotPulse 2s ease-in-out infinite;
}

.slot-animation span {
  font-size: 44px;
  opacity: 0.8;
}

@keyframes slotPulse {
  0%, 100% {
    opacity: 0.8;
    transform: scale(1);
  }
  50% {
    opacity: 0.4;
    transform: scale(1.05);
  }
}

/* 翻开动画容器 */
.slot-reveal-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: revealBg 0.5s ease-out forwards;
}

/* 翻开动画 - 图片渐变出现 */
.slot-image.slot-reveal {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  padding: 20px;
  animation: revealImage 0.8s ease-out 0.4s forwards;
  opacity: 0;
  transform: scale(0.8);
}

/* 翻开动画 - 信息渐变出现 */
.slot-info.slot-reveal {
  animation: revealInfo 0.7s ease-out 0.6s forwards;
  opacity: 0;
  transform: translateY(10px);
}

/* 底色渐变动画 */
@keyframes revealBg {
  0% {
    background: rgba(0,0,0,0.5);
  }
  100% {
    background: rgba(0,0,0,0.3);
  }
}

/* 图片翻转动画 */
@keyframes revealImage {
  0% {
    opacity: 0;
    transform: scale(0.8) rotateY(-180deg);
    filter: brightness(0);
  }
  50% {
    opacity: 0.5;
    transform: scale(0.95) rotateY(-90deg);
    filter: brightness(0.5);
  }
  100% {
    opacity: 1;
    transform: scale(1) rotateY(0);
    filter: brightness(1);
  }
}

/* 信息渐变动画 */
@keyframes revealInfo {
  0% {
    opacity: 0;
    transform: translateY(10px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 槽位信息 */
.slot-info {
  padding: 14px 14px 18px;
  text-align: center;
  background: rgba(0, 0, 0, 0.2);
}

.slot-name {
  font-size: 21px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.slot-type {
  font-size: 16px;
  color: #999;
}

/* 全部刮完提示 */
.scratch-complete {
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 15px;
  margin-top: 20px;
}

.complete-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.scratch-complete p {
  color: #fff;
  margin: 5px 0;
}

/* 旧样式兼容 */
.store-card-container {
  width: 100%;
  max-width: 400px;
  background: linear-gradient(135deg, #2d2d44 0%, #1a1a2e 100%);
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
  position: relative;
}

/* 稀有度徽章 */
.rarity-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.rarity-badge.rarity-legendary {
  background: linear-gradient(135deg, #ffd700 0%, #ff8c00 100%);
}

.rarity-badge.rarity-epic {
  background: linear-gradient(135deg, #9966ff 0%, #6633cc 100%);
}

.rarity-badge.rarity-rare {
  background: linear-gradient(135deg, #66b3ff 0%, #3366cc 100%);
}

.rarity-badge.rarity-common {
  background: linear-gradient(135deg, #999999 0%, #666666 100%);
}

.rarity-icon {
  color: white;
  font-size: 24px;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
}

/* 武器图片区域 */
.weapon-image-area {
  width: 100%;
  height: 200px;
  background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.scratch-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
}

.scratch-animation {
  text-align: center;
  animation: pulse 2s ease-in-out infinite;
}

.scratch-animation span {
  color: #fff;
  font-size: 24px;
  font-weight: bold;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.05);
  }
}

.weapon-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  padding: 20px;
}

/* 武器信息 */
.weapon-info {
  padding: 15px 20px;
  background: rgba(0,0,0,0.2);
}

.weapon-name {
  font-size: 18px;
  font-weight: bold;
  color: #fff;
  margin-bottom: 5px;
}

.weapon-type {
  font-size: 14px;
  color: #999;
}

/* 已获得武器列表 */
.weapon-collection {
  margin-top: 30px;
}

.weapon-collection h3 {
  color: #fff;
  margin-bottom: 15px;
  font-size: 18px;
}

.weapon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
}

.collection-card {
  background: linear-gradient(135deg, #2d2d44 0%, #1a1a2e 100%);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
  transition: transform 0.2s;
}

.collection-card:hover {
  transform: translateY(-3px);
}

.collection-rarity {
  padding: 5px 10px;
  font-size: 12px;
  font-weight: bold;
  color: #fff;
  text-align: center;
}

.collection-rarity.rarity-legendary {
  background: linear-gradient(135deg, #ffd700 0%, #ff8c00 100%);
}

.collection-rarity.rarity-epic {
  background: linear-gradient(135deg, #9966ff 0%, #6633cc 100%);
}

.collection-rarity.rarity-rare {
  background: linear-gradient(135deg, #66b3ff 0%, #3366cc 100%);
}

.collection-rarity.rarity-common {
  background: linear-gradient(135deg, #999999 0%, #666666 100%);
}

.collection-image {
  width: 100%;
  height: 100px;
  object-fit: contain;
  background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
  padding: 10px;
}

.collection-name {
  padding: 10px;
  font-size: 14px;
  font-weight: bold;
  color: #fff;
  text-align: center;
}

.collection-type {
  padding: 0 10px 10px;
  font-size: 12px;
  color: #999;
  text-align: center;
}
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



/* 抽奖统计样式 */
.chouka-stats {
  margin: 20px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
}

.stat-card {
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  color: white;
}

.stat-card.star-6 {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
}

.stat-card.star-5 {
  background: linear-gradient(135deg, #feca57 0%, #ff9ff3 100%);
}

.stat-card.star-4 {
  background: linear-gradient(135deg, #48dbfb 0%, #0abde3 100%);
}

.stat-card.total {
  background: linear-gradient(135deg, #485460 0%, #2c3e50 100%);
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
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

/* 整体布局容器 */
.app-container {
  display: flex;
  min-height: 100vh;
  font-family: Arial, sans-serif;
}

/* 左侧侧边栏 */
.sidebar {
  width: 220px;
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-header {
  padding: 0 20px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-header h1 {
  margin: 0;
  font-size: 18px;
  color: #fff;
  font-weight: 600;
}

/* 侧边栏导航 */
.sidebar-nav {
  flex: 1;
  padding: 15px 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  background: transparent;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  color: #999;
  font-size: 14px;
  transition: all 0.3s ease;
  text-align: left;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.nav-btn.active {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(139, 92, 246, 0.3) 100%);
  color: #fff;
  border-left: 3px solid #6366f1;
}

.nav-icon {
  font-size: 18px;
}

.nav-text {
  font-weight: 500;
}

/* 侧边栏底部用户信息 */
.sidebar-footer {
  padding: 15px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sidebar-footer .welcome-text {
  color: #999;
  font-size: 13px;
}

.sidebar-footer .logout-btn,
.sidebar-footer .login-btn {
  padding: 10px 15px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.sidebar-footer .logout-btn {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.sidebar-footer .logout-btn:hover {
  background: rgba(239, 68, 68, 0.3);
}

.sidebar-footer .login-btn {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: #fff;
}

.sidebar-footer .login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

/* 右侧主内容区域 */
.main-content {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
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
