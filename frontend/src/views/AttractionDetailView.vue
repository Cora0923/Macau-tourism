<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'

const route = useRoute()
const spot = ref(null)
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get(`/attractions/${route.params.id}`)
    spot.value = data
  } catch (e) {
    error.value = e.response?.data?.error || '加载失败'
  }
})
</script>

<template>
  <div class="container page">
    <p v-if="error" class="error-text center">{{ error }}</p>

    <template v-else-if="spot">
      <router-link to="/attractions" class="back muted">← 返回景点列表</router-link>

      <div class="detail card">
        <div class="banner">
          <img :src="spot.image" :alt="spot.name" />
        </div>
        <div class="body">
          <div class="head">
            <div>
              <h1>{{ spot.name }}</h1>
              <div class="meta">
                <span class="tag">{{ spot.category }}</span>
                <span class="rating">★ {{ spot.rating.toFixed(1) }}</span>
              </div>
            </div>
            <router-link to="/planner" class="btn btn-primary">
              加入行程规划
            </router-link>
          </div>

          <p class="brief">{{ spot.brief }}</p>

          <div class="info-grid">
            <div class="info-item">
              <span class="label muted">开放时间</span>
              <span>{{ spot.open_hours }}</span>
            </div>
            <div class="info-item">
              <span class="label muted">门票</span>
              <span>{{ spot.ticket }}</span>
            </div>
            <div class="info-item">
              <span class="label muted">建议游览</span>
              <span>约 {{ spot.duration_min }} 分钟</span>
            </div>
            <div class="info-item">
              <span class="label muted">坐标</span>
              <span>{{ spot.lat.toFixed(4) }}, {{ spot.lng.toFixed(4) }}</span>
            </div>
          </div>

          <section v-if="spot.history" class="history">
            <h2>历史沿革</h2>
            <p>{{ spot.history }}</p>
          </section>
        </div>
      </div>
    </template>

    <p v-else class="muted center">加载中…</p>
  </div>
</template>

<style scoped>
.page {
  padding: 24px 20px 48px;
}

.back {
  display: inline-block;
  font-size: 13px;
  margin-bottom: 16px;
}

.center {
  text-align: center;
  padding: 60px 0;
}

.banner {
  aspect-ratio: 21 / 9;
  background: #eee;
}

.banner img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.body {
  padding: 28px 32px 36px;
}

.head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 14px;
}

.head h1 {
  font-size: 26px;
  margin: 0 0 8px;
}

.meta {
  display: flex;
  gap: 10px;
  align-items: center;
}

.rating {
  color: #f0a020;
  font-weight: 600;
  font-size: 14px;
}

.brief {
  font-size: 15px;
  line-height: 1.7;
  margin-bottom: 24px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
  padding: 18px;
  background: var(--bg);
  border-radius: 12px;
  margin-bottom: 28px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 14px;
}

.info-item .label {
  font-size: 12px;
}

.history h2 {
  font-size: 18px;
  margin: 0 0 10px;
}

.history p {
  line-height: 1.9;
  color: #4a4a4a;
}
</style>
