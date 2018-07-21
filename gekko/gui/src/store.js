import Vue from 'vue'
import Vuex from 'vuex'

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
    },
    httpRoot: process.env.NODE_ENV === 'development' ? 'http://localhost:8050' : 'http://' + location.hostname + ':' + location.port,
    updateNumber: 0
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
    setCommunicationError (state, data) {
      if (!state.communicationError) {
        if (!state.showErrorModal) {
          state.showErrorModal = data
        }
        state.communicationError = data
      }
    },
    sethttpError (state, data) { state.httpError = data },
    showFullscreenPlot (state, data) { state.fullscreenPlot = data },
    setPlotData (state, data) {
      state.plotData = data
      for (var i = 0; i < state.plots.length; i++) {
        // Find a clever way to hot reload the plot data here
        // Make sure to retain the state describing which traces are displayed
        var plotData = state.plots[i].data
        for (var j = 0; j < plotData.length; j++) {
          var trace = plotData[j]
          var updatedTrace = state.plotData.find((t) => t.name === trace.name)
          trace.x = updatedTrace.x
          trace.y = updatedTrace.y
        }
      }
      state.updateNumber++
    },
    updatePlotLayout (state, data) { state.plots.find(p => p.id === data.id).layout = data.layout },
    setModelData (state, data) { state.modelData = data },
    setVarsData (state, data) { state.varsData = data },
    showErrorModal (state, data) { state.showErrorModal = data }
  },
  actions: {
    get_data ({commit, state}) {
      var api1 = fetch(`${this.state.httpRoot}/data`)
        .then(data => data.json())
        .then(data => {
          console.log('data', data)
          commit('setModelData', data.model)
          var plotArray = []
          const isMuchData = (
            data.vars.variables.length + data.vars.parameters.length +
            data.vars.intermediates.length + data.vars.constants.length
          ) > 5
          const v = data.vars
          for (var set in data.vars) {
            for (var variable in v[set]) {
              const trace = {
                x: v[set][variable].x,
                y: v[set][variable].data,
                mode: v[set][variable].data.length > 1 ? 'lines' : 'markers',
                type: 'scatter',
                name: v[set][variable].name,
                visible: isMuchData || set === 'intermediates' ? 'legendonly' : 'true'
              }
              plotArray.push(trace)
            }
          }
          commit('setPlotData', plotArray)
        })
        .catch(err => {
          console.log('Error fetching from get_data:', err)
        })
      const ignoredProps = ['INFO', 'APM']
      let options
      let varsData = {}
      var api2 = fetch(`${this.state.httpRoot}/get_options`)
        .then(data => data.json())
        .then(obj => {
          options = obj
          return Object.keys(obj).filter(key => !ignoredProps.includes(key))
        })
        .then(keys => {
          keys.forEach(key => {
            varsData[key] = options[key]
            varsData[key].ishidden = state.varsData[key] ? state.varsData[key].ishidden : true
            return null
          })
        }).then(() => {
          commit('setVarsData', varsData)
        })
      // This ensures .then on this action is only called after both return
      return Promise.all([api1, api2])
    },
    initialize ({commit, dispatch}) {
      dispatch('get_data').then(() => {
        commit('addPlot') // First plot added is the hidden fullscreen plot
        commit('updatePlotLayout', {id: 0, layout: {'height': window.innerHeight - 150}})
        commit('addPlot') // Second plot is the one shown on the main page
      })
    },
    poll ({commit, dispatch}) {
      fetch(`${this.state.httpRoot}/poll`)
        .then(resp => resp.json())
        .then(body => {
          if (body.updates === true) {
            dispatch('get_data')
          }
          this.showModal = false
          commit('setCommunicationError', false)
          setTimeout(() => {
            dispatch('poll')
          }, 1000)
        }, error => {
          console.log('HTTP Polling Error, Status:', error)
          commit('sethttpError', {
            header: 'Internal Communication Error',
            body: `This most often happens when the Gekko script
                crashes or exits for some reason. If this happens
                we cannot get any updates from your Gekko model.
                Please close this window and restart the script
                if this is the problem, otherwise report the
                following error.
                  ${error}`,
            report: `Please report any Gekko project errors as
              issues at https://github.com/BYU-PRISM/GEKKO`
          })
          commit('setCommunicationError', true)
        })
    }
  }
})

export default store
