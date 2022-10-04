<template>
  <v-row
    align="center"
    justify="center"
  >
    <v-col
      cols="12"
      class="pt-2 mt-2 mb-0 pb-0"
    >
      <div class="text-center align-center">
        <span class="headline text-uppercase font-weight-light">
          {{ header }}
        </span>
      </div>
      <v-row
        align="center"
        justify="center"
        class="my-0 py-0"
      >
        <v-btn
          icon
          color="black"
          small
          :style="{
            'transform': showDescription ? 'rotate(0deg)' : 'rotate(180deg)',
            'z-index': 10
          }"
          @click="showDescription = !showDescription"
        >
          <v-icon>mdi-chevron-up</v-icon>
        </v-btn>
      </v-row>
    </v-col>
    <v-expand-transition duration="800">
      <div v-if="showDescription">
        <v-col
          cols="12"
          class="my-0 py-0"
        >
          <slot name="description" />
        </v-col>
      </div>
    </v-expand-transition>
    <v-col
      cols="12"
      class="mt-0 pt-0"
    >
      <slot name="content" />
    </v-col>
  </v-row>
</template>

<script>
export default {
  name: 'DemoProjectTemplate',
  props: {
    header: { default: '', type: String }
  },
  data: () => ({
    showDescription: true
  }),
  computed: {
  },
  mounted () {
  },
  methods: {
  }
}
</script>
