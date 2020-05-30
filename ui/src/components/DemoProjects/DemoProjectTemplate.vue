<template>
  <v-row align="center" justify="center">
    <v-col cols="12">
      <div class="mb-2 text-center align-center">
        <span class="headline text-uppercase font-weight-light">
          {{ header }}
        </span>
      </div>
      <v-row align="center" justify="center" class="my-3 pb-1">
        <v-divider style="border-width: 2px; border-color: black; max-width: 30px;"></v-divider>
        <div style="position: absolute;">
          <v-icon
            color="black"
            size="36"
            :class="`${showDescription ? 'mb-2' : 'mt-2'}`"
            :style="`${showDescription ? 'transform: rotate(0deg);' : 'transform: rotate(180deg);'}`"
            @click="showDescription = !showDescription"
          >
            mdi-chevron-up
          </v-icon>
        </div>
        <span
          class="overline align-center"
          :style="{
            'position': 'absolute',
            'margin-top': showDescription ? '10px' : '-10px'
          }"
        >
          <a @click="showDescription = !showDescription">{{ showDescription ? 'Close' : '' }}</a>
        </span>
      </v-row>
    </v-col>
    <v-expand-transition duration="800">
      <div v-if="showDescription">
        <v-col cols="12" class="pt-0 mt-0 mb-0 pb-1">
          <slot name="description"></slot>
        </v-col>
      </div>
    </v-expand-transition>
    <v-divider></v-divider>
    <v-col cols="12">
      <slot name="content"></slot>
    </v-col>
  </v-row>
</template>

<script>
export default {
  name: 'demo-project-template',
  props: {
    header: { default: '', type: String }
  },
  data: () => ({
    showDescription: true
  }),
  computed: {
  },
  methods: {
  },
  mounted () {
  }
}
</script>
