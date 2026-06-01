<template>
  <NavBar />
  <div class="page-container">
    <router-view />
  </div>
</template>

<script setup>
import NavBar from './components/NavBar.vue'
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #f5f6fa; font-family: 'Microsoft YaHei', sans-serif; }
.page-container { max-width: 1200px; margin: 0 auto; padding: 24px 16px; }
</style>