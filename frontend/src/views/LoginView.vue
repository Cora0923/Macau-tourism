<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { setSession } from '../api'

const router = useRouter()
const route = useRoute()

const INTEREST_OPTIONS = ['历史', '美食', '文化', '摄影']

const mode = ref('login') // login | register
const loading = ref(false)
const error = ref('')

const form = reactive({
  name: '',
  email: '',
  password: '',
  interests: [],
})

function toggleInterest(tag) {
  const i = form.interests.indexOf(tag)
  if (i >= 0) form.interests.splice(i, 1)
  else form.interests.push(tag)
}

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const url = mode.value === 'login' ? '/auth/login' : '/auth/register'
    const payload =
      mode.value === 'login'
        ? { email: form.email, password: form.password }
        : { ...form }
    const { data } = await api.post(url, payload)
    setSession(data.token, data.user)
    router.push(route.query.redirect || '/attractions')
  } catch (e) {
    error.value = e.response?.data?.error || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card card">
      <h1 class="title">{{ mode === 'login' ? '欢迎回来' : '创建账号' }}</h1>
      <p class="subtitle muted">
        {{ mode === 'login' ? '登录后可规划并保存你的澳门路线' : '注册即享个性化路线规划' }}
      </p>

      <div class="mode-tabs">
        <button
          :class="{ active: mode === 'login' }"
          @click="mode = 'login'; error = ''"
        >
          登录
        </button>
        <button
          :class="{ active: mode === 'register' }"
          @click="mode = 'register'; error = ''"
        >
          注册
        </button>
      </div>

      <form @submit.prevent="submit">
        <div v-if="mode === 'register'" class="field">
          <label>姓名</label>
          <input v-model.trim="form.name" class="input" placeholder="你的称呼" required />
        </div>
        <div class="field">
          <label>邮箱</label>
          <input
            v-model.trim="form.email"
            class="input"
            type="email"
            placeholder="you@example.com"
            required
          />
        </div>
        <div class="field">
          <label>密码</label>
          <input
            v-model="form.password"
            class="input"
            type="password"
            placeholder="至少 6 位"
            minlength="6"
            required
          />
        </div>

        <div v-if="mode === 'register'" class="field">
          <label>兴趣偏好（用于路线推荐，可多选）</label>
          <div class="interest-row">
            <button
              v-for="tag in INTEREST_OPTIONS"
              :key="tag"
              type="button"
              class="chip"
              :class="{ on: form.interests.includes(tag) }"
              @click="toggleInterest(tag)"
            >
              {{ tag }}
            </button>
          </div>
        </div>

        <p v-if="error" class="error-text">{{ error }}</p>

        <button class="btn btn-primary submit" :disabled="loading">
          {{ loading ? '提交中…' : mode === 'login' ? '登录' : '注册并登录' }}
        </button>
      </form>

      <p class="demo muted">演示账号：t@t.com / 123456</p>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  padding: 60px 20px;
}

.auth-card {
  width: 400px;
  max-width: 100%;
  padding: 36px 32px;
}

.title {
  font-size: 24px;
  margin: 0 0 6px;
}

.subtitle {
  font-size: 13px;
  margin-bottom: 22px;
}

.mode-tabs {
  display: flex;
  background: var(--bg);
  border-radius: 10px;
  padding: 4px;
  margin-bottom: 22px;
}

.mode-tabs button {
  flex: 1;
  border: none;
  background: transparent;
  padding: 8px 0;
  border-radius: 8px;
  font-size: 14px;
  color: var(--muted);
}

.mode-tabs button.active {
  background: #fff;
  color: var(--ink);
  font-weight: 600;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.field {
  margin-bottom: 16px;
}

.field label {
  display: block;
  font-size: 13px;
  margin-bottom: 6px;
  color: var(--ink);
}

.interest-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.chip {
  border: 1px solid var(--line);
  background: #fff;
  border-radius: 999px;
  padding: 6px 16px;
  font-size: 13px;
  color: var(--muted);
  transition: 0.2s;
}

.chip.on {
  border-color: var(--primary);
  background: #fbeef0;
  color: var(--primary);
}

.submit {
  width: 100%;
  margin-top: 8px;
  padding: 12px;
  font-size: 15px;
}

.demo {
  margin-top: 18px;
  text-align: center;
  font-size: 12px;
}
</style>
