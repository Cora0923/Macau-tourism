import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import AttractionsView from '../views/AttractionsView.vue'
import AttractionDetailView from '../views/AttractionDetailView.vue'
import RoutePlannerView from '../views/RoutePlannerView.vue'
import MyRoutesView from '../views/MyRoutesView.vue'

const routes = [
  { path: '/', redirect: '/attractions' },
  { path: '/login', component: LoginView },
  { path: '/attractions', component: AttractionsView },
  { path: '/attractions/:id', component: AttractionDetailView },
  {
    path: '/planner',
    component: RoutePlannerView,
    meta: { requiresAuth: true },
  },
  {
    path: '/my-routes',
    component: MyRoutesView,
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !localStorage.getItem('token')) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
})

export default router
