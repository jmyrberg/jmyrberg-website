<template>
  <section
    class="section-block host-panel"
    :class="{
      'host-panel--busy': isHostBusy,
      'host-panel--status-dock-visible': statusDockVisible
    }"
    aria-label="Järjestäjä"
  >
    <div class="host-stack">
      <span class="host-tab-label">Aihe</span>
      <div class="host-domain-tabs">
        <button
          v-for="domain in domains"
          :key="domain.id"
          type="button"
          :class="{ 'host-domain-tabs__button--active': activeDomain === domain.id }"
          class="host-domain-tabs__button"
          @click="selectDomain(domain.id)"
        >
          {{ domain.label }}
        </button>
      </div>

      <div class="host-divider" role="presentation" />

      <span class="host-tab-label">Toiminto</span>
      <div class="host-action-tabs">
        <button
          v-for="action in currentActions"
          :key="action.id"
          type="button"
          :class="{ 'host-action-tabs__button--active': activeAction === action.id }"
          class="host-action-tabs__button"
          @click="selectAction(action.id)"
        >
          {{ action.label }}
        </button>
      </div>

      <form
        v-if="activeDomain === 'paivatehtava' && activeAction === 'luo'"
        class="host-card tip-form"
        @submit.prevent="createDailyTaskSetup"
      >
        <h2>Lisää päivätehtävä</h2>
        <p class="host-help">Syötä tehtävän sisältö ja aikataulu yhdessä paikassa. Ohjeet näkyvät osallistujille vasta, kun järjestäjä avaa ne käsiohjauksesta.</p>
        <label>
          Otsikko
          <input v-model.trim="dailyTaskDraft.title" required maxlength="48" />
        </label>
        <label>
          Paikka
          <input v-model.trim="dailyTaskDraft.location" required maxlength="60" />
        </label>
        <label>
          Aloitusaika
          <input v-model="dailyTaskStartDraft" type="datetime-local" required />
        </label>
        <label>
          Lopetusaika
          <input v-model="dailyTaskEndDraft" type="datetime-local" required />
        </label>
        <label>
          Ennen aloitusta näkyvä ohje
          <textarea v-model.trim="dailyTaskDraft.preparationText" rows="3" required />
        </label>
        <label>
          Osallistujille avattavat ohjeet
          <textarea v-model.trim="dailyTaskDraft.instructions" rows="5" required />
        </label>
        <button type="submit" class="primary-button" :disabled="isHostBusy">
          Lisää päivätehtävä
        </button>
      </form>

      <div v-else-if="activeDomain === 'paivatehtava' && activeAction === 'hallinta'" class="host-card">
        <h2>Muokkaa päivätehtävää</h2>
        <div class="choice-field">
          <span>Valitse päivätehtävä</span>
          <div class="task-choice-list">
            <button
              v-for="task in dailyTasks"
              :key="task.id"
              type="button"
              class="task-choice"
              :class="{ 'task-choice--active': editableDailyTask.id === task.id }"
              @click="selectDailyTask(task)"
            >
              <strong>{{ task.title }}</strong>
              <span>{{ formatDate(task.startsAt) }}<template v-if="activeDailyTaskId === task.id"> · Näkyy osallistujille</template></span>
            </button>
          </div>
        </div>
        <div class="task-summary">
          <strong>{{ editableDailyTask.title }}</strong>
          <span>{{ editableDailyTask.location }} · {{ formatDate(editableDailyTask.startsAt) }} - {{ formatClock(editableDailyTask.endsAt) }}</span>
          <button
            v-if="editableDailyTask.id !== activeDailyTaskId"
            type="button"
            class="pill-button"
            :disabled="isHostBusy"
            @click="publishSelectedDailyTask"
          >
            Näytä osallistujille
          </button>
        </div>
        <div v-if="canRemoveDailyTask(editableDailyTask)" class="host-subsection">
          <h3>Poista tehtävä</h3>
          <p class="host-help">Voit poistaa valitun tehtävän riippumatta siitä, onko se tuleva, käynnissä vai päättynyt.</p>
          <button type="button" class="pill-button pill-button--danger" :disabled="isHostBusy" @click="removeDailyTask(editableDailyTask.id)">
            Poista tehtävä
          </button>
        </div>

        <div class="host-subsection">
          <h3>Käsiohjaus</h3>
          <p class="host-help">{{ dailyTaskControlSummary }}</p>
          <div class="quick-actions">
            <button
              type="button"
              class="pill-button"
              :class="{ 'pill-button--danger': editableDailyTaskStatus === 'live' }"
              :disabled="isHostBusy || !canControlDailyTask(editableDailyTask)"
              @click="toggleTaskTiming"
            >
              {{ taskTimingActionLabel }}
            </button>
            <button
              type="button"
              class="pill-button"
              :disabled="isHostBusy || !canToggleDailyTaskGuidance"
              @click="toggleGuidanceVisibility"
            >
              {{ guidanceActionLabel }}
            </button>
          </div>
        </div>

        <details class="host-subsection">
          <summary>Muokkaa tehtävää</summary>
          <form class="tip-form" @submit.prevent="submitDailyTaskSetup">
            <label>
              Otsikko
              <input v-model.trim="dailyTaskDraft.title" required maxlength="48" />
            </label>
            <label>
              Paikka
              <input v-model.trim="dailyTaskDraft.location" required maxlength="60" />
            </label>
            <label>
              Aloitusaika
              <input v-model="dailyTaskStartDraft" type="datetime-local" required />
            </label>
            <label>
              Lopetusaika
              <input v-model="dailyTaskEndDraft" type="datetime-local" required />
            </label>
            <label>
              Ennen aloitusta näkyvä ohje
              <textarea v-model.trim="dailyTaskDraft.preparationText" rows="3" required />
            </label>
            <label>
              Osallistujille avattavat ohjeet
              <textarea v-model.trim="dailyTaskDraft.instructions" rows="5" required />
            </label>
            <button type="submit" class="primary-button" :disabled="isHostBusy">
              Tallenna muutokset
            </button>
          </form>
        </details>

        <div class="host-subsection">
          <h3>Lisävinkit</h3>
          <form class="tip-form" @submit.prevent="submitDailyTip">
            <label>
              Uusi vinkki
              <textarea v-model.trim="dailyTipText" rows="3" required />
            </label>
            <button type="submit" class="primary-button" :disabled="isHostBusy">
              Julkaise päivävinkki
            </button>
          </form>
          <div v-if="sortedDailyTips.length" class="host-list">
            <article v-for="tip in sortedDailyTips" :key="tip.id" class="host-list-item">
              <small>{{ formatDate(tip.createdAt) }}</small>
              <textarea
                :value="dailyDrafts[tip.id] ?? tip.text"
                rows="3"
                @input="dailyDrafts[tip.id] = inputValue($event)"
              />
              <div class="quick-actions">
                <button type="button" class="pill-button" :disabled="isHostBusy" @click="saveDailyTip(tip)">
                  Tallenna
                </button>
                <button type="button" class="pill-button pill-button--danger" :disabled="isHostBusy" @click="removeDailyTip(tip.id)">
                  Poista
                </button>
              </div>
            </article>
          </div>
          <p v-else class="empty-note">Ei päivävinkkejä.</p>
        </div>
      </div>

      <div v-else-if="activeDomain === 'hiiret' && activeAction === 'tila'" class="host-card">
        <h2>Muokkaa hiiriä</h2>
        <div class="mouse-toggle-grid">
          <button
            v-for="mouse in mice"
            :key="mouse.id"
            type="button"
            class="mouse-toggle"
            :class="{ 'mouse-toggle--found': foundMouse(mouse.id) }"
            :aria-pressed="!!foundMouse(mouse.id)"
            :disabled="isHostBusy"
            @click="toggleMouse(mouse.id)"
          >
            <img :src="foundMouse(mouse.id) ? mouse.foundImage : mouse.image" :alt="mouse.label" />
            <strong>{{ mouse.label }}</strong>
            <span>{{ foundMouse(mouse.id) ? teamName(foundMouse(mouse.id)?.teamId) : 'Piilossa' }}</span>
          </button>
        </div>
        <div class="choice-field">
          <span>Löytänyt joukkue</span>
          <div class="choice-group">
            <button
              type="button"
              class="choice-button"
              :class="{ 'choice-button--active': selectedMouseTeam === null }"
              @click="selectedMouseTeam = null"
            >
              Ei löydetty
            </button>
            <button
              v-for="team in teams"
              :key="team.id"
              type="button"
              class="choice-button"
              :class="{ 'choice-button--active': selectedMouseTeam === team.id }"
              :style="{ '--choice-accent': team.accent }"
              @click="selectedMouseTeam = team.id"
            >
              {{ team.name }}
            </button>
          </div>
        </div>
      </div>

      <div v-else-if="activeDomain === 'hiiret' && activeAction === 'vinkit'" class="host-card">
        <h2>Lisää hiirivinkki</h2>
        <form class="tip-form" @submit.prevent="submitTip">
          <div class="mouse-choice-group" role="radiogroup" aria-label="Valitse hiiri">
            <button
              v-for="mouse in mice"
              :key="mouse.id"
              type="button"
              class="mouse-choice"
              :class="{ 'mouse-choice--active': mouseId === mouse.id }"
              :aria-checked="mouseId === mouse.id"
              role="radio"
              @click="mouseId = mouse.id"
            >
              <img :src="mouse.image" :alt="mouse.label" />
              <span>{{ mouse.label }}</span>
            </button>
          </div>
          <label>
            Uusi vinkki
            <textarea v-model.trim="tipText" rows="3" required />
          </label>
          <button type="submit" class="primary-button" :disabled="isHostBusy">
            Lisää vinkki
          </button>
        </form>
        <div v-if="mouseTips.length" class="host-list">
          <article v-for="tip in sortedMouseTips" :key="tip.id" class="host-list-item">
            <small>{{ mouseLabel(tip.mouseId) }} · {{ formatDate(tip.createdAt) }}</small>
            <div class="mouse-choice-group mouse-choice-group--compact" role="radiogroup" aria-label="Vaihda hiiri">
              <button
                v-for="mouse in mice"
                :key="mouse.id"
                type="button"
                class="mouse-choice"
                :class="{ 'mouse-choice--active': selectedTipMouse(tip) === mouse.id }"
                :aria-checked="selectedTipMouse(tip) === mouse.id"
                role="radio"
                @click="mouseTipSelections[tip.id] = mouse.id"
              >
                <img :src="mouse.image" :alt="mouse.label" />
                <span>{{ mouse.label }}</span>
              </button>
            </div>
            <textarea
              :value="mouseDrafts[tip.id] ?? tip.text"
              rows="3"
              @input="mouseDrafts[tip.id] = inputValue($event)"
            />
            <div class="quick-actions">
              <button type="button" class="pill-button" :disabled="isHostBusy" @click="saveMouseTip(tip)">
                Tallenna
              </button>
              <button type="button" class="pill-button pill-button--danger" :disabled="isHostBusy" @click="removeMouseTip(tip.id)">
                Poista
              </button>
            </div>
          </article>
        </div>
        <p v-else class="empty-note">Ei hiirivinkkejä.</p>
      </div>

      <div v-else-if="activeDomain === 'pisteet' && activeAction === 'lisaa'" class="host-card">
        <h2>Lisää pisteet</h2>
        <SubmissionForm
          :teams="teams"
          :daily-tasks="dailyTasks"
          :active-daily-task-id="activeDailyTaskId"
          :disabled="isHostBusy"
          @add="submitScore"
        />
      </div>

      <div v-else-if="activeDomain === 'pisteet' && activeAction === 'muokkaa'" class="host-card">
        <h2>Muokkaa pisteitä</h2>
        <div v-if="scoreEvents.length" class="host-list">
          <article v-for="scoreEvent in sortedScoreEvents" :key="scoreEvent.id" class="host-list-item score-editor">
            <header class="score-editor__header">
              <div class="score-editor__title-row">
                <strong>{{ scoreHeader(scoreEvent) }}</strong>
                <span v-if="isScoreDirty(scoreEvent)" class="dirty-badge">Tallentamatta</span>
              </div>
              <small>{{ teamName(scoreTeam(scoreEvent)) }} · {{ formatDate(scoreEvent.createdAt) }}</small>
            </header>

            <div class="choice-field">
              <span>Joukkue</span>
              <div class="choice-group choice-group--teams">
                <button
                  v-for="team in teams"
                  :key="team.id"
                  type="button"
                  class="choice-button"
                  :class="{ 'choice-button--active': scoreTeam(scoreEvent) === team.id }"
                  :style="{ '--choice-accent': team.accent }"
                  @click="updateScoreDraft(scoreEvent, { teamId: team.id })"
                >
                  {{ team.name }}
                </button>
              </div>
            </div>

            <div class="choice-field">
              <span>Laji</span>
              <div class="choice-group">
                <button
                  v-for="option in scoreCategoryOptions"
                  :key="option.value"
                  type="button"
                  class="choice-button"
                  :class="{ 'choice-button--active': scoreCategory(scoreEvent) === option.value }"
                  @click="updateScoreCategory(scoreEvent, option.value)"
                >
                  {{ option.label }}
                </button>
              </div>
            </div>

            <div v-if="scoreCategory(scoreEvent) === 'paivatehtava'" class="choice-field">
              <span>Päivätehtävä</span>
              <div class="task-choice-list">
                <button
                  v-for="task in dailyTasks"
                  :key="task.id"
                  type="button"
                  class="task-choice"
                  :class="{ 'task-choice--active': scoreDailyTaskId(scoreEvent) === task.id }"
                  @click="updateScoreTask(scoreEvent, task)"
                >
                  <strong>{{ task.title }}</strong>
                  <span>{{ formatDate(task.startsAt) }}</span>
                </button>
              </div>
            </div>

            <div class="score-editor__fields">
              <label>
                Otsikko
                <input
                  :value="scoreTitle(scoreEvent)"
                  maxlength="48"
                  required
                  @input="updateScoreDraft(scoreEvent, { title: inputValue($event) })"
                />
              </label>

              <label>
                Pisteet
                <input
                  :value="scorePoints(scoreEvent)"
                  type="number"
                  min="-100"
                  max="100"
                  required
                  @input="updateScoreDraft(scoreEvent, { points: Number(inputValue($event)) })"
                />
              </label>
            </div>

            <div class="choice-field">
              <span>Pikapisteet</span>
              <div class="points-chips">
                <button
                  v-for="value in pointOptions"
                  :key="value"
                  type="button"
                  class="point-chip"
                  :class="{ 'point-chip--active': scorePoints(scoreEvent) === value }"
                  @click="updateScoreDraft(scoreEvent, { points: value })"
                >
                  {{ value }}p
                </button>
              </div>
            </div>

            <label>
              Lisätiedot
              <textarea
                :value="scoreDescription(scoreEvent)"
                rows="3"
                @input="updateScoreDraft(scoreEvent, { description: inputValue($event) })"
              />
            </label>

            <div class="quick-actions">
              <button type="button" class="pill-button" :disabled="isHostBusy || !isScoreDirty(scoreEvent)" @click="saveScore(scoreEvent)">
                Tallenna
              </button>
              <button v-if="isScoreDirty(scoreEvent)" type="button" class="pill-button" :disabled="isHostBusy" @click="cancelScoreDraft(scoreEvent.id)">
                Peru
              </button>
              <button type="button" class="pill-button pill-button--danger" :disabled="isHostBusy" @click="removeScore(scoreEvent.id)">
                Poista
              </button>
            </div>
          </article>
        </div>
        <p v-else class="empty-note">Ei pistekirjauksia.</p>
      </div>

      <div v-else-if="activeDomain === 'viestit' && activeAction === 'laheta'" class="host-card">
        <h2>Viestit</h2>
        <form class="tip-form" @submit.prevent="submitUserMessage">
          <label>
            Vastaanottaja
            <select v-model="userMessageRecipientId" required>
              <option value="" disabled>Valitse pelaaja</option>
              <option v-for="player in players" :key="player.id" :value="player.id">
                {{ player.name }}
              </option>
            </select>
          </label>
          <label>
            Uusi viesti
            <textarea v-model.trim="userMessageText" rows="4" required maxlength="500" />
          </label>
          <button type="submit" class="primary-button" :disabled="isHostBusy || !userMessageRecipientId">
            Lähetä viesti
          </button>
        </form>

        <div v-if="userMessages.length" class="host-list">
          <article v-for="message in sortedUserMessages" :key="message.id" class="host-list-item">
            <small>{{ playerName(message.recipientPlayerId) }} · {{ formatDate(message.createdAt) }}</small>
            <textarea
              :value="userMessageDrafts[message.id] ?? message.text"
              rows="3"
              maxlength="500"
              @input="userMessageDrafts[message.id] = inputValue($event)"
            />
            <div class="quick-actions">
              <button type="button" class="pill-button" :disabled="isHostBusy" @click="saveUserMessage(message)">
                Tallenna
              </button>
              <button type="button" class="pill-button pill-button--danger" :disabled="isHostBusy" @click="removeUserMessage(message.id)">
                Poista
              </button>
            </div>
          </article>
        </div>
        <p v-else class="empty-note">Ei lähetettyjä viestejä.</p>
      </div>

      <div v-else-if="activeDomain === 'joukkueet' && activeAction === 'hallinta'" class="host-card">
        <h2>Joukkueet</h2>
        <form class="tip-form" @submit.prevent="submitTeam">
          <label>
            Joukkueen nimi
            <input v-model.trim="teamNameDraft" required maxlength="32" />
          </label>
          <div class="choice-field">
            <span>Väri</span>
            <div class="color-choice-row">
              <button
                v-for="color in teamColorOptions"
                :key="color"
                type="button"
                class="color-choice"
                :class="{ 'color-choice--active': teamAccentDraft === color }"
                :style="{ '--team-accent': color }"
                :aria-label="`Valitse väri ${color}`"
                @click="teamAccentDraft = color"
              />
            </div>
          </div>
          <label>
            Oma väri
            <input v-model="teamAccentDraft" type="color" required />
          </label>
          <button type="submit" class="primary-button" :disabled="isHostBusy">
            Lisää joukkue
          </button>
        </form>

        <div v-if="teams.length" class="host-list">
          <article v-for="team in teams" :key="team.id" class="host-list-item team-editor">
            <small>Joukkue</small>
            <label>
              Nimi
              <input
                :value="teamDraftName(team)"
                maxlength="32"
                required
                @input="updateTeamDraft(team, { name: inputValue($event) })"
              />
            </label>
            <div class="choice-field">
              <span>Väri</span>
              <div class="color-choice-row">
                <button
                  v-for="color in teamColorOptions"
                  :key="color"
                  type="button"
                  class="color-choice"
                  :class="{ 'color-choice--active': teamDraftAccent(team) === color }"
                  :style="{ '--team-accent': color }"
                  :aria-label="`Valitse väri ${color}`"
                  @click="updateTeamDraft(team, { accent: color })"
                />
              </div>
            </div>
            <label>
              Oma väri
              <input
                :value="teamDraftAccent(team)"
                type="color"
                required
                @input="updateTeamDraft(team, { accent: inputValue($event) })"
              />
            </label>
            <div class="quick-actions">
              <button type="button" class="pill-button" :disabled="isHostBusy" @click="saveTeam(team)">
                Tallenna
              </button>
              <button
                type="button"
                class="pill-button pill-button--danger"
                :disabled="teams.length <= 1 || isHostBusy"
                @click="removeTeam(team.id)"
              >
                Poista
              </button>
            </div>
          </article>
        </div>
      </div>

      <div v-else-if="activeDomain === 'pelaajat' && activeAction === 'hallinta'" class="host-card">
        <h2>Pelaajat</h2>
        <form class="tip-form" @submit.prevent="submitPlayer">
          <label>
            Pelaajan nimi
            <input v-model.trim="playerNameDraft" required maxlength="32" />
          </label>
          <button type="submit" class="primary-button" :disabled="isHostBusy || !accessToken">
            Lisää pelaajakoodi
          </button>
          <p v-if="playerInviteError" class="login-panel__error">{{ playerInviteError }}</p>
        </form>

        <div v-if="latestPlayerInvite" class="host-code-box">
          <small>Uusin pelaajakoodi</small>
          <strong>{{ latestPlayerInvite.label }}</strong>
          <code>{{ latestPlayerInvite.code }}</code>
        </div>

        <div v-if="players.length" class="host-list">
          <article v-for="player in players" :key="player.id" class="host-list-item player-editor">
            <small>Pelaaja</small>
            <label>
              Nimi
              <input
                :value="playerDraftName(player)"
                maxlength="32"
                required
                @input="updatePlayerDraft(player, { name: inputValue($event) })"
              />
            </label>
            <label>
              Joukkue
              <select
                :value="playerDraftTeamId(player) ?? ''"
                :disabled="isHostBusy"
                @change="updatePlayerDraft(player, { teamId: selectedNullableTeamId($event) })"
              >
                <option value="">Ei joukkuetta</option>
                <option v-for="team in teams" :key="team.id" :value="team.id">
                  {{ team.name }}
                </option>
              </select>
            </label>
            <div v-if="playerDraftInviteCode(player)" class="player-code-line">
              <span>Pelaajakoodi</span>
              <code>{{ playerDraftInviteCode(player) }}</code>
            </div>
            <div class="quick-actions">
              <button type="button" class="pill-button" :disabled="isHostBusy" @click="savePlayer(player)">
                Tallenna
              </button>
              <button type="button" class="pill-button" :disabled="isHostBusy || !accessToken" @click="regeneratePlayerInvite(player)">
                Uusi koodi
              </button>
              <button type="button" class="pill-button pill-button--danger" :disabled="isHostBusy" @click="removePlayer(player.id)">
                Poista
              </button>
            </div>
          </article>
        </div>
        <p v-else class="empty-note">Ei pelaajia.</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import type { DailyTask, DailyTip, FoundMouse, MouseId, MouseTip, Player, ScoreCategory, ScoreEvent, TaskStatus, Team, TeamId, UserMessage } from '../types'
import { createPlayerInvite, type PlayerInvite } from '../services/accessGate'
import { formatClock, formatShortDateTime as formatDate } from '../utils/dateFormat'
import { dailyTaskScoreKey, defaultDailyTaskId, pointOptions, scoreCategoryLabel, scoreCategoryOptions, scoreDefaultsForCategory, teamNameForScore, validateScoreEvent } from '../utils/score'
import mouseBlack from '../assets/mouse-black.svg'
import mouseBlackFound from '../assets/mouse-black-found.svg'
import mousePink from '../assets/mouse-pink.svg'
import mousePinkFound from '../assets/mouse-pink-found.svg'
import mouseWhite from '../assets/mouse-white.svg'
import mouseWhiteFound from '../assets/mouse-white-found.svg'
import SubmissionForm from './SubmissionForm.vue'

type HostDomain = 'paivatehtava' | 'hiiret' | 'pisteet' | 'viestit' | 'joukkueet' | 'pelaajat'
type HostAction = 'luo' | 'hallinta' | 'tila' | 'vinkit' | 'lisaa' | 'muokkaa' | 'laheta'
type HostFeedbackStatus = 'pending' | 'success' | 'error'

type ScoreDraft = Partial<Pick<ScoreEvent, 'teamId' | 'category' | 'dailyTaskId' | 'title' | 'points' | 'description'>>
type TeamDraft = Partial<Pick<Team, 'name' | 'accent'>>
type PlayerDraft = Partial<Pick<Player, 'name' | 'teamId' | 'inviteCode'>>
type HostFeedback = {
  status: HostFeedbackStatus
  message: string
}

const props = defineProps<{
  teams: Team[]
  players: Player[]
  accessToken?: string
  dailyTask: DailyTask
  dailyTasks: DailyTask[]
  activeDailyTaskId: string
  mouseTips: MouseTip[]
  dailyTips: DailyTip[]
  userMessages: UserMessage[]
  foundMice: FoundMouse[]
  scoreEvents: ScoreEvent[]
  statusDockVisible: boolean
}>()

const emit = defineEmits<{
  addScore: [event: ScoreEvent]
  updateScore: [event: ScoreEvent]
  removeScore: [eventId: string]
  addTeam: [team: Team]
  updateTeam: [team: Team]
  removeTeam: [teamId: TeamId]
  addPlayer: [player: Player]
  updatePlayer: [player: Player]
  removePlayer: [playerId: string]
  addMouseTip: [tip: MouseTip]
  updateMouseTip: [tip: MouseTip]
  removeMouseTip: [tipId: string]
  addDailyTip: [tip: DailyTip]
  updateDailyTip: [tip: DailyTip]
  removeDailyTip: [tipId: string]
  addUserMessage: [message: UserMessage]
  updateUserMessage: [message: UserMessage]
  removeUserMessage: [messageId: string]
  createDailyTask: [task: DailyTask]
  updateDailyTask: [task: DailyTask]
  removeDailyTask: [taskId: string]
  setActiveDailyTask: [taskId: string]
  setMouseFound: [mouseId: MouseId, teamId: TeamId]
  setMouseHidden: [mouseId: MouseId]
  startTaskNow: [taskId: string]
  endTaskNow: [taskId: string]
  hostFeedbackChange: [feedback: HostFeedback | null]
}>()

const mouseId = ref<MouseId>('white')
const tipText = ref('')
const dailyTipText = ref('')
const userMessageText = ref('')
const userMessageRecipientId = ref(props.players[0]?.id ?? '')
const selectedMouseTeam = ref<TeamId | null>(null)
const teamNameDraft = ref('')
const teamAccentDraft = ref('#f7e87a')
const playerNameDraft = ref('')
const latestPlayerInvite = ref<PlayerInvite | null>(null)
const playerInviteError = ref('')
const activeDomain = ref<HostDomain>('pisteet')
const activeAction = ref<HostAction>('lisaa')
const selectedDailyTaskId = ref(props.activeDailyTaskId)
const dailyTaskDraft = reactive({
  title: '',
  location: '',
  preparationText: '',
  instructions: ''
})
const dailyTaskStartDraft = ref('')
const dailyTaskEndDraft = ref('')
const dailyDrafts = reactive<Record<string, string>>({})
const mouseDrafts = reactive<Record<string, string>>({})
const userMessageDrafts = reactive<Record<string, string>>({})
const mouseTipSelections = reactive<Record<string, MouseId>>({})
const scoreDrafts = reactive<Record<string, ScoreDraft>>({})
const teamDrafts = reactive<Record<string, TeamDraft>>({})
const playerDrafts = reactive<Record<string, PlayerDraft>>({})
const hostFeedback = ref<HostFeedback | null>(null)
const isDailyTaskDraftDirty = ref(false)
const now = ref(Date.now())
let feedbackTimeout: number | undefined
let taskStatusTimer: number | undefined
let isSyncingDailyTaskDraft = false

const domains: { id: HostDomain, label: string }[] = [
  { id: 'paivatehtava', label: 'Päivätehtävä' },
  { id: 'hiiret', label: 'Hiiret' },
  { id: 'pisteet', label: 'Pisteet' },
  { id: 'viestit', label: 'Viestit' },
  { id: 'joukkueet', label: 'Joukkueet' },
  { id: 'pelaajat', label: 'Pelaajat' }
]

const actionsByDomain: Record<HostDomain, { id: HostAction, label: string }[]> = {
  paivatehtava: [
    { id: 'luo', label: 'Lisää' },
    { id: 'hallinta', label: 'Muokkaa' }
  ],
  hiiret: [
    { id: 'tila', label: 'Muokkaa' },
    { id: 'vinkit', label: 'Lisää vinkki' }
  ],
  pisteet: [
    { id: 'lisaa', label: 'Lisää' },
    { id: 'muokkaa', label: 'Muokkaa' }
  ],
  viestit: [
    { id: 'laheta', label: 'Lähetä' }
  ],
  joukkueet: [
    { id: 'hallinta', label: 'Lisää / muokkaa' }
  ],
  pelaajat: [
    { id: 'hallinta', label: 'Lisää / muokkaa' }
  ]
}

const teamColorOptions = ['#f7e87a', '#8bd3f7', '#7ecf9a', '#f59aa5', '#f7c0c8', '#fff8dc']
const mice: { id: MouseId, label: string, image: string, foundImage: string }[] = [
  { id: 'white', label: 'Valkoinen hiiri', image: mouseWhite, foundImage: mouseWhiteFound },
  { id: 'pink', label: 'Pinkki hiiri', image: mousePink, foundImage: mousePinkFound },
  { id: 'black', label: 'Musta hiiri', image: mouseBlack, foundImage: mouseBlackFound }
]

const sortedMouseTips = computed(() => {
  return [...props.mouseTips].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
})

const sortedDailyTips = computed(() => {
  return props.dailyTips
    .filter(tip => tip.dailyTaskId === editableDailyTask.value.id)
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
})

const sortedUserMessages = computed(() => {
  return [...props.userMessages].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
})

const sortedScoreEvents = computed(() => {
  return [...props.scoreEvents].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
})

const currentActions = computed(() => actionsByDomain[activeDomain.value])
const editableDailyTask = computed(() => {
  return props.dailyTasks.find(task => task.id === selectedDailyTaskId.value) ?? props.dailyTask
})
const isHostBusy = computed(() => hostFeedback.value?.status === 'pending')
const editableDailyTaskStatus = computed<TaskStatus>(() => taskStatusFor(editableDailyTask.value))
const editableDailyTaskIsPublished = computed(() => editableDailyTask.value.id === props.activeDailyTaskId)
const editableDailyTaskCanShowGuidance = computed(() => editableDailyTaskIsPublished.value && editableDailyTaskStatus.value !== 'upcoming')
const canToggleDailyTaskGuidance = computed(() => canControlDailyTask(editableDailyTask.value) && editableDailyTaskCanShowGuidance.value)
const taskTimingActionLabel = computed(() => editableDailyTaskStatus.value === 'live' ? 'Lopeta nyt' : 'Aloita nyt')
const guidanceIsVisibleToParticipants = computed(() => editableDailyTaskCanShowGuidance.value && editableDailyTask.value.guidanceVisible)
const guidanceActionLabel = computed(() => guidanceIsVisibleToParticipants.value ? 'Piilota ohjeet' : 'Näytä ohjeet')
const dailyTaskControlSummary = computed(() => {
  if (!canControlDailyTask(editableDailyTask.value)) {
    return 'Valitse päivätehtävä käsiohjausta varten.'
  }

  const taskState = editableDailyTaskStatus.value === 'live'
    ? 'Tehtävä on käynnissä'
    : editableDailyTaskStatus.value === 'upcoming'
      ? 'Tehtävä ei ole vielä käynnissä'
      : 'Tehtävä on päättynyt'
  const guidanceState = guidanceVisibilitySummary(
    editableDailyTask.value,
    editableDailyTaskStatus.value,
    editableDailyTaskIsPublished.value
  )

  return `${taskState} ja ${guidanceState}.`
})

onMounted(() => {
  taskStatusTimer = window.setInterval(() => {
    now.value = Date.now()
  }, 1000)
})

onBeforeUnmount(() => {
  if (feedbackTimeout) {
    window.clearTimeout(feedbackTimeout)
  }

  if (taskStatusTimer) {
    window.clearInterval(taskStatusTimer)
  }

  emit('hostFeedbackChange', null)
})

watch(hostFeedback, feedback => {
  emit('hostFeedbackChange', feedback)
}, { immediate: true })

watch(() => props.players.map(player => player.id).join('|'), () => {
  if (!props.players.some(player => player.id === userMessageRecipientId.value)) {
    userMessageRecipientId.value = props.players[0]?.id ?? ''
  }
})

watch(() => props.dailyTasks.map(task => task.id).join('|'), () => {
  if (!props.dailyTasks.some(task => task.id === selectedDailyTaskId.value)) {
    selectedDailyTaskId.value = props.activeDailyTaskId
  }
})

watch(() => props.activeDailyTaskId, taskId => {
  if (!props.dailyTasks.some(task => task.id === selectedDailyTaskId.value)) {
    selectedDailyTaskId.value = taskId
  }
})

watch(
  () => [
    editableDailyTask.value.id,
    editableDailyTask.value.title,
    editableDailyTask.value.location,
    editableDailyTask.value.preparationText,
    editableDailyTask.value.instructions,
    editableDailyTask.value.startsAt,
    editableDailyTask.value.endsAt
  ],
  (nextTaskValues, previousTaskValues) => {
    if (activeDomain.value === 'paivatehtava' && activeAction.value === 'hallinta') {
      const didSwitchTask = nextTaskValues[0] !== previousTaskValues?.[0]

      if (isDailyTaskDraftDirty.value && !didSwitchTask) {
        return
      }

      syncDailyTaskDraft(editableDailyTask.value)
    }
  }
)

watch(
  () => [
    dailyTaskDraft.title,
    dailyTaskDraft.location,
    dailyTaskDraft.preparationText,
    dailyTaskDraft.instructions,
    dailyTaskStartDraft.value,
    dailyTaskEndDraft.value
  ],
  () => {
    if (!isSyncingDailyTaskDraft && activeDomain.value === 'paivatehtava' && isDailyTaskDraftAction(activeAction.value)) {
      isDailyTaskDraftDirty.value = true
    }
  }
)

watch([activeDomain, activeAction], ([domain, action]) => {
  if (domain !== 'paivatehtava') {
    return
  }

  if (action === 'hallinta') {
    syncDailyTaskDraft(editableDailyTask.value)
    return
  }

  resetDailyTaskDraft()
})

function selectDomain (domain: HostDomain): void {
  if (domain === activeDomain.value) {
    return
  }

  if (!confirmDiscardDailyTaskDraft()) {
    return
  }

  activeDomain.value = domain
  activeAction.value = actionsByDomain[domain][0].id
}

function selectAction (action: HostAction): void {
  if (action !== activeAction.value && !confirmDiscardDailyTaskDraft()) {
    return
  }

  activeAction.value = action
}

function submitTip (): void {
  runHostActivity('Julkaistaan hiirivinkkiä', () => {
    emit('addMouseTip', {
      id: window.crypto?.randomUUID?.() ?? `tip-${Date.now()}`,
      mouseId: mouseId.value,
      text: tipText.value,
      createdAt: new Date().toISOString()
    })

    tipText.value = ''
  })
}

function submitDailyTip (): void {
  runHostActivity('Julkaistaan päivävinkkiä', () => {
    emit('addDailyTip', {
      id: window.crypto?.randomUUID?.() ?? `daily-tip-${Date.now()}`,
      dailyTaskId: editableDailyTask.value.id,
      text: dailyTipText.value,
      createdAt: new Date().toISOString()
    })

    dailyTipText.value = ''
  })
}

function submitUserMessage (): void {
  if (!userMessageRecipientId.value) {
    return
  }

  runHostActivity('Lähetetään viestiä', () => {
    emit('addUserMessage', {
      id: window.crypto?.randomUUID?.() ?? `message-${Date.now()}`,
      recipientPlayerId: userMessageRecipientId.value,
      text: userMessageText.value,
      createdAt: new Date().toISOString()
    })

    userMessageText.value = ''
  })
}

function createDailyTaskSetup (): void {
  const validationError = validateDailyTaskDraft()

  if (validationError) {
    showHostFeedback('error', validationError)
    return
  }

  runHostActivity('Tallennetaan päivätehtävää', () => {
    const task = {
      ...dailyTaskFromDraft(),
      id: window.crypto?.randomUUID?.() ?? `daily-task-${Date.now()}`,
      guidanceVisible: false
    }

    emit('createDailyTask', task)
    selectedDailyTaskId.value = task.id
    activeAction.value = 'hallinta'
    syncDailyTaskDraft(task)
  }, 'Päivätehtävä lisätty, ei vielä osallistujilla')
}

function submitDailyTaskSetup (): void {
  const validationError = validateDailyTaskDraft()

  if (validationError) {
    showHostFeedback('error', validationError)
    return
  }

  runHostActivity('Tallennetaan muutoksia', () => {
    emit('updateDailyTask', dailyTaskFromDraft())
    isDailyTaskDraftDirty.value = false
  })
}

function isDailyTaskDraftAction (action: HostAction): boolean {
  return action === 'luo' || action === 'hallinta'
}

function confirmDiscardDailyTaskDraft (): boolean {
  if (activeDomain.value !== 'paivatehtava' || !isDailyTaskDraftAction(activeAction.value) || !isDailyTaskDraftDirty.value) {
    return true
  }

  if (!confirmAction('Hylätäänkö tallentamattomat muutokset päivätehtävästä?')) {
    return false
  }

  isDailyTaskDraftDirty.value = false
  return true
}

function canRemoveDailyTask (task: DailyTask): boolean {
  return props.dailyTasks.some(item => item.id === task.id)
}

function canControlDailyTask (task: DailyTask): boolean {
  return props.dailyTasks.some(item => item.id === task.id)
}

function guidanceVisibilitySummary (task: DailyTask, status: TaskStatus, isPublished: boolean): string {
  if (!isPublished) {
    return 'ohjeet eivät näy osallistujille, koska tehtävää ei ole valittu näkyviin'
  }

  if (status === 'upcoming') {
    return task.guidanceVisible
      ? 'ohjeet avautuvat, kun tehtävä aloitetaan'
      : 'ohjeet ovat piilossa osallistujilta'
  }

  return task.guidanceVisible
    ? 'ohjeet näkyvät osallistujille'
    : 'ohjeet ovat piilossa osallistujilta'
}

function validateDailyTaskDraft (): string | null {
  if (!dailyTaskDraft.title.trim()) {
    return 'Päivätehtävän otsikko puuttuu.'
  }

  if (!dailyTaskDraft.location.trim()) {
    return 'Päivätehtävän paikka puuttuu.'
  }

  if (!dailyTaskStartDraft.value || !dailyTaskEndDraft.value) {
    return 'Päivätehtävän aloitus- ja lopetusaika puuttuvat.'
  }

  if (new Date(dailyTaskStartDraft.value).getTime() >= new Date(dailyTaskEndDraft.value).getTime()) {
    return 'Lopetusajan pitää olla aloitusajan jälkeen.'
  }

  if (!dailyTaskDraft.preparationText.trim() || !dailyTaskDraft.instructions.trim()) {
    return 'Päivätehtävän ohjetekstit puuttuvat.'
  }

  return null
}

function dailyTaskFromDraft (): DailyTask {
  return {
    ...editableDailyTask.value,
    title: dailyTaskDraft.title,
    location: dailyTaskDraft.location,
    preparationText: dailyTaskDraft.preparationText,
    instructions: dailyTaskDraft.instructions,
    startsAt: fromDateTimeLocalValue(dailyTaskStartDraft.value),
    endsAt: fromDateTimeLocalValue(dailyTaskEndDraft.value)
  }
}

function selectDailyTask (task: DailyTask): void {
  if (isDailyTaskDraftDirty.value && !confirmAction('Hylätäänkö tallentamattomat muutokset ja vaihdetaan tehtävää?')) {
    return
  }

  selectedDailyTaskId.value = task.id
  syncDailyTaskDraft(task)
}

function publishSelectedDailyTask (): void {
  runHostActivity('Näytetään tehtävää osallistujille', () => {
    saveDirtyDailyTaskDraftForLiveAction()
    emit('setActiveDailyTask', editableDailyTask.value.id)
  }, 'Tehtävä valittu osallistujille')
}

function syncDailyTaskDraft (task: DailyTask): void {
  isSyncingDailyTaskDraft = true
  dailyTaskDraft.title = task.title
  dailyTaskDraft.location = task.location
  dailyTaskDraft.preparationText = task.preparationText
  dailyTaskDraft.instructions = task.instructions
  dailyTaskStartDraft.value = toDateTimeLocalValue(task.startsAt)
  dailyTaskEndDraft.value = toDateTimeLocalValue(task.endsAt)
  isDailyTaskDraftDirty.value = false
  window.setTimeout(() => {
    isSyncingDailyTaskDraft = false
  }, 0)
}

function resetDailyTaskDraft (): void {
  isSyncingDailyTaskDraft = true
  dailyTaskDraft.title = ''
  dailyTaskDraft.location = ''
  dailyTaskDraft.preparationText = ''
  dailyTaskDraft.instructions = ''
  dailyTaskStartDraft.value = ''
  dailyTaskEndDraft.value = ''
  isDailyTaskDraftDirty.value = false
  window.setTimeout(() => {
    isSyncingDailyTaskDraft = false
  }, 0)
}

function saveDirtyDailyTaskDraftForLiveAction (): void {
  if (!isDailyTaskDraftDirty.value) {
    return
  }

  const validationError = validateDailyTaskDraft()

  if (validationError) {
    throw new Error(validationError)
  }

  emit('updateDailyTask', dailyTaskFromDraft())
  isDailyTaskDraftDirty.value = false
}

function saveDailyTip (tip: DailyTip): void {
  runHostActivity('Tallennetaan päivävinkkiä', () => {
    emit('updateDailyTip', {
      ...tip,
      text: dailyDrafts[tip.id] ?? tip.text
    })
  })
}

function removeDailyTip (tipId: string): void {
  if (!confirmAction('Poistetaanko tämä päivävinkki? Tätä ei voi kumota.')) {
    return
  }

  runHostActivity('Poistetaan päivävinkkiä', () => {
    emit('removeDailyTip', tipId)
    delete dailyDrafts[tipId]
  })
}

function saveUserMessage (message: UserMessage): void {
  runHostActivity('Tallennetaan viestiä', () => {
    emit('updateUserMessage', {
      ...message,
      text: userMessageDrafts[message.id] ?? message.text
    })

    delete userMessageDrafts[message.id]
  })
}

function removeUserMessage (messageId: string): void {
  if (!confirmAction('Poistetaanko tämä viesti? Pelaaja ei näe sitä enää.')) {
    return
  }

  runHostActivity('Poistetaan viestiä', () => {
    emit('removeUserMessage', messageId)
    delete userMessageDrafts[messageId]
  })
}

function removeDailyTask (taskId: string): void {
  if (!confirmAction(`Poistetaanko tehtävä "${editableDailyTask.value.title}"? Tehtävän pisteet ja päivävinkit poistuvat samalla.`)) {
    return
  }

  runHostActivity('Poistetaan päivätehtävää', () => {
    emit('removeDailyTask', taskId)
  })
}

function saveMouseTip (tip: MouseTip): void {
  runHostActivity('Tallennetaan hiirivinkkiä', () => {
    emit('updateMouseTip', {
      ...tip,
      mouseId: selectedTipMouse(tip),
      text: mouseDrafts[tip.id] ?? tip.text
    })
  })
}

function removeMouseTip (tipId: string): void {
  if (!confirmAction('Poistetaanko tämä hiirivinkki? Tätä ei voi kumota.')) {
    return
  }

  runHostActivity('Poistetaan hiirivinkkiä', () => {
    emit('removeMouseTip', tipId)
    delete mouseDrafts[tipId]
    delete mouseTipSelections[tipId]
  })
}

function updateScoreDraft (event: ScoreEvent, draft: ScoreDraft): void {
  scoreDrafts[event.id] = {
    ...scoreDrafts[event.id],
    ...draft
  }
}

function updateScoreCategory (event: ScoreEvent, category: ScoreCategory): void {
  const dailyTaskId = category === 'paivatehtava' ? scoreDailyTaskId(event) || defaultDailyTaskId(props.dailyTasks, props.activeDailyTaskId) : undefined
  const selectedTask = props.dailyTasks.find(task => task.id === dailyTaskId)
  const defaults = scoreDefaultsForCategory(category, selectedTask)

  updateScoreDraft(event, {
    category,
    dailyTaskId,
    title: defaults.title,
    points: defaults.points
  })
}

function updateScoreTask (event: ScoreEvent, task: DailyTask): void {
  updateScoreDraft(event, {
    dailyTaskId: task.id,
    title: task.title
  })
}

function saveScore (event: ScoreEvent): void {
  const category = scoreCategory(event)
  const nextEvent: ScoreEvent = {
    ...event,
    teamId: scoreTeam(event),
    category,
    dailyTaskId: category === 'paivatehtava' ? scoreDailyTaskId(event) : undefined,
    title: scoreTitle(event).trim(),
    points: scorePoints(event),
    description: scoreDescription(event)
  }
  const validationError = validateScoreEvent(nextEvent, props.teams, props.dailyTasks)

  if (validationError) {
    showHostFeedback('error', validationError)
    return
  }

  if (duplicateDailyScoreEvents(nextEvent, event.id).length) {
    showHostFeedback('error', 'Tälle joukkueelle on jo päivätehtävän pisteet. Poista toinen kirjaus tai muokkaa olemassa olevaa.')
    return
  }

  runHostActivity('Tallennetaan pisteitä', () => {
    emit('updateScore', nextEvent)
    delete scoreDrafts[event.id]
  })
}

function submitScore (event: ScoreEvent, accept: (accepted: boolean) => void): void {
  const validationError = validateScoreEvent(event, props.teams, props.dailyTasks)

  if (validationError) {
    showHostFeedback('error', validationError)
    accept(false)
    return
  }

  const duplicates = duplicateDailyScoreEvents(event)

  if (duplicates.length > 1) {
    showHostFeedback('error', 'Tällä joukkueella on useampi päivätehtävän pistekirjaus. Korjaa ne Muokkaa-näkymässä.')
    accept(false)
    return
  }

  const duplicate = duplicates[0]

  if (duplicate) {
    const message = `Joukkueella ${teamNameForScore(event.teamId, props.teams)} on jo pisteet tehtävälle "${scoreTaskTitle(event)}" (${duplicate.points}p). Päivitetäänkö arvoksi ${event.points}p?`

    if (!confirmAction(message)) {
      showHostFeedback('success', 'Pistekirjausta ei muutettu.', 2200)
      accept(false)
      return
    }

    accept(true)
    runHostActivity('Päivitetään pisteitä', () => {
      emit('updateScore', {
        ...duplicate,
        teamId: event.teamId,
        category: event.category,
        dailyTaskId: event.dailyTaskId,
        title: event.title,
        points: event.points,
        description: event.description
      })
    }, 'Pistekirjaus päivitetty')
    return
  }

  accept(true)
  runHostActivity('Tallennetaan pisteitä', () => {
    emit('addScore', event)
  }, 'Pistekirjaus lisätty')
}

function removeScore (eventId: string): void {
  const event = props.scoreEvents.find(scoreEvent => scoreEvent.id === eventId)

  if (!event) {
    return
  }

  if (!confirmAction(`Poistetaanko "${scoreEntryLabel(event)}"? Pisteet poistuvat taulukosta heti.`)) {
    return
  }

  runHostActivity('Poistetaan pistekirjausta', () => {
    emit('removeScore', eventId)
    delete scoreDrafts[eventId]
  })
}

function cancelScoreDraft (eventId: string): void {
  delete scoreDrafts[eventId]
}

function isScoreDirty (event: ScoreEvent): boolean {
  return !!scoreDrafts[event.id]
}

function duplicateDailyScoreEvents (event: ScoreEvent, exceptEventId?: string): ScoreEvent[] {
  const key = dailyTaskScoreKey(event)

  if (!key) {
    return []
  }

  return props.scoreEvents.filter(scoreEvent => {
    return scoreEvent.id !== exceptEventId && dailyTaskScoreKey(scoreEvent) === key
  })
}

function scoreTaskTitle (event: ScoreEvent): string {
  return props.dailyTasks.find(task => task.id === event.dailyTaskId)?.title ?? event.title
}

function scoreEntryLabel (event: ScoreEvent): string {
  const title = event.category === 'paivatehtava'
    ? props.dailyTasks.find(task => task.id === event.dailyTaskId)?.title ?? event.title
    : scoreCategoryLabel(event.category)

  return `${teamName(event.teamId)} - ${title} - ${event.points}p`
}

function submitTeam (): void {
  runHostActivity('Lisätään joukkuetta', () => {
    emit('addTeam', {
      id: window.crypto?.randomUUID?.() ?? `team-${Date.now()}`,
      name: teamNameDraft.value,
      accent: teamAccentDraft.value
    })

    teamNameDraft.value = ''
    teamAccentDraft.value = teamColorOptions[props.teams.length % teamColorOptions.length]
  })
}

function submitPlayer (): void {
  const nextPlayerName = playerNameDraft.value.trim()
  playerInviteError.value = ''

  if (!nextPlayerName) {
    playerInviteError.value = 'Pelaajan nimi puuttuu.'
    showHostFeedback('error', playerInviteError.value)
    return
  }

  if (props.players.some(player => normalizePlayerName(player.name) === normalizePlayerName(nextPlayerName))) {
    playerInviteError.value = 'Pelaaja on jo listalla.'
    showHostFeedback('error', playerInviteError.value)
    return
  }

  runHostActivity('Luodaan pelaajakoodia', async () => {
    if (!props.accessToken) {
      playerInviteError.value = 'Järjestäjän kirjautuminen puuttuu.'
      throw new Error(playerInviteError.value)
    }

    const result = await createPlayerInvite(nextPlayerName, props.accessToken)

    if (!result.invite) {
      playerInviteError.value = result.error ?? 'Pelaajakoodia ei voitu luoda.'
      throw new Error(playerInviteError.value)
    }

    latestPlayerInvite.value = result.invite
    emit('addPlayer', {
      id: result.invite.playerId,
      name: result.invite.label,
      teamId: null,
      inviteCode: result.invite.code
    })
    playerNameDraft.value = ''
  })
}

function updateTeamDraft (team: Team, draft: TeamDraft): void {
  teamDrafts[team.id] = {
    ...teamDrafts[team.id],
    ...draft
  }
}

function updatePlayerDraft (player: Player, draft: PlayerDraft): void {
  playerDrafts[player.id] = {
    ...playerDrafts[player.id],
    ...draft
  }
}

function saveTeam (team: Team): void {
  const nextName = teamDraftName(team).trim()

  if (!nextName) {
    showHostFeedback('error', 'Joukkueen nimi puuttuu.')
    return
  }

  runHostActivity('Tallennetaan joukkuetta', () => {
    emit('updateTeam', {
      ...team,
      name: nextName,
      accent: teamDraftAccent(team)
    })

    delete teamDrafts[team.id]
  })
}

function savePlayer (player: Player): void {
  const nextName = playerDraftName(player).trim()

  playerInviteError.value = ''

  if (!nextName) {
    playerInviteError.value = 'Pelaajan nimi puuttuu.'
    showHostFeedback('error', playerInviteError.value)
    return
  }

  if (hasDuplicatePlayerName(player, nextName)) {
    playerInviteError.value = 'Pelaaja on jo listalla.'
    showHostFeedback('error', playerInviteError.value)
    return
  }

  runHostActivity('Tallennetaan pelaajaa', () => {
    emit('updatePlayer', {
      ...player,
      name: nextName,
      teamId: playerDraftTeamId(player),
      inviteCode: playerDraftInviteCode(player)
    })

    delete playerDrafts[player.id]
  })
}

function regeneratePlayerInvite (player: Player): void {
  const nextName = playerDraftName(player).trim()

  playerInviteError.value = ''

  if (!nextName) {
    playerInviteError.value = 'Pelaajan nimi puuttuu.'
    showHostFeedback('error', playerInviteError.value)
    return
  }

  if (hasDuplicatePlayerName(player, nextName)) {
    playerInviteError.value = 'Pelaaja on jo listalla.'
    showHostFeedback('error', playerInviteError.value)
    return
  }

  runHostActivity('Luodaan pelaajakoodia', async () => {
    if (!props.accessToken) {
      playerInviteError.value = 'Järjestäjän kirjautuminen puuttuu.'
      throw new Error(playerInviteError.value)
    }

    const result = await createPlayerInvite(nextName, props.accessToken, player.id)

    if (!result.invite) {
      playerInviteError.value = result.error ?? 'Pelaajakoodia ei voitu luoda.'
      throw new Error(playerInviteError.value)
    }

    latestPlayerInvite.value = result.invite
    emit('updatePlayer', {
      ...player,
      name: result.invite.label,
      teamId: playerDraftTeamId(player),
      inviteCode: result.invite.code
    })

    delete playerDrafts[player.id]
  })
}

function removePlayer (playerId: string): void {
  const player = props.players.find(item => item.id === playerId)

  if (!confirmAction(`Poistetaanko pelaaja "${player?.name ?? 'Pelaaja'}"? Myös pelaajan viestit poistuvat.`)) {
    return
  }

  runHostActivity('Poistetaan pelaajaa', () => {
    emit('removePlayer', playerId)
    delete playerDrafts[playerId]
  })
}

function removeTeam (teamId: TeamId): void {
  if (!confirmAction(`Poistetaanko joukkue "${teamName(teamId)}"? Joukkueen pisteet, hiirilöydöt ja pelaajien joukkuevalinnat poistuvat samalla.`)) {
    return
  }

  runHostActivity('Poistetaan joukkuetta', () => {
    emit('removeTeam', teamId)
    delete teamDrafts[teamId]
  })
}

function selectedNullableTeamId (event: Event): TeamId | null {
  const value = inputValue(event)
  return value ? value : null
}

function playerDraftName (player: Player): string {
  return hasPlayerDraftField(player, 'name') ? playerDrafts[player.id].name ?? '' : player.name
}

function playerDraftTeamId (player: Player): TeamId | null {
  return hasPlayerDraftField(player, 'teamId') ? playerDrafts[player.id].teamId ?? null : player.teamId
}

function playerDraftInviteCode (player: Player): string | undefined {
  return hasPlayerDraftField(player, 'inviteCode') ? playerDrafts[player.id].inviteCode : player.inviteCode
}

function hasPlayerDraftField (player: Player, field: keyof PlayerDraft): boolean {
  return Object.prototype.hasOwnProperty.call(playerDrafts[player.id] ?? {}, field)
}

function hasDuplicatePlayerName (player: Player, name: string): boolean {
  return props.players.some(item => item.id !== player.id && normalizePlayerName(item.name) === normalizePlayerName(name))
}

function normalizePlayerName (name: string): string {
  return name.trim().toLocaleLowerCase('fi-FI')
}

function teamDraftName (team: Team): string {
  return teamDrafts[team.id]?.name ?? team.name
}

function teamDraftAccent (team: Team): string {
  return teamDrafts[team.id]?.accent ?? team.accent
}

function scoreTeam (event: ScoreEvent): TeamId {
  return scoreDrafts[event.id]?.teamId ?? event.teamId
}

function scoreCategory (event: ScoreEvent): ScoreCategory {
  return scoreDrafts[event.id]?.category ?? event.category
}

function scoreDailyTaskId (event: ScoreEvent): string {
  return scoreDrafts[event.id]?.dailyTaskId ?? event.dailyTaskId ?? defaultDailyTaskId(props.dailyTasks, props.activeDailyTaskId)
}

function scoreTitle (event: ScoreEvent): string {
  return scoreDrafts[event.id]?.title ?? event.title
}

function scorePoints (event: ScoreEvent): number {
  return scoreDrafts[event.id]?.points ?? event.points
}

function scoreDescription (event: ScoreEvent): string {
  return scoreDrafts[event.id]?.description ?? event.description
}

function scoreHeader (event: ScoreEvent): string {
  const category = scoreCategory(event)

  if (category !== 'paivatehtava') {
    return scoreCategoryLabel(category)
  }

  const selectedTask = props.dailyTasks.find(task => task.id === scoreDailyTaskId(event))
  return selectedTask?.title ?? scoreTitle(event) ?? scoreCategoryLabel(category)
}

function selectedTipMouse (tip: MouseTip): MouseId {
  return mouseTipSelections[tip.id] ?? tip.mouseId
}

function foundMouse (mouseId: MouseId): FoundMouse | undefined {
  return props.foundMice.find(found => found.mouseId === mouseId)
}

function toggleMouse (mouseId: MouseId): void {
  runHostActivity('Tallennetaan hiiren tilaa', () => {
    if (selectedMouseTeam.value === null) {
      emit('setMouseHidden', mouseId)
    } else {
      emit('setMouseFound', mouseId, selectedMouseTeam.value)
    }
  }, selectedMouseTeam.value === null ? 'Hiiri merkitty piiloon' : 'Hiiren löytäjä päivitetty')
}

function toggleTaskTiming (): void {
  if (editableDailyTaskStatus.value === 'live') {
    endTaskNow()
    return
  }

  startTaskNow()
}

function toggleGuidanceVisibility (): void {
  if (!canToggleDailyTaskGuidance.value) {
    return
  }

  const guidanceVisible = !guidanceIsVisibleToParticipants.value

  runHostActivity(guidanceVisible ? 'Näytetään ohjeita' : 'Piilotetaan ohjeita', () => {
    const validationError = isDailyTaskDraftDirty.value ? validateDailyTaskDraft() : null

    if (validationError) {
      throw new Error(validationError)
    }

    const task = isDailyTaskDraftDirty.value ? dailyTaskFromDraft() : editableDailyTask.value

    emit('updateDailyTask', {
      ...task,
      guidanceVisible
    })

    isDailyTaskDraftDirty.value = false
  }, guidanceVisible ? 'Ohjeet näkyvät osallistujille' : 'Ohjeet piilotettu osallistujilta')
}

function startTaskNow (): void {
  if (!canControlDailyTask(editableDailyTask.value)) {
    return
  }

  if (!confirmAction(`Aloitetaanko tehtävä "${editableDailyTask.value.title}" nyt? Tehtävä näytetään samalla osallistujille.`)) {
    return
  }

  runHostActivity('Aloitetaan tehtävää', () => {
    saveDirtyDailyTaskDraftForLiveAction()
    emit('startTaskNow', editableDailyTask.value.id)
  })
}

function endTaskNow (): void {
  if (!canControlDailyTask(editableDailyTask.value)) {
    return
  }

  if (!confirmAction(`Lopetetaanko tehtävä "${editableDailyTask.value.title}" nyt? Tehtävä näytetään samalla osallistujille ja siirretään päättyneeksi.`)) {
    return
  }

  runHostActivity('Päätetään tehtävää', () => {
    saveDirtyDailyTaskDraftForLiveAction()
    emit('endTaskNow', editableDailyTask.value.id)
  })
}

function taskStatusFor (task: DailyTask): TaskStatus {
  const startsAt = new Date(task.startsAt).getTime()
  const endsAt = new Date(task.endsAt).getTime()

  if (now.value < startsAt) {
    return 'upcoming'
  }

  if (now.value <= endsAt) {
    return 'live'
  }

  return 'ended'
}

function confirmAction (message: string): boolean {
  return window.confirm(message)
}

function runHostActivity (label: string, activity: () => void | Promise<void>, successMessage = 'Muutos tehty'): void {
  if (isHostBusy.value) {
    return
  }

  clearHostFeedbackTimer()

  hostFeedback.value = {
    status: 'pending',
    message: label
  }
  const startedAt = Date.now()

  void Promise.resolve()
    .then(activity)
    .then(() => {
      const remainingMs = Math.max(0, 520 - (Date.now() - startedAt))

      feedbackTimeout = window.setTimeout(() => {
        showHostFeedback('success', successMessage, 2600)
      }, remainingMs)
    })
    .catch(error => {
      showHostFeedback('error', error instanceof Error ? error.message : 'Toiminto epäonnistui.', 6500)
    })
}

function showHostFeedback (status: HostFeedbackStatus, message: string, timeoutMs = 4500): void {
  clearHostFeedbackTimer()
  hostFeedback.value = {
    status,
    message
  }

  if (status !== 'pending') {
    feedbackTimeout = window.setTimeout(() => {
      hostFeedback.value = null
      feedbackTimeout = undefined
    }, timeoutMs)
  }
}

function clearHostFeedbackTimer (): void {
  if (feedbackTimeout) {
    window.clearTimeout(feedbackTimeout)
    feedbackTimeout = undefined
  }
}

function teamName (teamId: TeamId | undefined): string {
  return props.teams.find(team => team.id === teamId)?.name ?? ''
}

function playerName (playerId: string): string {
  return props.players.find(player => player.id === playerId)?.name ?? 'Poistettu pelaaja'
}

function mouseLabel (mouseId: MouseId): string {
  return mice.find(mouse => mouse.id === mouseId)?.label ?? ''
}

function inputValue (event: Event): string {
  return (event.target as HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement).value
}

function toDateTimeLocalValue (value: string): string {
  const date = new Date(value)
  const offsetMs = date.getTimezoneOffset() * 60 * 1000
  return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16)
}

function fromDateTimeLocalValue (value: string): string {
  return new Date(value).toISOString()
}
</script>
