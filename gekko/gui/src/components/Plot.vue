<template>
  <div>
    <h2>Plot Component</h2>
    <div id="plot-div"></div>
    <button type="button" name="button" @click="show_plot">Show Plot</button>
  </div>
</template>

<script>
import Plotly from 'plotly.js'

export default {
  name: 'Plot',
  methods: {
  },
  mounted () {
    console.log('Before plot')
    Plotly.newPlot('plot-div', [{
      x: [1, 2, 3, 4],
      y: [56, 34, 87, 12]
    }])
    console.log('After plot')
  }
}
</script>

<style lang="css">
</style>
