<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import api from '../api'

const INTEREST_OPTIONS = ['历史', '美食', '文化', '摄影']
const TIME_OPTIONS = [
  { label: '半天（4小时）', value: 240 },
  { label: '一天（8小时）', value: 480 },
  { label: '两天（16小时）', value: 960 },
]

const interests = ref([])
const timeBudget = ref(240)
const planning = ref(false)
const saving = ref(false)
const error = ref('')
const notice = ref('')
const plan = ref(null)

let map = null
let layerGroup = null

onMounted(() => {
  map = L.map('map').setView([22.1735, 113.545], 13)
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map)
  layerGroup = L.layerGroup().addTo(map)
})

onBeforeUnmount(() => {
  map?.remove()
  map = null
})

function toggleInterest(tag) {
  const i = interests.value.indexOf(tag)
  if (i >= 0) interests.value.splice(i, 1)
  else interests.value.push(tag)
}

function numberIcon(n) {
  return L.divIcon({
    className: 'num-marker',
    html: `<span>${n}</span>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  })
}

function drawPlan(data) {
  layerGroup.clearLayers()
  const pts = []

  // 起点
  const start = [data.start.lat, data.start.lng]
  L.circleMarker(start, {
    radius: 8,
    color: '#2b7de9',
    fillColor: '#2b7de9',
    fillOpacity: 1,
  })
    .addTo(layerGroup)
    .bindPopup('起点：议事亭前地')
  pts.push(start)

  data.stops.forEach((s, i) => {
    const p = [s.lat, s.lng]
    L.marker(p, { icon: numberIcon(i + 1) })
      .addTo(layerGroup)
      .bindPopup(
        `<b>${i + 1}. ${s.name}</b><br>${s.category} · 建议游览 ${s.duration_min} 分钟`,
      )
    pts.push(p)
  })

  if (pts.length > 1) {
    L.polyline(pts, { color: '#c8102e', weight: 4, opacity: 0.75 }).addTo(
      layerGroup,
    )
    map.fitBounds(L.latLngBounds(pts).pad(0.15))
  }
}

async function generate() {
  error.value = ''
  notice.value = ''
  planning.value = true
  try {
    const { data } = await api.post('/routes/plan', {
      interests: interests.value,
      time_budget: timeBudget.value,
    })
    plan.value = data
    drawPlan(data)
    if (!data.stops.length) {
      notice.value = '时间预算太短，未能安排任何景点，试试增加预算。'
    }
  } catch (e) {
    error.value = e.response?.data?.error || '规划失败，请稍后重试'
  } finally {
    planning.value = false
  }
}

async function save() {
  if (!plan.value?.stops?.length) return
  saving.value = true
  error.value = ''
  notice.value = ''
  try {
    const name = `澳门${interests.value.join('·') || '精选'}之旅（${plan.value.stops.length}站）`
    await api.post('/routes', {
      name,
      stops: plan.value.stops,
      total_distance_km: plan.value.total_distance_km,
      total_minutes: plan.value.total_minutes,
    })
    notice.value = '已保存到「我的路线」'
  } catch (e) {
    error.value = e.response?.data?.error || '保存失败'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="container page">
    <h1>路线规划</h1>
    <p class="muted sub">选择兴趣标签与时间预算，从议事亭前地出发，智能生成游览顺序</p>

    <div class="panel card">
      <div class="row">
        <span class="label">兴趣偏好</span>
        <div class="chip-row">
          <button
            v-for="tag in INTEREST_OPTIONS"
            :key="tag"
            class="chip"
            :class="{ on: interests.includes(tag) }"
            @click="toggleInterest(tag)"
          >
            {{ tag }}
          </button>
          <span class="muted hint">不选则覆盖全部景点</span>
        </div>
      </div>
      <div class="row">
        <span class="label">时间预算</span>
        <div class="chip-row">
          <button
            v-for="t in TIME_OPTIONS"
            :key="t.value"
            class="chip"
            :class="{ on: timeBudget === t.value }"
            @click="timeBudget = t.value"
          >
            {{ t.label }}
          </button>
        </div>
      </div>
      <div class="actions">
        <button class="btn btn-primary" :disabled="planning" @click="generate">
          {{ planning ? '规划中…' : '生成路线' }}
        </button>
        <button
          v-if="plan?.stops?.length"
          class="btn btn-ghost"
          :disabled="saving"
          @click="save"
        >
          {{ saving ? '保存中…' : '保存这条路线' }}
        </button>
        <span v-if="error" class="error-text">{{ error }}</span>
        <span v-if="notice" class="ok">{{ notice }}</span>
      </div>
    </div>

    <div class="planner-body">
      <div id="map" class="card"></div>

      <aside v-if="plan" class="plan-list card">
        <h2>行程（{{ plan.stops.length }} 站）</h2>
        <p class="muted total">
          总里程约 {{ plan.total_distance_km }} km · 预计用时
          {{ Math.floor(plan.total_minutes / 60) }} 小时 {{ plan.total_minutes % 60 }} 分钟
        </p>
        <ol>
          <li v-for="(s, i) in plan.stops" :key="s.id">
            <div class="stop-head">
              <span class="idx">{{ i + 1 }}</span>
              <router-link :to="`/attractions/${s.id}`" class="stop-name">
                {{ s.name }}
              </router-link>
              <span class="tag">{{ s.category }}</span>
            </div>
            <p class="muted stop-meta">
              游览 {{ s.duration_min }} 分钟
              <template v-if="i > 0 || true">
                · 距上站 {{ s.leg_km }} km（步行约 {{ s.travel_min }} 分钟）
              </template>
            </p>
          </li>
        </ol>
      </aside>
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

.panel {
  padding: 20px 24px;
  margin-bottom: 20px;
}

.row {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 14px;
}

.label {
  flex: none;
  width: 64px;
  font-size: 14px;
  font-weight: 600;
  padding-top: 6px;
}

.chip-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
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

.hint {
  font-size: 12px;
}

.actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 6px;
}

.ok {
  color: #1a9c54;
  font-size: 13px;
}

.planner-body {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 20px;
  align-items: start;
}

@media (max-width: 900px) {
  .planner-body {
    grid-template-columns: 1fr;
  }
}

#map {
  height: 520px;
  z-index: 1;
}

.plan-list {
  padding: 18px 20px;
  max-height: 520px;
  overflow: auto;
}

.plan-list h2 {
  font-size: 16px;
  margin: 0 0 4px;
}

.total {
  font-size: 12px;
  margin-bottom: 12px;
}

.plan-list ol {
  list-style: none;
  margin: 0;
  padding: 0;
}

.plan-list li {
  border-top: 1px solid var(--line);
  padding: 10px 0;
}

.stop-head {
  display: flex;
  align-items: center;
  gap: 8px;
}

.idx {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--primary);
  color: #fff;
  font-size: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: none;
}

.stop-name {
  font-weight: 600;
  font-size: 14px;
}

.stop-name:hover {
  color: var(--primary);
}

.stop-meta {
  font-size: 12px;
  margin: 4px 0 0 30px;
}

:global(.num-marker) {
  background: transparent;
}

:global(.num-marker span) {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #c8102e;
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  border: 2px solid #fff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}
</style>
