<template>
  <section class="section-block" aria-labelledby="hiiret-heading">
    <div class="ribbon">
      <span id="hiiret-heading">Hiiret</span>
    </div>

    <p class="section-summary">{{ mouseSummary }}</p>

    <div class="mouse-den">
      <article
        v-for="mouse in mice"
        :key="mouse.id"
        class="mouse-card"
        :class="{
          'mouse-card--found': foundByMouse[mouse.id],
          'mouse-card--shake': shakingMouseId === mouse.id
        }"
      >
        <button
          type="button"
          class="mouse-card__image-button"
          :aria-label="`${mouse.label}, ${foundByMouse[mouse.id] ? 'löydetty' : 'piilossa'}`"
          @click="vibrateMouse(mouse.id)"
        >
          <img
            class="mouse-card__image"
            :src="foundByMouse[mouse.id] ? mouse.foundImage : mouse.image"
            :alt="mouse.label"
          />
        </button>
        <div class="mouse-card__meta">
          <div class="mouse-card__meta-heading">
            <strong>{{ mouse.label }}</strong>
            <button
              v-if="showTipsForMouse(mouse.id)"
              type="button"
              class="mouse-card__tip-button"
              :class="{
                'mouse-card__tip-button--lit': !expandedTipMouseIds.includes(mouse.id)
              }"
              :aria-expanded="expandedTipMouseIds.includes(mouse.id)"
              :aria-label="expandedTipMouseIds.includes(mouse.id) ? `Piilota ${mouse.label} vinkit` : `Näytä ${mouse.label} vinkit`"
              @click="toggleTips(mouse.id)"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M9 19h6" />
                <path d="M10 22h4" />
                <path d="M8.5 14.8c-1.5-1.1-2.5-2.9-2.5-4.8a6 6 0 1 1 12 0c0 1.9-1 3.7-2.5 4.8-.6.5-.9 1.1-.9 1.8H9.4c0-.7-.3-1.3-.9-1.8Z" />
              </svg>
            </button>
          </div>
          <span v-if="foundByMouse[mouse.id]">Löydetty</span>
          <span v-else>Piilossa</span>
        </div>

        <transition name="expand">
          <div v-if="showTipsForMouse(mouse.id) && expandedTipMouseIds.includes(mouse.id)" class="mouse-card__tips">
            <ul>
              <li v-for="tip in tipsForMouse(mouse.id)" :key="tip.id">
                {{ tip.text }}
              </li>
            </ul>
          </div>
        </transition>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'
import type { FoundMouse, MouseAsset, MouseId, MouseTip } from '../types'
import mouseBlack from '../assets/mouse-black.svg'
import mouseBlackFound from '../assets/mouse-black-found.svg'
import mousePink from '../assets/mouse-pink.svg'
import mousePinkFound from '../assets/mouse-pink-found.svg'
import mouseWhite from '../assets/mouse-white.svg'
import mouseWhiteFound from '../assets/mouse-white-found.svg'

const props = defineProps<{
  foundMice: FoundMouse[]
  mouseTips: MouseTip[]
}>()

const emit = defineEmits<{
  viewTips: [seenAt: string]
}>()

const mice: MouseAsset[] = [
  {
    id: 'white',
    label: 'Valkoinen hiiri',
    image: mouseWhite,
    foundImage: mouseWhiteFound
  },
  {
    id: 'pink',
    label: 'Pinkki hiiri',
    image: mousePink,
    foundImage: mousePinkFound
  },
  {
    id: 'black',
    label: 'Musta hiiri',
    image: mouseBlack,
    foundImage: mouseBlackFound
  }
]

const foundByMouse = computed(() => {
  return props.foundMice.reduce<Record<string, FoundMouse>>((acc, found) => {
    acc[found.mouseId] = found
    return acc
  }, {})
})

const hiddenMouseCount = computed(() => mice.length - props.foundMice.length)
const mouseSummary = computed(() => hiddenMouseCount.value > 0 ? 'Hiiriä on piilossa' : 'Kaikki hiiret on löydetty')
const shakingMouseId = ref<MouseId | null>(null)
const expandedTipMouseIds = ref<MouseId[]>([])
let shakeTimeout: number | undefined

onBeforeUnmount(() => {
  if (shakeTimeout) {
    window.clearTimeout(shakeTimeout)
  }
})

function tipsForMouse (mouseId: MouseId): MouseTip[] {
  return props.mouseTips
    .filter(tip => tip.mouseId === mouseId)
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
}

function showTipsForMouse (mouseId: MouseId): boolean {
  return !foundByMouse.value[mouseId] && tipsForMouse(mouseId).length > 0
}

function toggleTips (mouseId: MouseId): void {
  if (expandedTipMouseIds.value.includes(mouseId)) {
    expandedTipMouseIds.value = expandedTipMouseIds.value.filter(id => id !== mouseId)
    return
  }

  expandedTipMouseIds.value = [...expandedTipMouseIds.value, mouseId]

  const newestTip = tipsForMouse(mouseId)[0]
  if (newestTip) {
    emit('viewTips', newestTip.createdAt)
  }
}

function vibrateMouse (mouseId: MouseId): void {
  if (shakeTimeout) {
    window.clearTimeout(shakeTimeout)
  }

  shakingMouseId.value = null
  window.requestAnimationFrame(() => {
    shakingMouseId.value = mouseId
  })

  if ('vibrate' in navigator) {
    const haptics = navigator as Navigator & { vibrate: (pattern: number | number[]) => boolean }
    haptics.vibrate([45, 35, 45, 35, 45, 35, 45, 35, 45, 35, 45, 35, 45, 35, 45, 35, 45, 35, 45, 35, 45, 35, 45])
  }

  shakeTimeout = window.setTimeout(() => {
    shakingMouseId.value = null
  }, 1000)
}
</script>
