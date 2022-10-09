<template>
  <DemoProjectTemplate header="Forecaster">
    <template #description>
      <p>
        TODO:
        <br>
        * Take frequency as input
        <br>
        * Visualization (d3.js?)
        <br>
        * Explanation here
      </p>
    </template>
    <template #content>
      <v-container
        fluid
        class="mt-2 pt-2"
      >
        <v-stepper
          v-model="step"
          flat
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

          <v-stepper-content step="1">
            <v-row
              class="my-0 py-0"
              justify="center"
            >
              <v-col
                class="my-0 py-0"
                xs="12"
                sm="6"
              >
                <v-file-input
                  v-model="file"
                  prepend-icon=""
                  :loading="loadingPrepare"
                  accept=".csv,.xls,.xlsx"
                  label="Select Excel or CSV file..."
                  @change="getPrepare"
                >
                  <template v-slot:prepend-inner>
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
              class="my-0 py-0"
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
                  :disabled="loadingPrepare"
                  @click="useSampleFile"
                >
                  Use a sample file (<a href="" target="_blank">download</a>)
                </v-btn>
              </v-col>
            </v-row>
          </v-stepper-content>

          <v-stepper-content step="2">
            <span class="subheading">Date column: {{ selectedDateColValue }}</span>
            <v-chip-group
              v-model="selectedDateColValue"
              active-class="primary--text"
              mandatory
            >
              <v-chip
                v-for="(col, i) in dateColOptions"
                :key="i"
                :value="col"
                outlined
              >
                {{ col }}
              </v-chip>
            </v-chip-group>
            <span class="subheading">Date frequency: {{ selectedDateCol.freq }}</span>
            <v-chip-group
              v-model="selectedDateCol.freq"
              active-class="primary--text"
              mandatory
            >
              <v-chip
                v-for="(freq, i) in freqOptions"
                :key="i"
                :value="freq.value"
                outlined
              >
                {{ freq.text }}
              </v-chip>
            </v-chip-group>

            <span class="subheading">Forecast column: {{ selectedForecastColValue }}</span>
            <v-chip-group
              v-model="selectedForecastColValue"
              active-class="primary--text"
              mandatory
            >
              <v-chip
                v-for="(col, i) in forecastColOptions"
                :key="i"
                :value="col"
                outlined
              >
                {{ col }}
              </v-chip>
            </v-chip-group>
            <v-slider
              v-model="horizon"
              :disabled="!readyToForecast"
              label="Horizon"
              min="1"
              max="48"
              :thumb-size="24"
              thumb-label="always"
            />
            <v-btn
              :disabled="!readyToForecast"
              :loading="loadingForecast"
              @click="getForecast"
            >
              Forecast
            </v-btn>
          </v-stepper-content>

          <v-stepper-content step="3">
            <div id="chart">
              <ApexChart
                type="area"
                height="350"
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
    horizon: 6,
    freqOptions: [
      { text: 'Hourly', value: 'H' },
      { text: 'Daily', value: 'D' },
      { text: 'Weekly', value: 'W' },
      { text: 'Monthly', value: 'M' },
      { text: 'Quarterly', value: 'Q' },
      { text: 'Annual', value: 'A' }
    ],
    rankDateCol: { value: '(auto)', dtype: 'datetime', dtypeName: 'date', freq: 'D' },
    columns: [],
    forecast: { series: [], dates: [], xAxisType: 'datetime' },
    loadingPrepare: false,
    loadingForecast: false
  }),
  computed: {
    selectedDateCol () {
      return this.selectedDateColValue ? [this.rankDateCol].concat(this.columns)
        .find(x => x.value === this.selectedDateColValue) : { freq: null }
    },
    selectedForecastCol () {
      return this.columns
        .find(x => x.value === this.selectedForecastColValue)
    },
    forecastColOptions () {
      return this.columns
        .filter(x => ['integer', 'float'].includes(x.dtypeName))
        .map(x => x.value)
    },
    dateColOptions () {
      return [this.rankDateCol].concat(this.columns)
        .filter(x => ['date'].includes(x.dtypeName))
        .map(x => x.value)
    },
    readyToForecast () {
      return this.file && this.columns.length > 0 && this.selectedDateColValue && this.selectedForecastColValue && this.dateColOptions.includes(this.selectedDateColValue) && this.forecastColOptions.includes(this.selectedForecastColValue)
    },
    chartOptions () {
      return {
        chart: {
          type: 'line',
          stacked: false,
          height: 350,
          zoom: {
            type: 'x',
            enabled: true,
            autoScaleYaxis: true
          },
          toolbar: {
            autoSelected: 'selection',
            tools: {
              pan: false
            },
            export: {
              csv: {
                filename: 'jmyrberg-forecaster-' + this.selectedForecastColValue
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
    forecastColOptions (newOpts, oldOpts) {
      // No options --> unselect
      if (newOpts === null || newOpts === undefined || newOpts.length === 0) {
        this.selectedForecastColValue = null
      // Selection not in new options --> select first
      } else if (!newOpts.includes(this.selectedForecastColValue)) {
        this.selectedForecastColValue = newOpts[0]
      }
    },
    dateColOptions (newOpts, oldOpts) {
      // No options --> unselect
      if (newOpts === null || newOpts === undefined || newOpts.length === 0) {
        this.selectedDateColValue = null
      // Selection not in new options --> select first
      } else if (!newOpts.includes(this.selectedDateColValue)) {
        this.selectedDateColValue = newOpts[0]
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
    useSampleFile () {
      // TODO: Fill selection with a sample
      // this.file = 
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
      } else {
        console.log('Wrong number of files')
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
    ...mapActions(['showMessage'])
  }
}
</script>

<style scoped>
  .v-stepper__header {
    box-shadow: none;
  }
</style>
