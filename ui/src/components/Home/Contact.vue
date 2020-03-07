<template>
  <v-container id="contact-container" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12">
        <div class="mb-2 text-center">
          <span class="headline text-uppercase font-weight-light">Contact</span>
        </div>
        <v-row align="center" justify="center" class="my-3 pb-1">
          <v-divider style="border-width: 2px; border-color: black; max-width: 30px;"></v-divider>
        </v-row>
        <p class="text-center font-weight-light mx-auto px-2 pt-1">
          Questions, comments, project ideas? Let's be in touch!
        </p>
      </v-col>
      <v-col cols="12" xs="12">
        <v-form
          ref="form"
          v-model="valid"
          lazy-validation
        >
            <v-text-field
              color="primary"
              v-model="name"
              :rules="nameRules"
              label="Name"
              required
              outlined
            ></v-text-field>
            <v-text-field
              color="primary"
              v-model="email"
              :rules="emailRules"
              label="E-mail address"
              required
              outlined
            ></v-text-field>
            <v-textarea
              color="primary"
              v-model="message"
              outlined
              label="Message"
              required
            ></v-textarea>
            <div v-if="!submitError && !submitSuccess">
              <v-btn
                :loading="submitting"
                :disabled="!valid"
                outlined
                color="primary"
                @click="submit"
              >
                Submit
              </v-btn>
            </div>
            <div v-else-if="submitSuccess">
              <v-icon color="success" class="mr-1">mdi-check</v-icon>
              <span class="font-weight-light">Thank you for contacting, I'll come back to you as soon as possible!</span>
            </div>
            <div v-else-if="submitError">
              <v-icon color="error" class="mr-1">mdi-alert-circle</v-icon>
              <span class="font-weight-light">Unfortunately something went wrong - please contact me through <a href="https://www.linkedin.com/in/jesse-myrberg/" target="_blank">LinkedIn</a> or <a href="mailto:jesse.myrberg@gmail.com">email</a></span>
            </div>
        </v-form>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'contact',
  data: () => ({
    valid: true,
    name: '',
    nameRules: [
      v => !!v || 'Please fill in your name'
    ],
    email: '',
    emailRules: [
      v => !!v || 'Please fill in your E-mail address',
      v => /.+@.+\..+/.test(v) || 'Please fill in a valid E-mail address'
    ],
    message: '',
    submitting: false,
    submitSuccess: false,
    submitError: false
  }),
  methods: {
    submit () {
      if (this.$refs.form.validate()) {
        this.submitting = true
        this.$api.post('/contact', {
          data: {
            name: this.name,
            email: this.email,
            message: this.message
          }
        }).then(resp => {
          this.submitSuccess = true
          this.submitted = true
        }).catch(err => {
          console.log(err)
          this.submitError = true
        })
      }
    }
  }
}
</script>
