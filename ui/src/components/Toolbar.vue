<template>
  <v-app-bar
    app
    fixed
    elevation="0"
    color="primary"
  >
    <v-container fluid>
      <v-row class="ma-n4 pa-0" justify="center" align="center">
        <v-col cols="12" id="toolbar-container" class="ma-0 pa-0">
          <div class="ma-0 pa-0" v-bind:class="`${$vuetify.breakpoint.smAndUp ? 'text-right' : 'text-center'}`">
            <v-spacer></v-spacer>
            <v-hover
              v-slot:default="{ hover }"
            >
              <v-btn
                class="px-2"
                color="secondary"
                :text="!hover"
                :outlined="hover || $route.name == 'home'"
                tile
                @click="goToLink('about')"
              >
                About
              </v-btn>
            </v-hover>
            <v-hover
              v-slot:default="{ hover }"
            >
              <v-btn
                class="px-3"
                color="secondary"
                :text="!hover"
                :outlined="hover"
                tile
                @click="goToLink('demo-projects')"
              >
                Demo projects
              </v-btn>
            </v-hover>
            <v-hover
              v-slot:default="{ hover }"
            >
              <v-btn
                class="px-2"
                color="secondary"
                :text="!hover"
                :outlined="hover"
                tile
                @click="goToLink('contact')"
              >
                Contact
              </v-btn>
            </v-hover>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </v-app-bar>
</template>

<script>
export default {
  name: 'toolbar',
  data: () => ({
  }),
  methods: {
    goToLink (target) {
      if (this.$route.name !== 'home') {
        this.$router.push({ name: 'home' }).then(() => {
          setTimeout(() => {
            this.$vuetify.goTo(`#${target}-container`, {})
          }, 500 + 250) // See App.vue css
        })
      } else {
        this.$vuetify.goTo(`#${target}-container`, {})
      }
    }
  }
}
</script>

<style>
  #toolbar-container {
    max-width: 1040px;
  }
</style>
