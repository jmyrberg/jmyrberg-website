<template>
  <DemoProjectTemplate header="Document Context Similarity">
    <template #description>
      <p>
        Recent years have shown tremendous progress in Natural Language Processing (NLP). <a
          href="https://ai.googleblog.com/2018/11/open-sourcing-bert-state-of-art-pre.html"
          target="_blank"
        >Google's BERT</a> is a neural network based NLP model, for which <a
          href="https://turkunlp.org/"
          target="_blank"
        >Turku NLP group</a> has trained a Finnish version called <a
          href="https://github.com/TurkuNLP/FinBERT"
          target="_blank"
        >FinBERT</a>.
      </p>
      <p>
        The model can be fine-tuned to achieve state-of-the-art results in various Finnish natural language processing tasks, such as:
        <ul>
          <li>Question answering</li>
          <li>Document classification</li>
          <li>Sentiment analysis</li>
          <li>Sentence relations (demonstrated below)</li>
        </ul>
      </p>
      <p class="mb-6">
        How likely two Finnish documents are to occur in the same context? Fill in your own sentences or use the random fill to find out!
      </p>
    </template>
    <template #content>
      <v-form
        ref="form"
        v-model="valid"
        lazy-validation
      >
        <v-textarea
          v-model="doc1"
          class="mt-0"
          color="primary"
          :rules="docRules"
          label="First document"
          :rows="$vuetify.breakpoint.mdAndUp ? 6 : 4"
          required
          outlined
        />
        <v-textarea
          v-model="doc2"
          color="primary"
          :rules="docRules"
          label="Second document"
          :rows="$vuetify.breakpoint.mdAndUp ? 6 : 4"
          required
          outlined
        />
        <v-progress-linear
          :value="probability === null ? 0 : probability"
          :color="color"
          :reactive="false"
          :indeterminate="loading"
          rounded
          height="25"
        >
          <span
            v-if="probability !== null"
            class="font-weight-light"
          >
            <strong>{{ interpretation }}</strong> to appear in the same context
          </span>
          <span v-else-if="loading">
            Analyzing, may take a while for the first time...
          </span>
          <span
            v-else
            style="color: grey;"
          >
            Results will appear here
          </span>
        </v-progress-linear>
        <v-row class="mx-auto my-0 py-0">
          <v-btn
            class="mt-6"
            outlined
            :loading="loading"
            :disabled="!valid"
            @click="predict"
          >
            Predict
          </v-btn>
          <v-spacer />
          <v-btn
            class="mt-6"
            text
            :disabled="loading"
            @click="randomArticle"
          >
            <v-icon left>
              mdi-text
            </v-icon>
            Random fill
          </v-btn>
        </v-row>
      </v-form>
    </template>
  </DemoProjectTemplate>
</template>

<script>
import { mapActions } from 'vuex'
import DemoProjectTemplate from '@/components/DemoProjects/DemoProjectTemplate'
export default {
  name: 'DocContextSimilarity',
  components: {
    DemoProjectTemplate
  },
  data: () => ({
    valid: true,
    doc1: '',
    doc2: '',
    docRules: [
      v => !!v || 'Document must contain at least one character'
    ],
    loading: false,
    probability: null,
    randomArticles: [
      'Jenni Mari Vartiainen on suomalainen laulaja ja lauluntekijä. Hän tuli tunnetuksi Popstars-televisio-ohjelmassa vuonna 2002 perustetun Gimmel-yhtyeen jäsenenä.',
      'Idols on suomalaisversio brittiläisestä FremantleMedian tuottamasta Pop Idol -televisio-ohjelmaformaatista, jossa etsitään uusia laulajakykyjä.',
      'Sanna Mirella Marin on suomalainen poliitikko, joka on toiminut Suomen pääministerinä 10. joulukuuta 2019 lähtien. Marin on sosiaalidemokraattien ensimmäinen varapuheenjohtaja.',
      'Juha Petri Sipilä on suomalainen poliitikko, liikemies ja yritysjohtaja, joka toimi Suomen pääministerinä vuosina 2015–2019. Sipilä on teknologiayritysten pääomarahoitukseen keskittyneen Fortel Invest Oy:n perustaja, ja hän on ollut noin 40 yrityksen johtotehtävissä.',
      'Nokia Oyj on suomalainen maailmanlaajuisesti toimiva tietoliikennealan yhtiö, jonka pääliiketoimintoja ovat verkkoinfrastruktuuri, sekä teknologiakehitys ja lisensointi.',
      'Pirkka-Pekka Petelius on suomalainen viihdetaiteilija ja poliitikko.'
    ]
  }),
  computed: {
    color () {
      if (this.probability === null) {
        return 'grey lighten-1'
      } else if (this.probability < 50) {
        return 'error'
      } else if (this.probability < 50) {
        return 'warning'
      } else if (this.probability < 75) {
        return 'green lighten-1'
      } else {
        return 'success'
      }
    },
    interpretation () {
      if (this.probability < 25) {
        return 'Very unlikely'
      } else if (this.probability < 50) {
        return 'Unlikely'
      } else if (this.probability < 75) {
        return 'Likely'
      } else {
        return 'Very likely'
      }
    }
  },
  methods: {
    predict () {
      if (this.$refs.form.validate()) {
        this.loading = true
        this.probability = null
        this.$api.post('/doc_context_similarity', {
          data: {
            doc1: this.doc1,
            doc2: this.doc2
          }
        }).then(resp => {
          this.probability = resp.data.data.probability * 100
          this.loading = false
        }).catch(err => {
          console.log(err)
          this.loading = false
          this.showMessage({
            message: err.response && err.response.data ? err.response.data.message : 'Something went wrong :(',
            color: 'error',
            delay: -1
          })
        })
      }
    },
    randomArticle () {
      const idx1 = Math.floor(Math.random() * this.randomArticles.length)
      let idx2 = idx1
      while (idx2 === idx1) {
        idx2 = Math.floor(Math.random() * this.randomArticles.length)
      }
      this.doc1 = this.randomArticles[idx1]
      this.doc2 = this.randomArticles[idx2]
      this.probability = null
    },
    ...mapActions(['showMessage'])
  }
}
</script>
