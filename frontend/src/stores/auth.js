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
      const { data } = await API.post('/auth/login/', { username, password })
      this.token = data.token
      localStorage.setItem('token', data.token)
      API.defaults.headers.common['Authorization'] = 'Token ' + data.token
      await this.fetchUser()
    },
    async register(username, password) {
      const { data } = await API.post('/auth/register/', { username, password })
      this.token = data.token
      localStorage.setItem('token', data.token)
      API.defaults.headers.common['Authorization'] = 'Token ' + data.token
      await this.fetchUser()
    },
    async fetchUser() {
      const { data } = await API.get('/auth/user/')
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