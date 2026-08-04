<template>
  <div class="card">
    <h2>Chat del documento</h2>
    <p v-if="document">Documento cargado: {{ document.filename }}</p>

    <div class="chat-window">
      <div v-for="message in messages" :key="message.id || message.created_at" :class="['message', message.role]">
        <strong>{{ message.role === 'user' ? 'Tú' : 'Asistente' }}:</strong>
        <div>{{ message.content }}</div>
      </div>
      <div v-if="isStreaming" class="message assistant">Escribiendo…</div>
    </div>

    <div class="input-row">
      <textarea v-model="draft" rows="3" placeholder="Escribe tu pregunta sobre el documento..." />
      <button @click="sendMessage" :disabled="isStreaming || !draft.trim()">Enviar</button>
    </div>

    <p v-if="error" style="color: #f87171; margin-top: 1rem;">{{ error }}</p>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { createChatSession, getChatHistory, sendMessageStream } from '../api'

const props = defineProps({ document: Object })

const messages = ref([])
const draft = ref('')
const error = ref('')
const isStreaming = ref(false)
const sessionId = ref(null)

async function ensureSession() {
  if (!props.document || sessionId.value) return
  try {
    const session = await createChatSession(props.document.id)
    sessionId.value = session.id
    const history = await getChatHistory(sessionId.value)
    messages.value = history
  } catch (err) {
    error.value = err.message || 'No se pudo crear la sesión de chat.'
  }
}

async function sendMessage() {
  if (!draft.value.trim() || !sessionId.value) return
  const userText = draft.value.trim()
  draft.value = ''
  messages.value.push({ role: 'user', content: userText, created_at: new Date().toISOString() })
  isStreaming.value = true
  error.value = ''

  try {
    const response = await sendMessageStream(sessionId.value, userText)
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let assistantText = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n').filter(Boolean)
      for (const line of lines) {
        if (line.startsWith('event:')) {
          const eventType = line.replace(/^event:\s*/, '').trim()
          if (eventType === 'error') {
            continue
          }
        }
        if (line.startsWith('data:')) {
          const payload = line.replace(/^data:\s*/, '')
          if (payload === '{}') {
            continue
          }
          try {
            const parsed = JSON.parse(payload)
            if (parsed.delta) {
              assistantText += parsed.delta
            }
            if (parsed.message) {
              error.value = parsed.message
              isStreaming.value = false
              return
            }
          } catch (e) {
            // ignore malformed fragments
          }
        }
      }
    }

    messages.value.push({ role: 'assistant', content: assistantText, created_at: new Date().toISOString() })
  } catch (err) {
    error.value = err.message || 'No se pudo enviar el mensaje.'
  } finally {
    isStreaming.value = false
  }
}

onMounted(() => {
  ensureSession()
})

watch(() => props.document?.id, () => {
  sessionId.value = null
  messages.value = []
  ensureSession()
})
</script>
