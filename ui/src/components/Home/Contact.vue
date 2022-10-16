<template>
  <v-container
    id="contact-container"
    fluid
  >
    <v-row
      align="center"
      justify="center"
    >
      <v-col cols="12">
        <div class="mb-2 text-center">
          <span class="headline text-uppercase font-weight-light">Contact</span>
        </div>
        <v-row
          align="center"
          justify="center"
          class="my-3 pb-1"
        >
          <v-divider style="border-width: 2px; border-color: black; max-width: 30px;" />
        </v-row>
        <p class="text-center font-weight-light mx-auto px-2 pt-1">
          Questions, comments, project ideas? Let's be in touch!
        </p>
      </v-col>
      <v-col
        cols="12"
        xs="12"
      >
        <v-form
          ref="form"
          v-model="valid"
          lazy-validation
        >
          <v-text-field
            v-model="name"
            color="primary"
            :rules="nameRules"
            label="Name"
            required
            outlined
          />
          <v-text-field
            v-model="email"
            color="primary"
            :rules="emailRules"
            label="E-mail address"
            required
            outlined
          />
          <v-textarea
            v-model="message"
            color="primary"
            :rules="messageRules"
            label="Message"
            required
            outlined
          />
          <v-slide-y-transition>
            <vue-recaptcha
              v-show="showReCaptcha"
              class="pb-2 mb-4"
              theme="dark"
              :sitekey="reCaptchaSiteKey"
              @verify="onReCaptchaVerify"
            />
          </v-slide-y-transition>
          <div v-if="!submitError && !submitSuccess">
            <v-btn
              :loading="submitting"
              :disabled="(!valid || !!!reCaptchaResponse)"
              outlined
              color="primary"
              @click="submit"
            >
              Submit
            </v-btn>
          </div>
          <div v-else-if="submitSuccess">
            <v-icon
              color="success"
              class="mr-1"
            >
              mdi-check
            </v-icon>
            <span class="font-weight-light">Thank you for contacting, I'll come back to you as soon as possible!</span>
          </div>
          <div v-else-if="submitError">
            <v-icon
              color="error"
              class="mr-1"
            >
              mdi-alert-circle
            </v-icon>
            <span class="font-weight-light">Unfortunately something went wrong - please contact me through <a
              href="https://www.linkedin.com/in/jesse-myrberg/"
              target="_blank"
            >LinkedIn</a> or <a href="mailto:jesse.myrberg@gmail.com">email</a></span>
          </div>
        </v-form>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { VueRecaptcha } from 'vue-recaptcha'
export default {
  name: 'Contact',
  components: { VueRecaptcha },
  data: () => ({
    valid: false,
    name: '',
    nameRules: [
      v => !!v || 'Please fill in your name'
    ],
    email: '',
    emailRules: [
      v => !!v || 'Please fill in a valid E-mail address',
      v => /.+@.+\..+/.test(v) || 'Please fill in a valid E-mail address'
    ],
    message: '',
    messageRules: [
      v => v.length > 0 || 'Please write a proper message'
    ],
    submitting: false,
    submitSuccess: false,
    submitError: false,
    reCaptchaSiteKey: process.env.VUE_APP_RECAPTCHA_SITE_KEY,
    reCaptchaResponse: ''
  }),
  computed: {
    showReCaptcha () {
      const formValid = (!!this.name && !!this.message && !!this.email)
      const reCaptchaResponseExists = !!this.reCaptchaResponse
      const submitNotDone = !this.submitSuccess
      return submitNotDone && (reCaptchaResponseExists || formValid)
    }
  },
  methods: {
    onReCaptchaVerify (verify) {
      this.reCaptchaResponse = verify
    },
    submit () {
      if (this.$refs.form.validate()) {
        this.submitting = true
        this.$api.post('/contact', {
          data: {
            name: this.name,
            email: this.email,
            message: this.message,
            reCaptchaResponse: this.reCaptchaResponse
          }
        }).then(resp => {
          this.submitSuccess = true
        }).catch(err => {
          console.log(err)
          this.submitError = true
        })
      }
    }
  }
}
</script>
