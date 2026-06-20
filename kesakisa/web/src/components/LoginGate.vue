<template>
  <section class="login-panel section-block" aria-labelledby="login-heading">
    <div class="ribbon">
      <span id="login-heading">{{ title }}</span>
    </div>

    <form class="login-form" @submit.prevent="submitCode">
      <p class="login-panel__help">{{ helpText }}</p>

      <div v-if="requiredRole === 'player'" class="login-countdown">
        <CountdownTimer
          :target-at="competitionStartsAt"
          label="Kesäkisa alkaa 21.6. klo 00.00."
          finished-label="Kesäkisa on alkanut."
          :as-button="false"
        />
      </div>

      <label>
        Koodi
        <input
          v-model.trim="code"
          autocomplete="one-time-code"
          :disabled="isSubmitting"
          inputmode="text"
          maxlength="40"
          required
          @input="errorText = ''"
        />
      </label>

      <p v-if="errorText" class="login-panel__error" role="alert">{{ errorText }}</p>

      <button type="submit" class="primary-button" :disabled="isSubmitting">
        {{ isSubmitting ? 'Tarkistetaan' : 'Avaa' }}
      </button>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import CountdownTimer from './CountdownTimer.vue'
import { loginWithCode, type AccessRole, type AccessSession } from '../services/accessGate'

const props = defineProps<{
  requiredRole: AccessRole
}>()

const emit = defineEmits<{
  unlock: [session: AccessSession]
}>()

const code = ref('')
const errorText = ref('')
const isSubmitting = ref(false)
const competitionStartsAt = '2026-06-21T00:00:00+03:00'
const invalidCodeMessage = 'Hups, koodi meni väärään mökkiin. Tarkista koodi ja kokeile uudestaan.'

const title = computed(() => props.requiredRole === 'admin' ? 'Järjestäjän koodi' : 'Pelaajakoodi')
const helpText = computed(() => props.requiredRole === 'admin'
  ? 'Syötä järjestäjän koodi avataksesi hallinnan.'
  : 'Syötä pelaajakoodi avataksesi kisan.'
)

async function submitCode (): Promise<void> {
  isSubmitting.value = true
  errorText.value = ''

  const result = await loginWithCode(code.value, props.requiredRole)
  isSubmitting.value = false

  if (!result.session) {
    errorText.value = loginErrorMessage(result.error)
    return
  }

  emit('unlock', result.session)
}

function loginErrorMessage (error: string | null): string {
  if (!error || error === 'Invalid code' || error === 'Koodia ei voitu vahvistaa.') {
    return invalidCodeMessage
  }

  return error
}
</script>
