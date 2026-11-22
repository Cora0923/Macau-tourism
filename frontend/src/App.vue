<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { clearSession, getUser } from './api'

const router = useRouter()
const user = ref(getUser())

// 路由切换时刷新登录态（登录页登录成功后跳转会触发）
router.afterEach(() => {
  user.value = getUser()
})

onMounted(() => {
  user.value = getUser()
})

const isLoggedIn = computed(() => !!user.value)

function logout() {
  clearSession()
  user.value = null
  router.push('/login')
}
</script>

<template>
  <div>
    <header class="navbar">
      <div class="container nav-inner">
        <router-link to="/attractions" class="logo">
          <span class="logo-mark">澳</span>
          <span class="logo-text">澳门文旅导航</span>
        </router-link>
        <nav class="nav-links">
          <router-link to="/attractions" active-class="active">景点</router-link>
          <router-link to="/planner" active-class="active">路线规划</router-link>
          <router-link v-if="isLoggedIn" to="/my-routes" active-class="active">
            我的路线
          </router-link>
        </nav>
        <div class="nav-user">
          <template v-if="isLoggedIn">
            <span class="greeting">你好，{{ user.name }}</span>
            <button class="btn btn-ghost" @click="logout">退出</button>
          </template>
          <router-link v-else to="/login" class="btn btn-primary">
            登录 / 注册
          </router-link>
        </div>
      </div>
    </header>
    <main>
      <router-view />
    </main>
    <footer class="footer muted">
      澳门文旅导航平台 · Vue3 + Flask + SQLite
    </footer>
  </div>
</template>

<style scoped>
.navbar {
  background: #fff;
  border-bottom: 1px solid var(--line);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-inner {
  display: flex;
  align-items: center;
  gap: 28px;
  height: 60px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 17px;
}

.logo-mark {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.nav-links {
  display: flex;
  gap: 22px;
  flex: 1;
}

.nav-links a {
  font-size: 14px;
  color: var(--muted);
  padding: 4px 2px;
  border-bottom: 2px solid transparent;
}

.nav-links a.active {
  color: var(--ink);
  border-bottom-color: var(--primary);
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.greeting {
  font-size: 13px;
  color: var(--muted);
}

.footer {
  text-align: center;
  padding: 32px 0 24px;
  font-size: 12px;
}
</style>
