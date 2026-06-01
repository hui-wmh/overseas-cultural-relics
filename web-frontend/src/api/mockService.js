import axios from 'axios'

const request = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 5000
})

const ok = (res) => res.data

export const getArtifacts = (params) => {
  return request.get('/api/artifacts', { params }).then(ok)
}

export const getArtifactDetail = (id) => {
  return request.get(`/api/artifacts/${id}`).then(ok)
}

export const getArtifactRecommendations = (id, params) => {
  return request.get(`/api/artifacts/${id}/recommendations`, { params }).then(ok)
}

export const searchArtifacts = (params) => {
  return request.get('/api/artifacts/search', { params }).then(ok)
}

export const exportArtifacts = (params) => {
  return request.get('/api/artifacts/export', { params }).then(ok)
}

export const getArtifactById = getArtifactDetail

export const getMuseums = (params) => {
  return request.get('/api/museums', { params }).then(ok)
}

export const getMuseumDetail = (id) => {
  return request.get(`/api/museums/${id}`).then(ok)
}

export const getMuseumById = getMuseumDetail

export const getDynasties = () => {
  return request.get('/api/dynasties').then(ok)
}

export const getTypes = () => {
  return request.get('/api/types').then(ok)
}

export const getArtifactTypes = getTypes

export const getMaterials = () => {
  return request.get('/api/materials').then(ok)
}

export const getArtists = (params) => {
  return request.get('/api/artists', { params }).then(ok)
}

export const register = (data) => {
  return request.post('/api/auth/register', data).then(ok)
}

export const login = (data) => {
  return request.post('/api/auth/login', data).then(ok)
}

export const getProfile = (token) => {
  return request.get('/api/auth/profile', {
    headers: {
      Authorization: token
    }
  }).then(ok)
}

export const getComments = (params) => {
  return request.get('/api/comments', { params }).then(ok)
}

export const addComment = (data) => {
  return request.post('/api/comments', data).then(ok)
}

export const postComment = addComment

export const askQuestion = (data) => {
  return request.post('/api/qa/ask', data).then(ok)
}

export const getQaHistory = (params) => {
  return request.get('/api/qa/history', { params }).then(ok)
}

export const getQaMessage = (id) => {
  return request.get(`/api/qa/messages/${id}`).then(ok)
}

export const getHotQuestions = (params) => {
  return request.get('/api/qa/hot', { params }).then(ok)
}

export const getArtifactGraph = (id) => {
  return request.get(`/api/graph/artifact/${id}`).then(ok)
}

export const getMuseumGraph = (id) => {
  return request.get(`/api/graph/museum/${id}`).then(ok)
}

export const searchGraph = (params) => {
  return request.get('/api/graph/search', { params }).then(ok)
}

export const getMuseumMapData = () => {
  return request.get('/api/museums').then(ok)
}

export const getDashboardStats = () => {
  return request.get('/api/stats/dashboard').then(ok)
}