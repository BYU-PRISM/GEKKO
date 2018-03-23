import Vue from 'vue'
import Vuex from 'vuex'
import VueResource from 'vue-resource'

Vue.use(Vuex)
Vue.use(VueResource)

const store = new Vuex.Store({
  state: {
    numPlots: 1,
    fullscreenPlot: false,
    plotIdCounter: 1,
    plots: [
      // id: number
      // data: Object
      // layout: Object
    ],
    plotData: {
      // A list of traces as returned by updatePlotData
      // initialized in App.vue
    }

  },
  mutations: {
    addPlot (state) {
      state.plots.push({
        id: state.plotIdCounter,
        data: state.plotData,
        layout: {}
      })
      state.plotIdCounter++
    },
    removePlot: state => state.numPlots--,
    showFullscreenPlot (state) { state.fullscreenPlot = true },
    hideFullscreenPlot (state) { state.fullscreenPlot = false },
    updatePlotData (state, data) { state.plotData = data }
  },
  actions: {
    updatePlotDataAsync ({commit, state}) {
      window.fetch(
        '/get_data',
        {headers: {
          'Access-Control-Request-Headers': 'Access-Control-Allow-Origin',
          'Access-Control-Allow-Origin': '*',
          'If-None-Match': 'CertainlyNotMyEtag'
        }
        })
        .then(response => {
          return response.json()
        })
        .then(data => {
          var plotArray = []
          console.log('get_data data:', data)
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
          commit('updatePlotData', plotArray)
        })
        .catch(err => {
          console.log('Error fetching from get_data:', err)
        })
    }
  }
})

export default store
