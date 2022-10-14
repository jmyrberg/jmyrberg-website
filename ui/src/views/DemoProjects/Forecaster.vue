<template>
  <DemoProjectTemplate header="Forecaster">
    <template #description>
      <p>
        <a
          href="https://en.wikipedia.org/wiki/Time_series"
          target="_blank"
        >
          Time series forecasting
        </a>
        &nbsp;predicts the future from historical data. The main idea is to drive <i>strategic decision-making</i> through better understanding of outcomes that are more and less likely to occur in the future.
      </p>
      <p class="mb-0">
        Examples of time series forecasting use cases:
      </p>
      <div class="mt-2">
        <v-icon class="mr-3">
          mdi-cart-outline
        </v-icon>
        Product demand - keep your customers and bottom line happy by matching the inputs and outputs
      </div>
      <div class="mt-2 pt-0">
        <v-icon class="mr-3">
          mdi-web
        </v-icon>
        Website traffic - plan ahead the capacity you'll need to meet the demand
      </div>
      <div class="mt-2 pt-0">
        <v-icon class="mr-3">
          mdi-finance
        </v-icon>
        Financials - understand the future outlook to make more informed business decisions
      </div>
      <div class="mt-2 pt-0">
        <v-icon class="mr-3">
          mdi-repeat
        </v-icon>
        Understanding cyclic and seasonal patterns of your business
      </div>
      <p class="mt-5">
        Use the <b>Forecaster</b> tool below to create forecasts for your own datasets or the sample provided.
      </p>
    </template>
    <template #content>
      <v-card
        :style="{
          'min-height': chartHeight + 72 + 68 + 'px'
        }"
      >
        <v-container
          fluid
          class="mt-1 pt-1 mx-0 px-0"
        >
          <v-stepper
            v-model="step"
            flat
          >
            <v-row
              justify="center"
            >
              <v-col
                xs="12"
                sm="12"
                md="8"
                lg="8"
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
              class="my-2 py-2"
              step="1"
            >
              <v-row
                justify="center"
                cols="12"
              >
                <v-col
                  xs="12"
                  sm="12"
                  md="8"
                  lg="8"
                  xl="8"
                  align="center"
                  class="pb-1"
                >
                  <v-file-input
                    v-model="file"
                    prepend-icon=""
                    :loading="loadingPrepare || loadingSampleFile"
                    accept=".csv,.xls,.xlsx"
                    label="Select Excel or CSV file..."
                    width="100%"
                  >
                    <template #prepend-inner>
                      <v-icon
                        left
                        color="green darken-2"
                      >
                        mdi-file-excel-box
                      </v-icon>
                    </template>
                    <template #append>
                      <v-tooltip
                        open-on-click
                        :open-on-hover="false"
                        transition="slide-x-reverse-transition"
                        max-width="600"
                        close-delay="200"
                        nudge-right="10"
                        left
                      >
                        <template #activator="{ on, attrs }">
                          <v-icon
                            v-bind="attrs"
                            v-on="on"
                          >
                            mdi-information-outline
                          </v-icon>
                        </template>
                        <span>
                          Provide an Excel or CSV file that will be used for forecasting:
                          <br>
                          <li>
                            The first row should contain headers
                          </li>
                          <li>
                            At least one datetime column, preferrably with consistent frequency
                          </li>
                          <li>
                            At least one numeric column
                          </li>
                          <li>
                            Maximum number of rows is 366
                          </li>
                          <v-btn
                            class="mt-4 mb-1"
                            small
                            outlined
                            color="secondary"
                            @click="getSampleFile(downloadOnly = true)"
                          >
                            <v-icon
                              left
                              color="white"
                            >
                              mdi-download
                            </v-icon>
                            Download example
                          </v-btn>
                        </span>
                      </v-tooltip>
                    </template>
                  </v-file-input>
                </v-col>
                <v-col
                  cols="12"
                  align="center"
                  class="pt-0"
                >
                  <div class="h1 text-uppercase font-weight-light">
                    OR
                  </div>
                </v-col>
                <v-col
                  xs="12"
                  sm="12"
                  md="8"
                  lg="8"
                  xl="8"
                  align="center"
                >
                  <v-btn
                    width="100%"
                    outlined
                    :disabled="loadingPrepare || loadingSampleFile"
                    @click="getSampleFile(downloadOnly = false)"
                  >
                    Use a sample file
                  </v-btn>
                </v-col>
              </v-row>
            </v-stepper-content>

            <v-stepper-content
              class="my-2 py-2"
              step="2"
            >
              <v-row
                cols="12"
                justify="center"
              >
                <v-col
                  xs="12"
                  sm="12"
                  md="8"
                  lg="8"
                  xl="8"
                >
                  <v-row cols="12">
                    <v-col
                      align="left"
                      xs="12"
                      sm="12"
                      md="12"
                      lg="12"
                      xl="12"
                    >
                      <small>Date column</small>
                      <v-tooltip
                        v-if="dateColValueHint"
                        max-width="600"
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
                        mandatory
                      >
                        <v-chip
                          v-for="(col, i) in dateColValueOptions"
                          :key="i"
                          :value="col"
                          :text-color="col === selectedDateColValue ? 'white' : undefined"
                          :style="{
                            'background-color': col === selectedDateColValue ? '#212121' : undefined,
                          }"
                        >
                          {{ col }}
                        </v-chip>
                      </v-chip-group>
                    </v-col>
                    <v-col
                      align="left"
                      xs="12"
                      sm="12"
                      md="12"
                      lg="12"
                      xl="12"
                    >
                      <small>Date frequency</small>
                      <v-tooltip
                        v-if="freqHint"
                        max-width="600"
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
                      <v-chip-group
                        v-model="selectedDateCol.freq"
                        mandatory
                      >
                        <v-chip
                          v-for="(freq, i) in freqOptions"
                          :key="i"
                          :value="freq.value"
                          :text-color="freq === selectedFreq ? 'white' : undefined"
                          :style="{
                            'background-color': freq === selectedFreq ? '#212121' : undefined,
                          }"
                        >
                          {{ freq.text }}
                        </v-chip>
                      </v-chip-group>
                    </v-col>
                  </v-row>
                  <v-row
                    class="my-0 py-0"
                    cols="12"
                  >
                    <v-col
                      align="left"
                      xs="12"
                      sm="12"
                      md="12"
                      lg="12"
                      xl="12"
                    >
                      <small>Forecast column</small>
                      <v-chip-group
                        v-model="selectedForecastColValue"
                        mandatory
                      >
                        <v-chip
                          v-for="(col, i) in forecastColValueOptions"
                          :key="i"
                          :value="col"
                          :text-color="selectedForecastColValue === col ? 'white' : undefined"
                          :style="{
                            'background-color': selectedForecastColValue === col ? '#212121' : undefined,
                          }"
                        >
                          {{ col }}
                        </v-chip>
                      </v-chip-group>
                    </v-col>
                    <v-col
                      align="left"
                      xs="12"
                      sm="12"
                      md="12"
                      lg="12"
                      xl="12"
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
                      align="center"
                    >
                      <v-tooltip
                        top
                      >
                        <template #activator="{ on, attrs }">
                          <v-btn
                            width="100%"
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
              class="my-2 py-2 px-1 mx-0"
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
      </v-card>
    </template>
  </DemoProjectTemplate>
</template>

<script>
import { saveAs } from 'file-saver'
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
    chartHeight () {
      const heights = {
        xs: 350,
        sm: 420,
        md: 420,
        lg: 450,
        xl: 500
      }
      return heights[this.$vuetify.breakpoint.name]
    },
    chartOptions () {
      return {
        colors: ['#212121', '#303F9F', '#E53935', '#E53935'],
        chart: {
          type: 'line',
          stacked: false,
          height: this.chartHeight,
          zoom: {
            type: 'x',
            enabled: true,
            autoScaleYaxis: true
          },
          toolbar: {
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
          align: this.$vuetify.breakpoint.xs ? 'left' : 'center'
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
    getSampleFile (downloadOnly = false) {
      const formData = new FormData()
      formData.append('mode', 'sampleFile')
      this.loadingSampleFile = true
      return this.$api.post('/forecaster', formData)
        .then(resp => {
          const data = resp.data.data
          const file = this.b64ExcelToFile(data.excel, 'sample-data.xlsx')
          if (downloadOnly) {
            saveAs(file, 'sample-data.xlsx')
          } else {
            this.file = file
          }
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
  .v-tooltip__content {
    pointer-events: initial;
  }
</style>
