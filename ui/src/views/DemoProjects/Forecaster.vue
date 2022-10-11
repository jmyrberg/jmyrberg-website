<template>
  <DemoProjectTemplate header="Forecaster">
    <template #description>
      <p>
        TODO: Explanation
      </p>
    </template>
    <template #content>
      <v-container
        fluid
        class="mt-1 pt-1 mx-0 px-0"
      >
        <v-stepper
          v-model="step"
          flat
        >
          <v-row justify="center">
            <v-col
              xs="12"
              sm="12"
              md="10"
              lg="10"
              xl="8"
            >
              <v-stepper-header>
                <v-stepper-step
                  :complete="maxEditableStep > 1"
                  :editable="maxEditableStep >= 1"
                  edit-icon="$complete"
                  step="1"
                  @click="step = 1"
                >
                  Data
                </v-stepper-step>
                <v-divider />
                <v-stepper-step
                  :complete="maxEditableStep > 2"
                  :editable="maxEditableStep >= 2"
                  edit-icon="$complete"
                  step="2"
                >
                  Parameters
                </v-stepper-step>
                <v-divider />
                <v-stepper-step
                  :complete="maxEditableStep > 3"
                  :editable="maxEditableStep >= 3"
                  edit-icon="$complete"
                  step="3"
                >
                  Forecast
                </v-stepper-step>
              </v-stepper-header>
            </v-col>
          </v-row>

          <v-stepper-content
            class="my-2 py-2 mx-1 px-1"
            step="1"
          >
            <v-row
              justify="center"
            >
              <v-col
                xs="12"
                sm="8"
                md="6"
                lg="6"
                xl="6"
              >
                <v-file-input
                  v-model="file"
                  prepend-icon=""
                  :loading="loadingPrepare || loadingSampleFile"
                  accept=".csv,.xls,.xlsx"
                  label="Select Excel or CSV file..."
                >
                  <template #prepend-inner>
                    <v-icon
                      left
                      color="green darken-2"
                    >
                      mdi-file-excel-box
                    </v-icon>
                  </template>
                </v-file-input>
              </v-col>
            </v-row>
            <v-row
              justify="center"
            >
              <v-col
                class="mt-0 pt-0"
                cols="12"
                align="center"
                justify="center"
              >
                <span class="h1 text-uppercase font-weight-light">OR</span>
              </v-col>
              <v-col
                cols="12"
                align="center"
                justify="center"
              >
                <v-btn
                  outlined
                  :disabled="loadingPrepare || loadingSampleFile"
                  @click="getSampleFile"
                >
                  Use a sample file
                </v-btn>
              </v-col>
            </v-row>
          </v-stepper-content>

          <v-stepper-content
            class="my-2 py-2 mx-1 px-1"
            step="2"
          >
            <v-row
              cols="12"
              justify="center"
            >
              <v-col
                xs="12"
                sm="12"
                md="10"
                lg="10"
                xl="8"
              >
                <v-row cols="12">
                  <v-col
                    align="left"
                    xs="12"
                    sm="6"
                    md="6"
                    lg="6"
                    xl="6"
                  >
                    <small>Date column</small>
                    <v-tooltip
                      v-if="dateColValueHint"
                      top
                    >
                      <template #activator="{ on, attrs }">
                        <v-icon
                          class="ml-1"
                          color="warning"
                          dark
                          small
                          v-bind="attrs"
                          v-on="on"
                        >
                          mdi-information-outline
                        </v-icon>
                      </template>
                      <span>{{ dateColValueHint }}</span>
                    </v-tooltip>
                    <v-chip-group
                      v-model="selectedDateColValue"
                      active-class="primary--text"
                      mandatory
                    >
                      <v-chip
                        v-for="(col, i) in dateColValueOptions"
                        :key="i"
                        :value="col"
                        outlined
                      >
                        {{ col }}
                      </v-chip>
                    </v-chip-group>
                  </v-col>
                  <v-col
                    align="left"
                    xs="12"
                    sm="6"
                    md="6"
                    lg="6"
                    xl="6"
                  >
                    <small>Date frequency</small>
                    <v-tooltip
                      v-if="freqHint"
                      top
                    >
                      <template #activator="{ on, attrs }">
                        <v-icon
                          class="ml-1"
                          color="warning"
                          dark
                          small
                          v-bind="attrs"
                          v-on="on"
                        >
                          mdi-information-outline
                        </v-icon>
                      </template>
                      <span>{{ freqHint }}</span>
                    </v-tooltip>
                    <v-select
                      v-model="selectedDateCol.freq"
                      :items="freqOptions"
                      class="mt-0 pt-1"
                      single-line
                    />
                  </v-col>
                </v-row>
                <v-row
                  class="my-0 py-0"
                  cols="12"
                >
                  <v-col
                    align="left"
                    xs="12"
                    sm="6"
                    md="6"
                    lg="6"
                    xl="6"
                  >
                    <small>Forecast column</small>
                    <v-chip-group
                      v-model="selectedForecastColValue"
                      active-class="primary--text"
                      mandatory
                    >
                      <v-chip
                        v-for="(col, i) in forecastColValueOptions"
                        :key="i"
                        :value="col"
                        outlined
                      >
                        {{ col }}
                      </v-chip>
                    </v-chip-group>
                  </v-col>
                  <v-col
                    align="left"
                    xs="12"
                    sm="6"
                    md="6"
                    lg="6"
                    xl="6"
                  >
                    <small>Horizon</small>
                    <v-slider
                      v-model="horizon"
                      :disabled="!readyToForecast"
                      min="1"
                      max="48"
                      :thumb-size="24"
                      thumb-label="always"
                      class="mt-1 pt-1"
                    />
                  </v-col>
                </v-row>
                <v-row class="my-0 py-0">
                  <v-col
                    align="right"
                  >
                    <v-tooltip
                      top
                    >
                      <template #activator="{ on, attrs }">
                        <v-btn
                          v-bind="attrs"
                          :disabled="!readyToForecast"
                          :loading="loadingForecast"
                          outlined
                          v-on="on"
                          @click="getForecast"
                        >
                          <v-icon left>
                            mdi-chart-line-variant
                          </v-icon>
                          Forecast
                        </v-btn>
                      </template>
                      <span>
                        <small>Will forecast "{{ selectedForecastColValue }}" {{ horizon }} {{ selectedFreq.saying }} ahead {{ selectedDateColValue === '(auto)' ? 'by creating an integer index for dates' : 'with "' + selectedDateColValue + '" as date' }}</small>
                      </span>
                    </v-tooltip>
                  </v-col>
                </v-row>
              </v-col>
            </v-row>
          </v-stepper-content>

          <v-stepper-content
            class="my-2 py-2 mx-0 px-0"
            step="3"
          >
            <div id="chart">
              <ApexChart
                :options="chartOptions"
                :series="forecast.series"
              />
            </div>
          </v-stepper-content>
        </v-stepper>
      </v-container>
    </template>
  </DemoProjectTemplate>
</template>

<script>
import { mapActions } from 'vuex'
import DemoProjectTemplate from '@/components/DemoProjects/DemoProjectTemplate'
export default {
  name: 'Forecaster',
  components: {
    DemoProjectTemplate
  },
  data: () => ({
    step: 1,
    maxEditableStep: 0,
    file: null,
    isSelecting: false,
    selectedForecastColValue: null,
    selectedDateColValue: null,
    horizon: 24,
    defaultFreqOptions: [
      { text: 'Hourly', value: 'H', saying: 'hours' },
      { text: 'Daily', value: 'D', saying: 'days' },
      { text: 'Weekly', value: 'W', saying: 'weeks' },
      { text: 'Monthly', value: 'M', saying: 'months' },
      { text: 'Quarterly', value: 'Q', saying: 'quarters' },
      { text: 'Annual', value: 'A', saying: 'years' }
    ],
    rankDateCol: { value: '(auto)', dtype: 'datetime', dtypeName: 'date', freq: 'D' },
    originalColumns: [],
    columns: [],
    forecast: { series: [], dates: [], xAxisType: 'datetime' },
    loadingSampleFile: false,
    loadingPrepare: false,
    loadingForecast: false
  }),
  computed: {
    allCols () {
      return [this.rankDateCol].concat(this.columns)
    },
    selectedDateCol () {
      return this.selectedDateColValue ? this.allCols.find(x => x.value === this.selectedDateColValue) : this.rankDateCol
    },
    selectedForecastCol () {
      return this.columns
        .find(x => x.value === this.selectedForecastColValue)
    },
    selectedOriginalFreq () {
      return this.originalColumns.find(x => x.value === this.selectedDateColValue).freq
    },
    selectedFreq () {
      return this.freqOptions.find(x => x.value === this.selectedDateCol.freq)
    },
    freqOptions () {
      const originalCol = this.originalColumns.find(x => x.value === this.selectedDateColValue)
      if (originalCol && originalCol.freq && !this.defaultFreqOptions.map(x => x.value).includes(originalCol.freq)) {
        const newFreqOption = { text: 'Auto (' + originalCol.freq + ')', value: originalCol.freq, saying: 'periods' }
        // eslint-disable-next-line no-undef
        const newOptions = structuredClone(this.defaultFreqOptions)
        return [newFreqOption].concat(newOptions)
      } else {
        return this.defaultFreqOptions
      }
    },
    freqHint () {
      // Recommend setting frequency to "auto", when it's automatically detected
      const autoFreq = this.freqOptions.find(x => x.text.includes('Auto (') && x.saying === 'periods')
      const autoFreqSelected = this.selectedFreq.text.includes('Auto (') && this.selectedFreq.saying === 'periods'
      if (autoFreq && !autoFreqSelected) {
        return `Warning: The frequency of "${this.selectedDateColValue}" was automatically detected as "${autoFreq.text}", which your current selection "${this.selectedFreq.text}" will override`
      } else {
        return null
      }
    },
    forecastColValueOptions () {
      return this.columns
        .filter(x => ['integer', 'float'].includes(x.dtypeName))
        .map(x => x.value)
    },
    dateColValueOptions () {
      const options = this.allCols.filter(x => ['date'].includes(x.dtypeName)).map(x => x.value)
      return options.length > 1 ? options.filter(x => x !== '(auto)') : options
    },
    dateColValueHint () {
      if (this.selectedDateColValue === '(auto)') {
        return 'Warning: No date columns were detected! An integer index will be automatically created and used as a date column'
      } else {
        return null
      }
    },
    readyToForecast () {
      return this.file && this.columns.length > 0 && this.selectedDateColValue && this.selectedForecastColValue && this.dateColValueOptions.includes(this.selectedDateColValue) && this.forecastColValueOptions.includes(this.selectedForecastColValue)
    },
    chartOptions () {
      return {
        chart: {
          type: 'line',
          stacked: false,
          height: this.$vuetify.breakpoint.lgAndUp ? 500 : 350,
          zoom: {
            type: 'x',
            enabled: true,
            autoScaleYaxis: true
          },
          toolbar: {
            autoSelected: 'pan',
            tools: {
              download: true,
              selection: true,
              zoom: true,
              zoomin: true,
              zoomout: true,
              pan: true,
              reset: true
            },
            export: {
              csv: {
                filename: 'jmyrberg-forecaster-' + this.selectedForecastColValue,
                dateFormatter: (timestamp) => {
                  return new Date(timestamp).toISOString()
                }
              },
              svg: {
                filename: 'jmyrberg-forecaster-' + this.selectedForecastColValue
              },
              png: {
                filename: 'jmyrberg-forecaster-' + this.selectedForecastColValue
              }
            }
          },
          animations: {
            enabled: false
          }
        },
        forecastDataPoints: {
          count: this.horizon
        },
        stroke: {
          curve: 'straight'
        },
        dataLabels: {
          enabled: false
        },
        markers: {
          size: 0
        },
        title: {
          text: 'Forecast for "' + this.selectedForecastColValue + '"',
          align: 'left'
        },
        yaxis: {
          show: true,
          forceNiceScale: true,
          labels: {
            formatter: (val) => {
              return val
            }
          },
          title: {
            text: undefined
          }
        },
        xaxis: {
          type: this.forecast.xAxisType,
          categories: this.forecast.dates,
          tickAmount: 12,
          title: {
            text: this.selectedDateColValue
          },
          tickPlacement: 'on'
        },
        tooltip: {
          shared: true,
          y: {
            formatter: (val) => {
              return val ? (val % 1 === 0 ? val : val.toFixed(2)) : val
            }
          }
        }
      }
    },
    step1Hash () {
      return this.file
    },
    step2Hash () {
      return {
        selectedForecastValue: this.selectedForecastColValue,
        selectedDateColValue: this.selectedDateColValue,
        selectedDateColFreq: this.selectedDateCol.freq,
        horizon: this.horizon
      }
    }
  },
  watch: {
    file (newFile, oldFile) {
      if (newFile && newFile !== oldFile) {
        this.getPrepare()
      }
    },
    forecastColValueOptions (newOpts, oldOpts) {
      // No options --> unselect
      if (newOpts === null || newOpts === undefined || newOpts.length === 0) {
        this.selectedForecastColValue = null
      // Selection not in new options --> select first
      } else if (!newOpts.includes(this.selectedForecastColValue)) {
        this.selectedForecastColValue = newOpts[0]
      }
    },
    dateColValueOptions (newOpts, oldOpts) {
      // No options --> unselect
      if (newOpts === null || newOpts === undefined || newOpts.length === 0) {
        this.selectedDateColValue = null
      // Selection not in new options --> select last (to avoid (auto))
      } else if (!newOpts.includes(this.selectedDateColValue)) {
        this.selectedDateColValue = newOpts[newOpts.length - 1]
      }
    },
    step1Hash (newHash, oldHash) {
      this.maxEditableStep = 1
    },
    step2Hash: {
      handler (newHash, oldHash) {
        if (oldHash.selectedDateColValue !== null) {
          this.maxEditableStep = 2
        }
      },
      deep: true
    },
    step (newStep, oldStep) {
      this.maxEditableStep = Math.max(this.step, this.maxEditableStep)
    }
  },
  mounted () {
  },
  methods: {
    getSampleFile () {
      const formData = new FormData()
      formData.append('mode', 'sampleFile')
      this.loadingSampleFile = true
      return this.$api.post('/forecaster', formData)
        .then(resp => {
          const data = resp.data.data
          this.file = this.b64ExcelToFile(data.excel, 'sample-data.xlsx')
          this.loadingSampleFile = false
        }).catch(err => {
          this.loadingSampleFile = false
          this.showMessage({
            message: err.response && err.response.data ? err.response.data.message : 'Something went wrong, please try again later :(',
            color: 'error',
            delay: -1
          })
        })
    },
    getPrepare () {
      if (this.file) {
        const formData = new FormData()
        formData.append('mode', 'prepare')
        formData.append('inputFile', this.file, this.file.name)
        this.loadingPrepare = true
        return this.$api.post('/forecaster', formData)
          .then(resp => {
            const data = resp.data.data
            this.columns = data.columns
            // eslint-disable-next-line no-undef
            this.originalColumns = structuredClone(this.columns)
            this.loadingPrepare = false
            this.step = 2
          }).catch(err => {
            this.loadingPrepare = false
            this.showMessage({
              message: err.response && err.response.data ? err.response.data.message : 'Something went wrong, please try again later :(',
              color: 'error',
              delay: -1
            })
          })
      }
    },
    getForecast () {
      if (this.readyToForecast) {
        this.maxEditableStep = 3
        const formData = new FormData()
        formData.append('mode', 'forecast')
        formData.append('inputFile', this.file, this.file.name)
        const params = new Blob([JSON.stringify({
          selectedDateCol: this.selectedDateCol.value,
          selectedDateColFreq: this.selectedDateCol.freq,
          selectedForecastCol: this.selectedForecastCol.value,
          horizon: this.horizon
        })], {
          type: 'application/json'
        })
        formData.append('params', params)
        this.loadingForecast = true
        return this.$api.post('/forecaster', formData)
          .then(resp => {
            const data = resp.data.data
            this.forecast = data.forecast
            this.loadingForecast = false
            this.step = 3
            this.maxEditableStep = 4
          }).catch(err => {
            this.loadingForecast = false
            this.showMessage({
              message: err.response && err.response.data ? err.response.data.message : 'Something went wrong, please try again later :(',
              color: 'error',
              delay: -1
            })
          })
      }
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
    b64ExcelToFile (excel, filename) {
      const blob = this.b64toBlob(excel, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=utf-8')
      return new File([blob], filename)
    },
    ...mapActions(['showMessage'])
  }
}
</script>

<style scoped>
  .v-stepper__header {
    box-shadow: none;
  }
</style>
