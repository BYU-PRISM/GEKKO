<template>
  <div class="mainDiv">
    <modalPlot
      :hidden="!$store.state.fullscreenPlot"
      @close="showModalPlot(false)"/>
    <div
      class="row"
      style="margin-right:0px;">
      <div class="col-sm-3">
        <tabs/>
      </div>
      <div class="col-sm-9">
        <div class="plots-div">
          <div
            v-for="plot in displayPlots"
            :key="plot.id">
            <plot :external-id="plot.id"/>
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
          @click="showModalPlot(true)"
          style="margin-top:10px;">Fullscreen plot</button>
      </div>
    </div>
    <div
      class="communication-status"
      :style="statusStyle">
      <p>Status: {{ $store.state.communicationError ? 'Error' : 'Good' }}</p>
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
    return { }
  },
  computed: {
    plotArray () {
      return this.$store.state.plots
    },
    displayPlots () {
      return this.plotArray.filter((plot) => plot.id !== 0)
    },
    statusStyle () {
      return {
        border: this.$store.state.communicationError ? 'red 2px' : 'green 2px',
        padding: '3px',
        borderTopLeftRadius: '2px',
        borderStyle: 'solid',
        color: this.$store.state.communicationError ? 'red' : 'green'
      }
    }
  },
  mounted () { },
  methods: {
    addPlot () { this.$store.commit('addPlot') },
    removePlot (id) {
      console.log('Removing plot', id)
      this.$store.commit('removePlot', id)
    },
    showModalPlot (data) { this.$store.commit('showFullscreenPlot', data) }
  }
}
</script>

<style>
.plots-div {
  max-height: 91vh;
  overflow-y: auto;
  border: 1px blue;
  border-style: solid;
  padding-right: 15px;
  border-radius: 10px;
}

.communication-status {
  position: absolute;
  bottom: 0px;
  right: 0px;
  height: 30px;
  width: 100px;
}
</style>
