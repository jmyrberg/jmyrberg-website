<template>
  <div>
    <About></About>
    <v-divider class="mt-3 mb-5 mx-auto"></v-divider>
    <DemoProjectList></DemoProjectList>
    <v-divider class="mt-8 mb-3 mx-auto"></v-divider>
    <Contact></Contact>
  </div>
</template>

<script>
import About from '@/components/Home/About.vue'
import Contact from '@/components/Home/Contact.vue'
import DemoProjectList from '@/components/Home/DemoProjectList.vue'
export default {
  name: 'home',
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
