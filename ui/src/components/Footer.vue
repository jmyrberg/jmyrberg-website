<template>
  <v-container fluid>
    <v-row align="center" justify="center" class="mt-0">
      <div class="text-xs-center">
        <v-hover
          v-slot:default="{ hover }"
        >
          <v-btn
            icon
            href="https://github.com/jmyrberg"
            target="_blank"
            x-large
            :elevation="hover ? 4 : 0"
          >
            <v-icon>mdi-github</v-icon>
          </v-btn>
        </v-hover>
        <v-hover
          v-slot:default="{ hover }"
        >
          <v-btn
            icon
            href="https://www.linkedin.com/in/jesse-myrberg/"
            target="_blank"
            x-large
            :elevation="hover ? 4 : 0"
          >
            <v-icon>mdi-linkedin</v-icon>
          </v-btn>
        </v-hover>
      </div>
    </v-row>
    <v-row align="center" justify="center" class="mt-3 mb-3">
      <div class="font-weight-light">
        &copy; 2020 Jesse Myrberg
      </div>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'toolbar',
  data: () => ({
    style: {
      toolbarHeight: { xs: 210, sm: 240, md: 240, lg: 240, xl: 240 },
      profileTextSize: { xs: '.6em', sm: '.75em', md: '1em', lg: '1em', xl: '1.25em' }
    }
  }),
  methods: {
    goToLink (target) {
      if (this.$route.name !== 'home') {
        this.$router.push({ name: 'home' }).then(() => {
          this.$vuetify.goTo(`#${target}-container`, {})
        })
      } else {
        this.$vuetify.goTo(`#${target}-container`, {})
      }
    }
  }
}
</script>

<style lang="scss">
  @import '~vuetify/src/styles/styles.sass';

  @media #{map-get($display-breakpoints, 'xs-only')} {
  }
</style>
