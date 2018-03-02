<template>
  <div class="mainDiv">
    <div class="row">
      <div class="col-sm-3">
        <tabs/>
      </div>
      <div class="col-sm-9">
        <div class="plots-div">
          <div v-for="value in plotArray" :key="value">
            <plot :externalId="value" v-on:plot-removed="removePlot"/>
          </div>
        </div>
        <button type="button" class="btn btn-primary" @click="addPlot" style="margin-top:10px;">Add Plot</button>
      </div>
    </div>
  </div>
</template>

<script>
import Plot from './Plot'
import Tabs from './Tabs'

export default {
  name: 'Main',
  components: {'plot': Plot, 'tabs': Tabs},
  data () {
    return {
      activeTab: 'Model',
      plotArray: [1],
      idCounter: 2
    }
  },
  methods: {
    addPlot () {
      this.plotArray.push(this.idCounter)
      ++this.idCounter
    },
    removePlot (id) {
      console.log('Removing plot', id)
      this.plotArray = this.plotArray.filter(val => val !== id)
    }
  }
}
</script>
<style>
.plots-div {
  max-height: 85vh;
  overflow-y: auto;
  border: 1px blue;
  border-style: solid;
  border-radius: 10px;
}
</style>
