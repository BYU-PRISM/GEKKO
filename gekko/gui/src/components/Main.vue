<template>
  <div class="mainDiv">
    <modalPlot
      v-if="$store.state.fullscreenPlot"
      @close="hideModalPlot"/>
    <div
      class="row"
      style="margin-right:0px;">
      <div class="col-sm-3">
        <tabs/>
      </div>
      <div class="col-sm-9">
        <div class="plots-div">
          <div
            v-for="value in plotArray"
            :key="value">
            <plot
              :external-id="value"
              @plot-removed="removePlot"
              :num-plots="plotArray.length"/>
          </div>
        </div>
        <button
          type="button"
          class="btn btn-primary"
          @click="addPlot"
          style="margin-top:10px;">Add Plot</button>
        <button
          type="button"
          class="btn btn-secondary"
          @click="showModalPlot"
          style="margin-top:10px;">Fullscreen plot</button>
        <button
          type="button"
          class="btn btn-secondary"
          @click="$store.dispatch('updatePlotDataAsync')"
          style="margin-top:10px;">Test data fetch</button>
      </div>
    </div>
  </div>
</template>

<script>
import Plot from './Plot'
import Tabs from './Tabs'
import ModalPlot from './ModalPlot'

export default {
  name: 'Main',
  components: {'plot': Plot, 'tabs': Tabs, 'modalPlot': ModalPlot},
  data () {
    return {
    }
  },
  computed: {
    plotArray () {
      return this.$store.state.plots
    }
  },
  methods: {
    addPlot () { this.$store.commit('addPlot') },
    removePlot (id) {
      console.log('Removing plot', id)
      this.plotArray = this.plotArray.filter(val => val !== id)
    },
    hideModalPlot () { this.$store.commit('hideFullscreenPlot') },
    showModalPlot () { this.$store.commit('showFullscreenPlot') }
  }
}
</script>

<style>
.plots-div {
  max-height: 93vh;
  overflow-y: auto;
  border: 1px blue;
  border-style: solid;
  padding-right: 15px;
  border-radius: 10px;
}
</style>
