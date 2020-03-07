<template>
  <v-container id="demo-projects-container" fluid class="ma-0 pa-0">
    <v-row align="center" justify="center" class="mx-auto px-auto">
      <v-col cols="12">
        <div class="mb-2 text-center">
          <span class="headline text-uppercase font-weight-light">Demo projects</span>
        </div>
        <v-row align="center" justify="center" class="my-3 pb-1">
          <v-divider style="border-width: 2px; border-color: black; max-width: 30px;"></v-divider>
        </v-row>
        <p class="text-center font-weight-light mx-auto px-2 pt-1">
          Examples of my free-time projects.
        </p>
      </v-col>
      <v-col cols="12" class="ma-0 pa-0">
        <v-row>
          <v-col
            v-for="card in cards"
            :key="card.title"
            xs="12"
            sm="6"
          >
            <v-hover v-slot:default="{ hover }">
              <v-card
                class="d-flex flex-column"
                link
                :to="{ name: card.to }"
                :hover="hover"
                height="400px"
              >
                <v-img
                  :src="card.src"
                  class="white--text align-end"
                  gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.8)"
                  height="180"
                >
                  <v-card-title class="headline" v-text="card.title"></v-card-title>
                </v-img>
                <v-card-subtitle class="subtitle-2 mb-0 pb-1">{{ card.subtitle }}</v-card-subtitle>
                <v-card-text class="font-weight-light">{{ card.text }}</v-card-text>
                <v-spacer></v-spacer>
                <v-card-actions class="mb-2">
                  <div
                    v-for="(label, i) in card.labels"
                    :key="i"
                  >
                    <v-hover
                      v-slot:default="{ hover }"
                    >
                        <v-chip
                          class="mx-1"
                          small
                          :dark="hover"
                        >
                          {{ label }}
                        </v-chip>
                    </v-hover>
                  </div>
                </v-card-actions>
              </v-card>
            </v-hover>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'demo-projects',
  data () {
    return {
      cards: [
        {
          title: 'Document Context Similarity',
          subtitle: 'Natural Language Processing',
          text: 'The past few years have shown tremendous progress in Natural Language Processing. This tool lets you predict whether two Finnish documents are likely to appear in the same context.',
          labels: ['NLP', 'Finnish', 'BERT', 'Similarity'],
          to: 'doc-context-similarity',
          src: require('@/assets/doc-context-similarity.jpg')
        },
        {
          title: 'Food Recommender',
          subtitle: 'Apps',
          text: 'What\'s cooking? This app provides a shareable list of food items and suggests what to cook next. The more the user interacts with the list, the more relevant the recommendations become.',
          labels: ['App', 'Food', 'Recommender System'],
          to: 'food-recommender',
          src: require('@/assets/food-recommender.jpg')
        },
        {
          title: 'Maximum Flows',
          subtitle: 'Optimization',
          text: 'Demonstration of what optimization can be used for. This tool lets you create a network, and then find the path through the network which maximizes the flow from the source to destination node.',
          labels: ['Optimization', 'Network', 'Flows'],
          to: 'maximum-flows',
          src: require('@/assets/maximum-flows.jpg')
        }
      ]
    }
  }
}
</script>
