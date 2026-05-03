import { request } from './client.js'

export function login(email, password) {
  return request('/auth/login', {
    method: 'POST',
    body: { email, password },
  })
}

export function register(username, email, password) {
  return request('/auth/register', {
    method: 'POST',
    body: { username, email, password },
  })
}

export function logout() {
  return request('/auth/logout', { method: 'POST' })
}

export function getMe() {
  return request('/users/me')
}
