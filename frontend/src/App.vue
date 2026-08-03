<template>
  <div class="container">
    <h1>DocIntel</h1>
    <p style="color: #cbd5e1;">Sube un documento PDF y conversa con él en tiempo real.</p>

    <DocumentUpload v-if="!document" @document-uploaded="onDocumentUploaded" />
    <ChatPanel v-else :document="document" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import DocumentUpload from './components/DocumentUpload.vue'
import ChatPanel from './components/ChatPanel.vue'

const document = ref(null)

function onDocumentUploaded(uploadedDocument) {
  document.value = uploadedDocument
}
</script>
