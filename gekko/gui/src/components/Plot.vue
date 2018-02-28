<template>
  <div>
    <div id="plot-div"></div>
  </div>
</template>

<script>
import Plotly from 'plotly.js/dist/plotly.min'

// Resizes the plots whenever the size of the window changes
window.onresize = () => {
  Plotly.Plots.resize('plot-div')
}

export default {
  name: 'Plot',
  data () {
    return {
      error: ''
    }
  },

  methods: {
  },

  created () {
    this.$http.headers.common['Access-Control-Allow-Origin'] = '*'
    this.$http.get('get_data')
      .then(response => response.json())
      .then(data => {
        var plotArray = []
        for (var key in data) {
          if (data.hasOwnProperty(key)) {
            if (key !== 'time') {
              plotArray.push({
                x: data.time,
                y: data[key],
                mode: 'lines+markers',
                type: 'scatter',
                name: key
              })
            }
          }
        }
        Plotly.newPlot('plot-div', plotArray)
      })
  },
  mounted () {
    Plotly.newPlot('plot-div', [{}])
  }
}
</script>

<style lang="css">
.error{
    color: red;
}
</style>
