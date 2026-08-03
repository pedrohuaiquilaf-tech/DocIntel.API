async function request(path, { method = 'GET', body, headers = {}, parseJson = true } = {}) {
  const options = {
    method,
    headers: {
      ...(body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
      ...headers,
    },
  }

  if (body !== undefined) {
    options.body = body instanceof FormData ? body : JSON.stringify(body)
  }

  const response = await fetch(path, options)
  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(errorText || 'Request failed')
  }

  if (!parseJson) {
    return response
  }

  return response.json()
}

export async function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request('/api/documents/upload', { method: 'POST', body: formData, parseJson: true })
}

export async function createChatSession(documentId) {
  return request('/api/chat/sessions', { method: 'POST', body: { document_id: documentId }, parseJson: true })
}

export async function getChatHistory(sessionId) {
  return request(`/api/chat/sessions/${sessionId}/messages`, { method: 'GET', parseJson: true })
}

export async function sendMessageStream(sessionId, content) {
  const response = await fetch(`/api/chat/sessions/${sessionId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(errorText || 'Streaming request failed')
  }

  return response
}
