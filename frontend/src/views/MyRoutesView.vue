<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'

const routes = ref([])
const loading = ref(true)
const error = ref('')
const expandedId = ref(null)

function parseStops(r) {
  try {
    return JSON.parse(r.stops)
  } catch {
    return []
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get('/routes')
    routes.value = data.map((r) => ({ ...r, stopList: parseStops(r) }))
  } catch (e) {
    error.value = e.response?.data?.error || '加载失败'
  } finally {
    loading.value = false
  }
})

function toggle(id) {
  expandedId.value = expandedId.value === id ? null : id
}
</script>

<template>
  <div class="container page">
    <h1>我的路线</h1>
    <p class="muted sub">已保存的游览路线，可随时回顾</p>

    <p v-if="loading" class="muted center">加载中…</p>
    <p v-else-if="error" class="error-text center">{{ error }}</p>

    <template v-else-if="routes.length">
      <div v-for="r in routes" :key="r.id" class="card route-card">
        <button class="route-head" @click="toggle(r.id)">
          <div>
            <h3>{{ r.name }}</h3>
            <p class="muted meta">
              {{ r.stopList.length }} 站 · {{ r.total_distance_km }} km ·
              约 {{ Math.floor(r.total_minutes / 60) }} 小时
              {{ r.total_minutes % 60 }} 分钟
            </p>
          </div>
          <span class="arrow" :class="{ open: expandedId === r.id }">⌄</span>
        </button>
        <ol v-if="expandedId === r.id" class="stops">
          <li v-for="(s, i) in r.stopList" :key="i">
            <span class="idx">{{ i + 1 }}</span>
            <router-link :to="`/attractions/${s.id}`">{{ s.name }}</router-link>
            <span class="tag">{{ s.category }}</span>
          </li>
        </ol>
      </div>
    </template>

    <div v-else class="empty center">
      <p class="muted">还没有保存的路线</p>
      <router-link to="/planner" class="btn btn-primary">去规划一条</router-link>
    </div>
  </div>
</template>

<style scoped>
.page {
  padding: 24px 20px 48px;
}

h1 {
  font-size: 26px;
  margin: 8px 0 6px;
}

.sub {
  font-size: 13px;
  margin-bottom: 20px;
}

.center {
  text-align: center;
  padding: 60px 0;
}

.route-card {
  margin-bottom: 14px;
}

.route-head {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: none;
  background: none;
  padding: 18px 22px;
  text-align: left;
}

.route-head h3 {
  margin: 0 0 4px;
  font-size: 16px;
}

.meta {
  font-size: 12px;
}

.arrow {
  font-size: 18px;
  color: var(--muted);
  transition: transform 0.2s;
}

.arrow.open {
  transform: rotate(180deg);
}

.stops {
  list-style: none;
  margin: 0;
  padding: 0 22px 18px;
}

.stops li {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  font-size: 14px;
}

.idx {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--primary);
  color: #fff;
  font-size: 11px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: none;
}

.empty .btn {
  margin-top: 14px;
  display: inline-block;
}
</style>
