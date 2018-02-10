<template>
  <div>
    <h2>Plot Component</h2>
    <div class="plot-div"></div>
    <button type="button" name="button" @click="show_plot">Show Plot</button>
  </div>
</template>

<script>
import Plotly from 'plotly.js/dist/plotly'
// var Plotly = require('plotly.js/lib/core');
// Plotly.register([
//     require('plotly.js/lib/scatter'),
//     require('plotly.js/lib/scatter3d'),
// ])

var trace1 = {
  x: [1, 2, 3, 4],
  y: [10, 15, 13, 17],
  mode: 'markers',
  type: 'scatter'
}

var trace2 = {
  x: [2, 3, 4, 5],
  y: [16, 5, 11, 9],
  mode: 'lines',
  type: 'scatter'
}

var trace3 = {
  x: [1, 2, 3, 4],
  y: [12, 9, 15, 12],
  mode: 'lines+markers',
  type: 'scatter'
}

var layout = {
  title: 'My Chart'
}

var data = [trace1, trace2, trace3]

export default {
  name: 'Plot',
  methods: {
    show_plot () {
      console.log('Log testing...')
      Plotly.plot('plot-div', data, layout, {showLink: false})
    }
  }
}
</script>

<style lang="css">
</style>
