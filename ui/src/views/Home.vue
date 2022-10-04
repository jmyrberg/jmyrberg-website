<template>
  <div>
    <About />
    <v-divider class="mt-6 mb-5 mx-auto" />
    <DemoProjectList />
    <v-divider class="mt-8 mb-3 mx-auto" />
    <Contact />
  </div>
</template>

<script>
import About from '@/components/Home/About.vue'
import Contact from '@/components/Home/Contact.vue'
import DemoProjectList from '@/components/Home/DemoProjectList.vue'
export default {
  name: 'Home',
  components: {
    About,
    Contact,
    DemoProjectList
  },
  data () {
    return {}
  }
}
</script>
