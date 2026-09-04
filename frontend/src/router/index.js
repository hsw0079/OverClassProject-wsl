import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { guest: true }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/qr/:id',
    name: 'QRPass',
    component: () => import('../views/QRPass.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/nav',
    name: 'Navigation',
    component: () => import('../views/Navigation.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/nav/:id',
    name: 'NavigationDetail',
    component: () => import('../views/NavigationDetail.vue'),
    meta: { requiresAuth: true }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.guest && token) {
    next('/')
  } else {
    next()
  }
})

export default router