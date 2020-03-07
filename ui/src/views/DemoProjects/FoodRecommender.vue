<template>
  <DemoProjectTemplate header="Food Recommender">
    <template v-slot:description>
      <p>
        What shall I cook next? A question I ended up asking myself way too often. This app provides a shareable list that stays relevant through user interactions:
      </p>
      <div>
        <v-icon color="green" class="mr-1">mdi-silverware-fork-knife</v-icon> "I cooked this" - more likely in the future
      </div>
      <div class="mt-3 mb-3">
        <v-icon color="red" class="mr-1">mdi-update</v-icon> "Not now" - less likely in the future
      </div>
      <p class="pt-1">
        The score is based on multiplication of the following factors:
        <ul>
          <li>Recency - last time the food was cooked</li>
          <li>Frequency - how regularly this food is cooked</li>
          <li>Popularity - ratio of positive/negative actions</li>
        </ul>
      </p>
    </template>
    <template v-slot:content>
      <v-text-field
        v-model="search"
        label="Search or add item..."
        append-icon="mdi-plus"
        @click:append="addItem"
        @keydown.enter="addItem"
        autofocus
        solo
        single-line
        :rules="[ruleNameExists, ruleNameTooShort]"
      >
      </v-text-field>
      <v-row class="my-0 py-0">
        <v-col class="my-0 py-0" cols="6">
          <div class="mt-0 mb-0 py-0">
            <a
              v-if="listId === ''"
              class="overline"
              @click="createShareableLink"
            >
              <span v-if="!creatingShareableLink">Create shareable link</span>
              <span v-else>Creating link...</span>
            </a>
            <a v-else class="overline" :href="currentPath">
              Copy the target of this link to share
            </a>
          </div>
        </v-col>
        <v-col align="right" class="my-0 py-0" cols="6">
          <div v-if="!enableSaving">
          </div>
          <div v-else-if="unsavedChanges && !saving">
            <v-icon small left color="warning">mdi-content-save-alert</v-icon>
            <span class="overline">Unsaved changes</span>
          </div>
          <div v-else-if="unsavedChanges && saving">
            <v-progress-circular
              size="10"
              width="1"
              indeterminate
              color="primary"
              class="mr-2"
            >
            </v-progress-circular>
            <span class="overline">Saving...</span>
          </div>
          <div v-else-if="!unsavedChanges">
            <v-icon small left color="primary">mdi-content-save</v-icon>
          </div>
          <div v-else>
          </div>
        </v-col>
      </v-row>
      <v-data-table
        class="item-table elevation-1"
        ref="itemTable"
        :headers="headers"
        :items="itemsWithScore"
        :expanded.sync="expanded"
        :search="search"
        single-expand
        show-expand
        :mobile-breakpoint="0"
        selectable-key="selectable"
        single-select
        :value="selected"
        sort-by="score"
        :sort-desc="true"
        :items-per-page="10"
        calculate-widths
        :loading="loadingData"
      >
        <template v-slot:item.name="{ item }">
          <div v-if="item.link && item.link.length > 5">
            <a :href="item.link" target="_blank">
              <span
                class="d-inline-block text-truncate"
                :style="'max-width: ' + ($vuetify.breakpoint.smAndUp ? '100%;' : '100px;')"
              >
                <u>{{ item.name }}</u>
              </span>
            </a>
          </div>
          <div v-else>
            {{ item.name }}
          </div>
        </template>
        <template v-slot:item.data-table-expand="props">
          <v-row class="ma-0 pa-0">
            <v-icon
              class="mr-2"
              color="green"
              @click="markEaten(props.item)"
            >
              mdi-silverware-fork-knife
            </v-icon>
            <v-icon
              color="red"
              @click="markLater(props.item)"
            >
              mdi-update
            </v-icon>
            <v-spacer></v-spacer>
            <v-icon
              :class="{
                'v-data-table__expand-icon': true,
                'v-data-table__expand-icon--active': props.isExpanded && transitioned[props.item.id]
              }"
              color="primary"
              @click="toggleExpand(props)"
            >
              mdi-chevron-down
            </v-icon>
          </v-row>
        </template>
        <template v-slot:item.score="{ item }">
          <v-chip
            :color="getScoreColor(item.score)"
            @click="showScores(item)"
            dark
            small
          >
            {{ item.score }}
          </v-chip>
        </template>
        <template v-slot:expanded-item="{ headers, item }">
          <td
            :colspan="headers.length"
            :class="{'expanded-closing': !transitioned[item.id]}"
            style="height: auto;"
          >
            <v-expand-transition>
              <div v-show="transitioned[item.id]">
                <v-row>
                  <v-col class="mb-0 pb-0" cols="12" lg="6">
                    <v-text-field
                      label="Name"
                      color="primary"
                      v-model="item.name"
                      :rules="[ruleNameTooShort]"
                    ></v-text-field>
                  </v-col>
                  <v-col class="mb-0 pb-0" cols="12" lg="6">
                    <v-text-field
                      label="Link"
                      placeholder="E.g. https://kotikokki.net"
                      color="primary"
                      v-model="item.link"
                      :rules="[ruleLinkValid]"
                    ></v-text-field>
                  </v-col>
                  <v-col class="mb-0 pb-0 mt-0" cols="12">
                    <v-combobox
                      label="Tags"
                      color="primary"
                      v-model="item.tags"
                      multiple
                      chips
                      small-chips
                      deletable-chips
                      hide-details
                      hide-selected
                      :allow-overflow="false"
                    >
                    </v-combobox>
                  </v-col>
                  <v-col align="left" class="mt-4 mb-1" cols="12" lg="12">
                    <v-btn
                      color="error"
                      small
                      dark
                      outlined
                      @click="deleteItem(item)"
                    >
                      <v-icon left>mdi-delete</v-icon>
                      Remove
                    </v-btn>
                  </v-col>
                </v-row>
              </div>
            </v-expand-transition>
          </td>
        </template>
      </v-data-table>
      <v-dialog
        v-model="showScoreDialog"
        v-if="showScoreDialog"
        max-width="600"
      >
        <v-card>
          <v-card-title>Scores</v-card-title>
          <v-card-text>
            <div class="overline mt-3 mb-1"><b>R</b>ecency ({{ dialogItem.eaten.length ? 'Latest ' + moment(dialogItem.eaten.slice(-1)[0]).format('D.M.YYYY') : 'Never eaten' }})</div>
            <v-progress-linear
              color="red"
              height="20"
              :value="dialogItem.recency"
            >
              <template v-slot="{ value }">
                {{ value }} %
              </template>
            </v-progress-linear>
            <div class="overline mt-3 mb-1"><b>F</b>requency ({{ dialogItem.eaten.length ? `${dialogItem.frequency >= 0.999 ? '&ge;' : ''}` + `${dialogItem.frequency / 100} times per week` : 'Never eaten' }})</div>
            <v-progress-linear
              color="green"
              height="20"
              :value="dialogItem.frequency"
            >
              <template v-slot="{ value }">
                {{ value }} %
              </template>
            </v-progress-linear>
            <div class="overline mt-3 mb-1"><b>P</b>opularity</div>
            <v-progress-linear
              color="blue"
              height="20"
              :value="dialogItem.popularity"
            >
              <template v-slot="{ value }">
                {{ value }} %
              </template>
            </v-progress-linear>
            <div class="overline mt-3 mb-1"><b>Score = R * F * P</b></div>
            <v-progress-linear
              :color="getScoreColor(dialogItem.score)"
              height="20"
              :value="dialogItem.score"
            >
              <template v-slot="{ value }">
                <strong>{{ value }} %</strong>
              </template>
            </v-progress-linear>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              text
              @click="showScoreDialog = false"
            >
              Close
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </template>
  </DemoProjectTemplate>
</template>

<script>
import moment from 'moment'
import DemoProjectTemplate from '@/components/DemoProjects/DemoProjectTemplate'
let _ = require('lodash')
export default {
  name: 'FoodRecommender',
  props: ['id'],
  components: {
    DemoProjectTemplate
  },
  data: () => ({
    moment: moment,
    headers: [
      { text: 'Name', value: 'name' },
      { text: 'Tags', value: 'tags', align: ' d-none' }, // Hidden, but searchable
      { text: 'Score', value: 'score', sortable: true },
      { text: 'Actions', value: 'data-table-expand', width: 130, sortable: false }
    ],
    defaultItem: { name: null, picture: null, recency: null, frequency: null, popularity: null, score: null, eaten: [], markedLater: [], link: '', tags: [] },
    items: [],
    transitioned: [],
    closeTimeouts: [],
    search: '',
    listId: '',
    enableSaving: false,
    expanded: [],
    selected: [],
    showScoreDialog: false,
    dialogItem: {},
    unsavedChanges: false,
    saving: false,
    creatingShareableLink: false,
    loadingData: false
  }),
  watch: {
    items: {
      handler (newVal, oldVal) {
        if (this.enableSaving) {
          this.unsavedChanges = true
          this.saveData()
          this.saving = true
        }
      },
      deep: true
    }
  },
  computed: {
    uniqueNames () {
      const allNames = []
      this.items.forEach(x => {
        allNames.push(x.name)
      })
      return allNames.filter(this.onlyUnique)
    },
    uniqueTags () {
      const allTags = []
      this.items.forEach(x => {
        allTags.push(...x.tags)
      })
      return allTags.filter(this.onlyUnique)
    },
    itemsWithScore () {
      this.items.forEach(item => {
        const scores = this.getScores(item)
        item.recency = scores.recency
        item.frequency = scores.frequency
        item.popularity = scores.popularity
        item.score = scores.score
      })
      return this.items
    },
    currentPath () {
      return window.location.href
    }
  },
  methods: {
    getData () {
      this.loadingData = true
      return this.$api.get('/get_food_recommender', {
        params: {
          listId: this.listId
        }
      }).then(resp => {
        this.items = resp.data.data.items
        this.loadingData = false
      }).catch(err => {
        console.log(err)
        this.loadingData = false
      })
    },
    saveData: _.debounce(function () {
      this.saving = true
      return this.$api.post('/post_food_recommender',
        { data: { items: this.items } },
        { params: { listId: this.listId } }
      ).then(resp => {
        const listId = resp.data.data.listId
        if (this.$route.params.id !== listId) {
          this.$router.replace({ name: 'food-recommender', params: { id: listId } })
        }
        this.listId = listId
        this.unsavedChanges = false
        this.saving = false
        this.creatingShareableLink = false
      }).catch(err => {
        console.log(err)
        this.saving = false
      })
    }, 5000),
    createShareableLink () {
      // TODO: Create link that can be easily copied!
      this.creatingShareableLink = true
      this.unsavedChanges = true
      this.enableSaving = true
      this.saveData()
      this.saving = true
    },
    getScores (item) {
      const now = moment(new Date())
      let recency = 0.5
      let frequency = 0.5
      if (item.eaten.length > 0) {
        const lastEaten = moment(item.eaten.slice(-1)[0])
        recency = (365 - Math.min(moment.duration(now.diff(lastEaten)).asDays(), 365)) / 365

        const firstEaten = item.eaten[0]
        const eatenWeeks = moment.duration(now.diff(firstEaten)).asWeeks()
        frequency = Math.min(item.eaten.length / eatenWeeks, 1)
      }
      let popularity = item.eaten.length / (item.markedLater.length + item.eaten.length)
      if (item.markedLater.length === 0 && item.eaten.length === 0) {
        popularity = 0.5
      }
      const score = recency * frequency * popularity * 100
      return {
        recency: Math.round(recency * 100),
        frequency: Math.round(frequency * 100),
        popularity: Math.round(popularity * 100),
        score: Math.round(score)
      }
    },
    getScoreColor (score) {
      if (score < 10) {
        return 'error'
      } else if (score >= 10 && score < 50) {
        return 'warning'
      } else if (score >= 50 && score < 75) {
        return 'light-green'
      } else {
        return 'success'
      }
    },
    markEaten (item) {
      item.eaten.push(new Date())
    },
    markLater (item) {
      item.markedLater.push(new Date())
    },
    onlyUnique (value, index, self) {
      return self.indexOf(value) === index
    },
    addItem () {
      if (this.ruleNameExists(this.search) === true && this.ruleNameTooShort(this.search) === true && this.search !== '') {
        const newItem = JSON.parse(JSON.stringify(this.defaultItem))
        newItem.name = this.search
        newItem.id = this.getRandomId()
        this.items.push(newItem)
        this.search = ''
      }
    },
    deleteItem (item) {
      const index = this.items.indexOf(item)
      confirm('Are you sure you want to delete this item?') && this.items.splice(index, 1)
    },
    showScores (item) {
      this.showScoreDialog = true
      this.dialogItem = item
    },
    ruleNameExists (name) {
      return this.uniqueNames.map(x => x.toLowerCase()).indexOf(name.toLowerCase()) === -1 ? true : 'Name already exists'
    },
    ruleNameTooShort (name) {
      return name.length >= 4 || name === '' ? true : 'Name must be at least 4 characters long'
    },
    ruleLinkValid (link) {
      // eslint-disable-next-line no-useless-escape
      var res = link.match(/(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g)
      return res === null && link !== '' ? 'Please give a valid url' : true
    },
    getRandomId () {
      return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        let r = Math.random() * 16 | 0
        let v = c === 'x' ? r : (r & 0x3 | 0x8)
        return v.toString(16)
      })
    },
    toggleExpand (props) {
      // Complicated for transition purposes, relies on single expand
      // https://codepen.io/webifi/pen/ExxmXbJ?editors=1010
      const item = props.item
      const id = props.item.id
      if (props.isExpanded && this.transitioned[id]) {
        this.closeExpand(item)
        this.selected = []
      } else {
        clearTimeout(this.closeTimeouts[id])
        props.expand(true)
        this.$nextTick(() => this.$set(this.transitioned, id, true))
        this.$nextTick(() => this.expanded.forEach(i => i !== item && this.closeExpand(i)))
        this.selected = [item]
      }
    },
    closeExpand (item) {
      const id = item.id
      this.$set(this.transitioned, id, false)
      this.closeTimeouts[id] = setTimeout(() => this.$refs.itemTable.expand(item, false), 600)
    }
  },
  mounted () {
    if (this.id) {
      this.listId = this.id
      this.getData().then(() => {
        if (this.items.length > 0) {
          this.enableSaving = true
        }
      })
    }
  }
}
</script>

<style scoped>
>>>.v-data-footer {
  flex-wrap: nowrap;
}
>>>.v-data-footer__select {
  margin-left: 8px;
}
>>>.v-data-footer__select .v-select {
  margin: 13px 0 13px 13px;
}
>>>.v-data-footer__pagination {
  margin: 13px 0 13px 13px;
}
</style>
