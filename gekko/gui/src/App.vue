<template>
  <div id="app">
    <h1>GEKKO Optimization Results</h1>
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin-left: 10px;
  margin-top: 10px;
  margin-bottom: 10px;
  max-width: 98vw;
}
</style>
