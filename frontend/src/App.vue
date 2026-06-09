<template>
  <div id="app-root">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
onMounted(() => {
  auth.init()
})
</script>

<style>
#app-root { min-height: 100vh; background: #fff; }
</style>