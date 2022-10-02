<template>
  <v-app>
    <Toolbar></Toolbar>
    <v-main>
      <v-container
        fluid
        id="main-container"
        class="overflow-y-auto"
      >
        <transition name="fade" mode="out-in">
          <router-view></router-view>
        </transition>
      </v-container>
    </v-main>
    <v-divider class="mt-4 mb-2 mx-3"></v-divider>
    <Footer></Footer>
    <v-snackbar
      bottom
      :color="getSnackbarColor"
      :timeout="-1"
      v-model="snackbar"
      inset
    >
      <div class="text-center">{{ getMessage }}</div>
      <template v-slot:action="{ attrs }">
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
  methods: {
    ...mapActions(['closeMessage'])
  },
  mounted () {
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
