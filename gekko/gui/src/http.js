import axios from 'axios'

export const HTTP = axios.create({
  baseURL: process.env.NODE_ENV === 'development' ? 'http://localhost:8050' : `http://${location.hostname}:${location.port}`,
  headers: { 'Access-Control-Allow-Origin': '*' }
})
