<script setup>
import { onMounted, ref, watch } from 'vue'
import api from '../api'

const CATEGORIES = ['全部', '历史', '美食', '文化', '摄影']

const items = ref([])
const total = ref(0)
const page = ref(1)
const perPage = 9
const q = ref('')
const category = ref('全部')
const loading = ref(false)

async function fetchList() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: perPage }
    if (q.value.trim()) params.q = q.value.trim()
    if (category.value !== '全部') params.category = category.value
    const { data } = await api.get('/attractions', { params })
    items.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function search() {
  page.value = 1
  fetchList()
}

function pickCategory(c) {
  category.value = c
  page.value = 1
  fetchList()
}

const totalPages = () => Math.max(1, Math.ceil(total.value / perPage))

watch(page, fetchList)
onMounted(fetchList)
</script>

<template>
  <div class="container page">
    <section class="hero">
      <h1>发现澳门</h1>
      <p class="muted">历史街巷 · 葡韵风情 · 地道美食，一站式规划你的澳门之旅</p>
    </section>

    <div class="toolbar">
      <div class="search-box">
        <input
          v-model="q"
          class="input"
          placeholder="搜索景点，如：大三巴、蛋挞…"
          @keyup.enter="search"
        />
        <button class="btn btn-primary" @click="search">搜索</button>
      </div>
      <div class="cat-row">
        <button
          v-for="c in CATEGORIES"
          :key="c"
          class="chip"
          :class="{ on: category === c }"
          @click="pickCategory(c)"
        >
          {{ c }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="muted center">加载中…</div>

    <div v-else-if="items.length" class="grid">
      <router-link
        v-for="a in items"
        :key="a.id"
        :to="`/attractions/${a.id}`"
        class="card spot"
      >
        <div class="thumb">
          <img :src="a.image" :alt="a.name" loading="lazy" />
          <span class="tag cat">{{ a.category }}</span>
        </div>
        <div class="spot-body">
          <div class="spot-head">
            <h3>{{ a.name }}</h3>
            <span class="rating">★ {{ a.rating.toFixed(1) }}</span>
          </div>
          <p class="brief muted">{{ a.brief }}</p>
        </div>
      </router-link>
    </div>
    <p v-else class="muted center">没有找到相关景点，换个关键词试试。</p>

    <div v-if="totalPages() > 1" class="pager">
      <button class="btn btn-ghost" :disabled="page <= 1" @click="page--">
        上一页
      </button>
      <span class="muted">{{ page }} / {{ totalPages() }}</span>
      <button
        class="btn btn-ghost"
        :disabled="page >= totalPages()"
        @click="page++"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<style scoped>
.page {
  padding-bottom: 48px;
}

.hero {
  padding: 44px 0 24px;
}

.hero h1 {
  font-size: 32px;
  margin: 0 0 8px;
}

.toolbar {
  margin-bottom: 24px;
}

.search-box {
  display: flex;
  gap: 10px;
  max-width: 560px;
  margin-bottom: 14px;
}

.cat-row {
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

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

@media (max-width: 900px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 560px) {
  .grid {
    grid-template-columns: 1fr;
  }
}

.spot {
  transition: transform 0.2s;
}

.spot:hover {
  transform: translateY(-4px);
}

.thumb {
  position: relative;
  aspect-ratio: 4 / 3;
  background: #eee;
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cat {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(255, 255, 255, 0.92);
}

.spot-body {
  padding: 14px 16px 16px;
}

.spot-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.spot-head h3 {
  margin: 0;
  font-size: 16px;
}

.rating {
  color: #f0a020;
  font-size: 13px;
  font-weight: 600;
}

.brief {
  font-size: 13px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pager {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
}

.center {
  text-align: center;
  padding: 60px 0;
}
</style>
