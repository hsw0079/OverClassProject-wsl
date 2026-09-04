import { defineStore } from 'pinia'
import axios from 'axios'

const API = axios.create({ baseURL: '/api' })

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null
  }),
  getters: {
    isLoggedIn: (state) => !!state.token
  },
  actions: {
    async login(username, password) {
      console.log('[Auth] POST /auth/login/'); const { data } = await API.post('/auth/login/', { username, password }); console.log('[Auth] response:', data)
      this.token = data.token
      localStorage.setItem('token', data.token)
      API.defaults.headers.common['Authorization'] = 'Token ' + data.token
      await this.fetchUser()
    },
    async register(username, password) {
      console.log('[Auth] POST /auth/register/'); const { data } = await API.post('/auth/register/', { username, password }); console.log('[Auth] response:', data)
      this.token = data.token
      localStorage.setItem('token', data.token)
      API.defaults.headers.common['Authorization'] = 'Token ' + data.token
      await this.fetchUser()
    },
    async fetchUser() {
      console.log('[Auth] GET /auth/user/'); const { data } = await API.get('/auth/user/'); console.log('[Auth] user:', data)
      this.user = data
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      delete API.defaults.headers.common['Authorization']
    },
    init() {
      if (this.token) {
        API.defaults.headers.common['Authorization'] = 'Token ' + this.token
      }
    }
  }
})