<template>
  <DemoProjectTemplate header="Finscraper">
    <template #description>
      <p>
        This tool demonstrates the use of <b><a
          href="https://github.com/jmyrberg/finscraper"
          target="_blank"
        >finscraper</a></b> Python library for fetching content from popular Finnish websites. You may define the number of items to be fetched and download them in Excel or JSON format. The maximum number of items in this demo is limited to 50 - please see the <a
          href="https://finscraper.readthedocs.io/"
          target="_blank"
        >library documentation</a> for more extensive usage.
      </p>
      <p>
        The same technology can be used for fetching any kind of content on the web. Typical use cases include automated lead generation, product price comparison, brand sentiment monitoring, or data collection for machine learning.
      </p>
    </template>
    <template #content>
      <v-container
        fluid
        class="mt-2 pt-2"
      >
        <v-row>
          <v-col
            class="my-0 py-0"
            cols="12"
            xs="12"
            sm="6"
            md="4"
          >
            <v-select
              v-model="spider"
              :items="spiderOptions"
              label="Spider"
              :loading="initLoading"
              :placeholder="initLoading ? 'Loading spiders, please wait...' : 'Select spider to use'"
            />
          </v-col>
          <v-col
            class="my-0 py-0"
            cols="12"
            xs="12"
            sm="6"
            md="4"
          >
            <v-slider
              v-model="nItems"
              class="pt-4"
              :disabled="initLoading"
              label="# items"
              hint="Number of items to fetch"
              min="1"
              max="50"
              thumb-label="always"
            />
          </v-col>
          <v-col
            class="my-0 pt-2 pb-0"
            cols="12"
            xs="12"
            sm="6"
            md="4"
          >
            <v-tooltip top>
              <template #activator="{ on }">
                <v-btn
                  :disabled="initLoading"
                  outlined
                  :loading="loading"
                  v-on="on"
                  @click="scrape"
                >
                  <v-icon left>
                    mdi-spider
                  </v-icon>
                  Scrape
                </v-btn>
              </template>
              <span>Fetch at least {{ nItems }} items</span>
            </v-tooltip>
            <v-menu
              v-if="results.length > 0"
              v-model="showDownloadMenu"
              bottom
              offset-y
              transition="slide-y-transition"
            >
              <template #activator="{ on }">
                <v-btn
                  text
                  v-on="on"
                >
                  Download
                  <v-icon right>
                    {{ showDownloadMenu ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
                  </v-icon>
                </v-btn>
              </template>
              <v-list>
                <v-list-item @click="downloadExcel">
                  <v-list-item-title>
                    <v-icon
                      left
                      color="green darken-2"
                    >
                      mdi-file-excel-box
                    </v-icon>Excel
                  </v-list-item-title>
                </v-list-item>
                <v-list-item @click="downloadJSON">
                  <v-list-item-title>
                    <v-icon
                      left
                      color="yellow darken-3"
                    >
                      mdi-code-json
                    </v-icon>JSON
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </v-col>
        </v-row>
        <v-row
          class="pt-4 mt-2"
        >
          <v-expansion-panels
            focusable
          >
            <v-expansion-panel
              v-for="(item, idx) in results"
              :key="idx"
            >
              <v-expansion-panel-header>{{ idx + 1 }}: {{ 'title' in item ? item.title : ('name' in item ? item.name : item.url) }}</v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-list-item
                  v-for="(key, itemIdx) in Object.keys(item)"
                  :key="itemIdx"
                >
                  <v-list-item-content><span class="title">{{ key }}</span> {{ item[key] }}</v-list-item-content>
                </v-list-item>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-row>
      </v-container>
    </template>
  </DemoProjectTemplate>
</template>

<script>
import { saveAs } from 'file-saver'
import { mapActions } from 'vuex'
import DemoProjectTemplate from '@/components/DemoProjects/DemoProjectTemplate'
export default {
  name: 'Finscraper',
  components: {
    DemoProjectTemplate
  },
  metaInfo: {
    title: 'Finscraper | Jesse Myrberg',
    titleTemplate: null,
    meta: [
      { vmid: 'description', name: 'description', content: 'This tool demonstrates the use of finscraper Python library for fetching content from popular Finnish websites, such as is.fi, il.fi or vauva.fi' }
    ]
  },
  data: () => ({
    spider: null,
    spiderOptions: [],
    nItems: 10,
    timeout: 60,
    loading: false,
    initLoading: false,
    results: [],
    excel: null,
    showDownloadMenu: false
  }),
  computed: {
  },
  watch: {
  },
  mounted () {
    this.getSpiders()
  },
  methods: {
    scrape () {
      this.loading = true
      return this.$api.post('/finscraper', {
        data: {
          spider: this.spider,
          nItems: this.nItems,
          timeout: this.timeout
        }
      }).then(resp => {
        this.results = resp.data.data.items.slice(0, this.nItems)
        this.excel = resp.data.data.excel
        this.loading = false
        if (this.results && this.results.length === 0) {
          this.showMessage({
            message: 'Scraping seems to be prohibited from the cloud for this content. Please try changing the spider.',
            color: 'warning',
            delay: -1
          })
        }
      }).catch(err => {
        console.log(err)
        this.loading = false
        this.showMessage({
          message: err.response && err.response.data ? err.response.data.message : 'Something went wrong, please try again later :(',
          color: 'error',
          delay: -1
        })
      })
    },
    getSpiders () {
      this.initLoading = true
      this.$api.get('/finscraper').then(resp => {
        this.spiderOptions = resp.data.data
        if (this.spider === null && this.spiderOptions.length > 0) {
          this.spider = this.spiderOptions[0].value
        }
        this.initLoading = false
      }).catch(err => {
        console.log(err)
        this.showMessage({
          message: err.response && err.response.data ? err.response.data.message : 'Something went wrong, please try again later :(',
          color: 'error',
          delay: -1
        })
        this.initLoading = false
      })
    },
    b64toBlob (b64Data, contentType, sliceSize = 15) {
      const byteCharacters = atob(b64Data)
      const byteArrays = []

      for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
        const slice = byteCharacters.slice(offset, offset + sliceSize)

        const byteNumbers = new Array(slice.length)
        for (let i = 0; i < slice.length; i++) {
          byteNumbers[i] = slice.charCodeAt(i)
        }

        const byteArray = new Uint8Array(byteNumbers)
        byteArrays.push(byteArray)
      }

      const blob = new Blob(byteArrays, { type: contentType })
      return blob
    },
    downloadExcel () {
      const blob = this.b64toBlob(this.excel, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=utf-8')
      saveAs(blob, 'data.xlsx')
    },
    downloadJSON () {
      const blob = new Blob([JSON.stringify(this.results)], { type: 'data:text/json;charset=utf-8' })
      saveAs(blob, 'data.json')
    },
    ...mapActions(['showMessage'])
  }
}
</script>

<style scoped>
</style>
