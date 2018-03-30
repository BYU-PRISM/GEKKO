import Vue from 'vue'
import Vuex from 'vuex'
import { HTTP } from '../http'

Vue.use(Vuex)

const store = new Vuex.Store({
  state: {
    numPlots: 0, // id: 0 is always the fullscreen plot
    communicationError: false,
    fullscreenPlot: false,
    plotIdCounter: 0,
    plots: [
      // id: number
      // data: Object
      // layout: Object
    ],
    plotData: {
      // A list of traces as returned by updatePlotData
      // initialized in App.vue
    },
    modelData: {
      // list of gekko model attributes
    },
    varsData: {
      // list of gekko variable objects
    },
    showErrorModal: false,
    httpError: {
      header: '',
      body: '',
      report: `Please report any Gekko project errors as
        issues at https://github.com/BYU-PRISM/GEKKO`
    }
  },
  mutations: {
    removePlot: (state, data) => {
      state.numPlots--
      state.plots = state.plots.filter(plot => plot.id !== data)
    },
    addPlot (state, data) {
      state.plots.push({
        id: state.plotIdCounter,
        data: state.plotData,
        layout: {}
      })
      state.plotIdCounter++
      state.numPlots++
    },
    setCommunicationError (state, data) { state.communicationError = data },
    showFullscreenPlot (state) { state.fullscreenPlot = true },
    hideFullscreenPlot (state) { state.fullscreenPlot = false },
    updatePlotData (state, data) { state.plotData = data },
    updatePlotLayout (state, data) { state.plots.filter(p => p.id === data.id)[0].layout = data.layout },
    setModelData (state, data) { state.modelData = data },
    setVarsData (state, data) { state.varsData = data },
    showErrorModal (state, data) { state.showErrorModal = true },
    hideErrorModal (state, data) { state.showErrorModal = false }
  },
  actions: {
    initialize ({commit, state}) {
      HTTP.get('/get_data')
        .then(data => data.data)
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
          commit('addPlot') // First plot added is the hidden fullscreen plot
          commit('updatePlotLayout', {id: 0, layout: {'height': window.innerHeight - 150}})
          commit('addPlot') // Second plot is the one shown on the main page
        })
        .catch(err => {
          console.log('Error fetching from get_data:', err)
        })
      const ignoredProps = ['INFO', 'APM']
      let options
      let varsData = {}
      HTTP.get('get_options')
        .then(data => data.data)
        .then(obj => {
          options = obj
          console.log('options:', obj)
          return Object.keys(obj).filter(key => !ignoredProps.includes(key))
        })
        .then(keys => {
          keys.forEach(key => {
            varsData[key] = options[key]
            varsData[key].ishidden = true
            return null
          })
        }).then(() => {
          commit('setVarsData', varsData)
          console.log('varsData:', varsData)
        })
      HTTP.get('get_model')
        .then(data => data.data)
        .then(model => {
          commit('setModelData', model)
          console.log('model:', model)
        })
    }
  }
})

export default store
