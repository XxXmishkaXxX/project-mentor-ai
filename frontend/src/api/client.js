const BASE_URL = '/api'

export class ApiError extends Error {
  constructor(status, data) {
    super(data?.detail || `HTTP ${status}`)
    this.status = status
    this.data = data
  }
}

export async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`
  const config = {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  }

  if (config.body && typeof config.body === 'object' && !(config.body instanceof FormData)) {
    config.body = JSON.stringify(config.body)
  }

  if (config.body instanceof FormData) {
    delete config.headers['Content-Type']
  }

  const response = await fetch(url, config)

  if (!response.ok) {
    let data
    try {
      data = await response.json()
    } catch {
      data = { detail: response.statusText }
    }
    throw new ApiError(response.status, data)
  }

  if (response.status === 204) return null

  return response.json()
}

export async function streamRequest(path, body) {
  const url = `${BASE_URL}${path}`
  const response = await fetch(url, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    let data
    try {
      data = await response.json()
    } catch {
      data = { detail: response.statusText }
    }
    throw new ApiError(response.status, data)
  }

  return response
}
