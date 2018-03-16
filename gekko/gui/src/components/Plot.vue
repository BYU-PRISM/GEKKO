<template>
  <div class="plot-div">
    <button
      v-if="numPlots > 1"
      type="button"
      class="btn btn-sm btn-danger plot-close"
      @click="removePlot">X</button>
    <div :id="id"/>
  </div>
</template>

<script>
import Plotly from 'plotly.js/dist/plotly.min'

// Resizes the plots whenever the size of the window changes
window.onresize = () => {
  this.plotlyResize // eslint-disable-line
}

export default {
  name: 'Plot',
  props: {
    externalId: {
      type: Number,
      default: 1
    },
    numPlots: {
      type: Number,
      default: 1
    }
  },
  data () {
    return {
      id: Math.random().toString(36).substring(7)
    }
  },
  watch: {
    numPlots: () => {
      console.log('numPlots changed, resizing plot')
      this.plotlyResize // eslint-disable-line
    }
  },
  beforeDestroy: function () {
    window.removeEventListener('resize', this.plotlyResize)
  },
  mounted () {
    window.addEventListener('resize', this.plotlyResize)
    this.$http.headers.common['Access-Control-Allow-Origin'] = '*'
    this.$http.get('get_data')
      .then(response => response.json())
      .then(data => {
        var plotArray = []
        console.log(data)
        const isMuchData = Object.keys(data).length > 5
        for (var key in data) {
          if (data.hasOwnProperty(key)) {
            if (key !== 'time') {
              const trace = {
                x: data.time,
                y: data[key],
                mode: 'lines',
                type: 'scatter',
                name: key,
                visible: isMuchData ? 'legendonly' : 'true'
              }
              plotArray.push(trace)
            }
          }
        }
        Plotly.newPlot(this.id, plotArray)
      })
  },
  methods: {
    plotlyResize () {
      console.log('handling resize for:', this.id)
      Plotly.Plots.resize(this.id)
    },
    removePlot () {
      this.$emit('plot-removed', this.externalId)
    }
  }

}
</script>

<style lang="css">
.plot-div {
  position: relative;
}
.plot-close {
  position: absolute;
  z-index: 1;
}
</style>
