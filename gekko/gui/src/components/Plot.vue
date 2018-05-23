<template>
  <div class="plot-div">
    <button
      v-if="$store.state.plots.length > 2 && externalId != 0"
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
    // This is passed in and is used for looking up the other props from the global store
    externalId: {
      type: Number,
      required: true
    }
  },
  data () {
    return {
      // This id is simply for handling window updates and is soley internal state
      id: Math.random().toString(36).substring(7)
    }
  },
  computed: {
    updateNumber () {
      return this.$state.updateNumber
    },
    plotData () {
      if (this.$store.state.plots.length > 0) {
        return this.$store.state.plots.find(plot => plot.id === this.externalId).data
      } else {
        return false
      }
    },
    layout () { return this.$store.state.plots.find(plot => plot.id === this.externalId).layout }
  },
  watch: {
    numPlots () {
        this.plotlyResize // eslint-disable-line
    }
  },
  created () {
    this.$store.watch(
      (state) => { return state.plots },
      () => {
        Plotly.react(this.id, this.plotData, this.layout)
      },
      {deep: true}
    )
  },
  beforeDestroy () { window.removeEventListener('resize', this.plotlyResize) },
  mounted () {
    window.addEventListener('resize', this.plotlyResize)
    if (this.plotData) {
      Plotly.newPlot(this.id, this.plotData, this.layout)
    }
  },
  methods: {
    plotlyResize () { Plotly.Plots.resize(this.id) },
    removePlot () { this.$store.commit('removePlot', this.externalId) }
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
