<template>
  <v-container id="about-container" fluid>
    <v-row align="center" justify="center" class="mx-auto px-auto">
      <v-col cols="12">
        <div class="mb-2 text-center align-center">
          <span class="headline text-uppercase font-weight-light">About</span>
        </div>
        <v-row align="center" justify="center" class="my-3 pb-1">
          <v-divider style="border-width: 2px; border-color: black; max-width: 30px;"></v-divider>
        </v-row>
      </v-col>
      <v-col cols="12" xs="12" sm="6">
        <v-row align="center" justify="center" class="mx-auto">
          <v-spacer v-if="$vuetify.breakpoint.smAndUp"></v-spacer>
          <v-hover
            v-slot:default="{ hover }"
          >
            <v-avatar
              size="80%"
              :tile="!hover"
            >
              <v-img
                :src="require('@/assets/jesse-myrberg.jpg')"
                style="filter: grayscale(100%); border-radius: 4px;"
                max-height="500"
              ></v-img>
            </v-avatar>
          </v-hover>
        </v-row>
      </v-col>
      <v-col cols="12" xs="12" sm="6">
        <v-row class="ma-0 pa-0" :justify="$vuetify.breakpoint.smAndUp ? 'left' : 'center'" align="center">
          <p class="my-2" v-bind:class="{ 'text-center': !$vuetify.breakpoint.smAndUp }">
            I am a business problem solver with more than 5 years of experience in building advanced analytics solutions for various domains. My key competences include <strong>mathematical optimization</strong> and <strong>machine learning</strong>, but I am eager to take challenges all the way from backend APIs to end-user interfaces and trainings.
          </p>
        </v-row>
        <v-row :justify="$vuetify.breakpoint.smAndUp ? 'left' : 'center'" align="center">
          <div :class="`ml-${$vuetify.breakpoint.smAndUp ? 'n8' : '0'}`">
            <v-img
              :src="require('@/assets/signature.png')"
              max-height="60"
              contain
            ></v-img>
          </div>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'about',
  data: () => ({
  })
}
</script>

<style>
</style>
