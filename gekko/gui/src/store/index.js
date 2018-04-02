import Vue from 'vue'
import Vuex from 'vuex'
import { HTTP } from '../http'

Vue.use(Vuex)
/* eslint-disable no-multi-spaces */
const store = new Vuex.Store({
  state: {
    numPlots: 0,                  // id: 0 is always the fullscreen plot
    communicationError: false,    // Whether there is a communication error with the backend
    fullscreenPlot: false,        // Whether the fullscreen plot should be displayed
    plotIdCounter: 0,             // Used for giving new plots externalIds
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
    // Object describing communication errors with the backend
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
        data: JSON.parse(JSON.stringify(state.plotData)),
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
      HTTP.get('/data')
        .then(data => data.data)
        .then(data => {
          console.log('new data obj:', data)
          commit('setModelData', data.model)
          var plotArray = []
          const isMuchData = (
            data.vars.variables.length + data.vars.parameters.length +
            data.vars.intermediates.length + data.vars.constants.length
          ) > 5
          const v = data.vars
          console.log(v)
          for (var set in data.vars) {
            console.log('set', set, v[set])
            for (var variable in v[set]) {
              console.log(v[set][variable])
              const trace = {
                x: data.time,
                y: v[set][variable].data,
                mode: 'lines',
                type: 'scatter',
                name: v[set][variable].name,
                visible: isMuchData ? 'legendonly' : 'true'
              }
              console.log('trace for:', variable.name, trace)
              plotArray.push(trace)
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
    }
  }
})

export default store
