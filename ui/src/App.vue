<template>
  <v-app>
    <Toolbar />
    <v-main>
      <v-container
        id="main-container"
        fluid
        class="overflow-y-auto"
      >
        <transition
          name="fade"
          mode="out-in"
        >
          <router-view />
        </transition>
      </v-container>
    </v-main>
    <v-divider class="mt-4 mb-2 mx-3" />
    <Footer />
    <v-snackbar
      v-model="snackbar"
      bottom
      :color="getSnackbarColor"
      :timeout="-1"
      inset
    >
      <div class="text-center">
        {{ getMessage }}
      </div>
      <template #action="{ attrs }">
        <v-btn
          v-bind="attrs"
          color="white"
          text
          @click="snackbar = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import Footer from '@/components/Footer'
import Toolbar from '@/components/Toolbar'
export default {
  name: 'App',
  metaInfo () {
    return {
      title: 'Jesse Myrberg',
      titleTemplate: '%s | Jesse Myrberg',
      htmlAttrs: {
        lang: 'en-US'
      },
      link: [{ rel: 'canonical', href: `${process.env.VUE_APP_PUBLIC_URL}${this.$route.path}` }],
      meta: [
        { charset: 'utf-8' },
        { vmid: 'description', name: 'description', content: 'Jesse Myrberg\'s personal website with analytics demo projects and contact information' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' }
      ]
    }
  },
  components: {
    Toolbar,
    Footer
  },
  data: () => ({
  }),
  computed: {
    snackbar: {
      get () {
        return this.getSnackbar
      },
      set (value) {
        if (!value) {
          this.closeMessage()
        }
      }
    },
    ...mapGetters(['getMessage', 'getSnackbarColor', 'getSnackbar'])
  },
  mounted () {
  },
  methods: {
    ...mapActions(['closeMessage'])
  }
}
</script>

<style scoped>
#main-container {
  max-width: 1040px;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity .25s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>
