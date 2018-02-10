<template>
  <div>
    <h2>Plot Component</h2>
    <div id="plot-div"></div>
    <button type="button" name="button" @click="update_error">Show Plot</button>
    <p class="error">{{ error }}</p>
  </div>
</template>

<script>
import Plotly from 'plotly.js'

export default {
  name: 'Plot',
  data () {
    return {
      error: ''
    }
  },
  methods: {
    update_error () {
      this.error = 'No Errors!'
    }
  },
  mounted () {
    Plotly.newPlot('plot-div', [{
      x: [1, 2, 3, 4],
      y: [56, 34, 87, 12]
    }])
  }
}
</script>

<style lang="css">
.error{
    color: red;
}
</style>
