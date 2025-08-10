
// src/api.js
import axios from 'axios'
import Cookies from 'js-cookie'

const API = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true,
})

API.interceptors.request.use((config) => {
  const token = Cookies.get('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default API
