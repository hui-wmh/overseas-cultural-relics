import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/',              name: 'Home',           component: () => import('../views/HomeView.vue') },
  { path: '/artifacts',     name: 'Artifacts',      component: () => import('../views/ArtifactsView.vue') },
  { path: '/artifacts/:id', name: 'ArtifactDetail', component: () => import('../views/ArtifactDetailView.vue') },
  { path: '/search',        name: 'Search',         component: () => import('../views/SearchView.vue') },
  { path: '/graph',         name: 'Graph',          component: () => import('../views/GraphView.vue') },
  { path: '/timeline',      name: 'Timeline',       component: () => import('../views/TimelineView.vue') },
  { path: '/map',           name: 'Map',            component: () => import('../views/MapView.vue') },
  { path: '/dashboard',     name: 'Dashboard',      component: () => import('../views/DashboardView.vue') },
  { path: '/qa',            name: 'QA',             component: () => import('../views/QAView.vue') },
  { path: '/login',         name: 'Login',          component: () => import('../views/LoginView.vue') },
  { path: '/profile',       name: 'Profile',        component: () => import('../views/ProfileView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router