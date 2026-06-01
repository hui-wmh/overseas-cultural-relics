import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: JSON.parse(localStorage.getItem('userInfo') || '{}'),
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
  },
  actions: {
    setUser(data) {
      this.token = data.token
      this.userInfo = {
        id: data.userId || data.id,
        username: data.username,
        nickname: data.nickname || data.username,
        email: data.email || '',
        phone: data.phone || '',
        avatar: data.avatar || '',
      }
      localStorage.setItem('token', data.token)
      localStorage.setItem('userInfo', JSON.stringify(this.userInfo))
    },
    updateInfo(info) {
      this.userInfo = { ...this.userInfo, ...info }
      localStorage.setItem('userInfo', JSON.stringify(this.userInfo))
    },
    logout() {
      this.token = ''
      this.userInfo = {}
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
    },
  },
})