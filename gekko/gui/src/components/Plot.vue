<template>
  <div>
    <button v-if="!onlyPlot" type="button" class="btn btn-danger" @click="removePlot">X</button>
    <div :id="id"></div>
  </div>
</template>

<script>
import Plotly from 'plotly.js/dist/plotly.min'

// Resizes the plots whenever the size of the window changes
window.onresize = () => {
}

export default {
  name: 'Plot',
  props: ['externalId', 'onlyPlot'],
  data () {
    return {
      id: Math.random().toString(36).substring(7)
    }
  },
  beforeDestroy: function () {
    window.removeEventListener('resize', this.plotlyResize)
  },
  methods: {
    plotlyResize () {
      console.log('handling resize for:', this.id)
      Plotly.Plots.resize(this.id)
    },
    removePlot () {
      this.$emit('plot-removed', this.externalId)
    }
  },
  mounted () {
    window.addEventListener('resize', this.plotlyResize)
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
        Plotly.newPlot(this.id, plotArray)
      })
  }
}
</script>

<style lang="css">
.error{
    color: red;
}
</style>
