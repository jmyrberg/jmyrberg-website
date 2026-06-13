<template>
  <aside
    class="host-status-dock"
    :class="`host-status-dock--${primaryTone}`"
    :role="hasError ? 'alert' : 'status'"
    :aria-live="hasError ? 'assertive' : 'polite'"
    aria-atomic="true"
  >
    <div class="host-status-dock__inner">
      <div
        v-if="statusItem"
        class="host-status-dock__item"
        :class="`host-status-dock__item--${statusItem.tone}`"
      >
        <span
          class="host-status-dock__icon"
          :class="{ 'host-status-dock__icon--spin': statusItem.isLoading }"
          aria-hidden="true"
        >
          {{ statusItem.icon }}
        </span>
        <span class="host-status-dock__copy">
          <strong>{{ statusItem.title }}</strong>
          <span>{{ statusItem.message }}</span>
        </span>
        <button
          v-if="statusItem.canRetry"
          type="button"
          class="text-button"
          @click="emit('retryRemoteSave')"
        >
          Yritä uudelleen
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type HostFeedbackStatus = 'pending' | 'success' | 'error'
type RemoteSaveStatus = 'idle' | 'saving' | 'saved' | 'error'
type StatusTone = 'pending' | 'success' | 'error'

interface HostFeedback {
  status: HostFeedbackStatus
  message: string
}

interface StatusItem {
  id: string
  title: string
  message: string
  tone: StatusTone
  icon: string
  isLoading?: boolean
  canRetry?: boolean
}

const props = defineProps<{
  hostFeedback: HostFeedback | null
  remoteSaveStatus: RemoteSaveStatus
  remoteSaveMessage: string
  remoteSyncError: string
}>()

const emit = defineEmits<{
  retryRemoteSave: []
}>()

const statusItem = computed<StatusItem | null>(() => {
  if (props.remoteSaveStatus === 'error' && props.remoteSaveMessage) {
    return {
      id: 'remote-save-error',
      title: 'Julkaisuvirhe',
      message: props.remoteSaveMessage,
      tone: 'error',
      icon: '!',
      canRetry: true
    }
  }

  if (props.remoteSyncError) {
    return {
      id: 'remote-sync-error',
      title: 'Yhteysvirhe',
      message: props.remoteSyncError,
      tone: 'error',
      icon: '!'
    }
  }

  if (props.hostFeedback) {
    return {
      id: 'host-feedback',
      title: titleForHostFeedback(props.hostFeedback.status),
      message: props.hostFeedback.message,
      tone: toneForHostFeedback(props.hostFeedback.status),
      icon: iconForHostFeedback(props.hostFeedback.status),
      isLoading: props.hostFeedback.status === 'pending'
    }
  }

  if (props.remoteSaveStatus === 'saving' && props.remoteSaveMessage) {
    return {
      id: 'remote-save-saving',
      title: 'Julkaistaan',
      message: props.remoteSaveMessage,
      tone: 'pending',
      icon: '',
      isLoading: true
    }
  }

  if (props.remoteSaveStatus === 'saved' && props.remoteSaveMessage) {
    return {
      id: 'remote-save-saved',
      title: 'Julkaistu',
      message: props.remoteSaveMessage,
      tone: 'success',
      icon: '✓'
    }
  }

  return null
})

const hasError = computed(() => statusItem.value?.tone === 'error')
const primaryTone = computed<StatusTone>(() => statusItem.value?.tone ?? 'pending')

function titleForHostFeedback (status: HostFeedbackStatus): string {
  if (status === 'pending') {
    return 'Tallennetaan'
  }

  if (status === 'success') {
    return 'Valmis'
  }

  return 'Virhe'
}

function toneForHostFeedback (status: HostFeedbackStatus): StatusTone {
  return status === 'pending' ? 'pending' : status
}

function iconForHostFeedback (status: HostFeedbackStatus): string {
  if (status === 'success') {
    return '✓'
  }

  if (status === 'error') {
    return '!'
  }

  return ''
}
</script>
