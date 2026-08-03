<template>
  <div class="card">
    <h2>Upload de documento</h2>
    <p>Sube un PDF para extraer su contenido y comenzar a conversar con él.</p>

    <div
      class="upload-area"
      :class="{ dragover: isDragging }"
      @dragover.prevent="onDragOver"
      @dragleave.prevent="onDragLeave"
      @drop.prevent="onDrop"
      @click="$refs.fileInput.click()"
    >
      <p>{{ fileName || 'Arrastra un PDF aquí o haz clic para seleccionarlo' }}</p>
      <input ref="fileInput" type="file" accept="application/pdf" @change="handleFileSelect" hidden />
    </div>

    <div class="input-row" style="margin-top: 1rem;">
      <button @click="uploadFile" :disabled="!selectedFile || isUploading">
        {{ isUploading ? 'Subiendo...' : 'Subir documento' }}
      </button>
    </div>

    <p v-if="error" style="color: #f87171; margin-top: 1rem;">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { uploadDocument } from '../api'

const emit = defineEmits(['document-uploaded'])

const selectedFile = ref(null)
const fileName = ref('')
const isDragging = ref(false)
const isUploading = ref(false)
const error = ref('')

function onDragOver() {
  isDragging.value = true
}

function onDragLeave() {
  isDragging.value = false
}

function onDrop(event) {
  isDragging.value = false
  const droppedFile = event.dataTransfer?.files?.[0]
  if (droppedFile) {
    selectedFile.value = droppedFile
    fileName.value = droppedFile.name
  }
}

function handleFileSelect(event) {
  const file = event.target.files?.[0]
  if (file) {
    selectedFile.value = file
    fileName.value = file.name
  }
}

async function uploadFile() {
  if (!selectedFile.value) return
  error.value = ''
  isUploading.value = true

  try {
    const document = await uploadDocument(selectedFile.value)
    emit('document-uploaded', document)
  } catch (err) {
    error.value = err.message || 'No se pudo subir el documento.'
  } finally {
    isUploading.value = false
  }
}
</script>
