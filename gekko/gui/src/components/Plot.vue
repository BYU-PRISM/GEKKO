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
    },
    layout: {
      type: Object,
      default: () => {
        return {
          'height': 500
        }
      }
    }
  },
  data () {
    return {
      id: Math.random().toString(36).substring(7)
    }
  },
  computed: {
    plotData () {
      return this.$store.state.plotData
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
    console.log('plot layout', this.layout)
    Plotly.newPlot(this.id, this.plotData, this.layout)
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
