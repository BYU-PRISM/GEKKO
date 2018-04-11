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
    httpRoot: process.env.NODE_ENV === 'development' ? 'http://localhost:8050' : 'http://' + location.hostname + ':' + location.port
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
    get_data ({commit, state}) {
      fetch(`${this.state.httpRoot}/data`)
        .then(data => data.json())
        .then(data => {
          console.log('data:', data)
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
                x: data.time,
                y: v[set][variable].data,
                mode: 'lines',
                type: 'scatter',
                name: v[set][variable].name,
                visible: isMuchData ? 'legendonly' : 'true'
              }
              plotArray.push(trace)
            }
          }
          commit('updatePlotData', plotArray)
        })
        .catch(err => {
          console.log('Error fetching from get_data:', err)
        })
      const ignoredProps = ['INFO', 'APM']
      let options
      let varsData = {}
      fetch(`${this.state.httpRoot}/get_options`)
        .then(data => data.json())
        .then(obj => {
          options = obj
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
        })
    },
    initialize ({commit, dispatch}) {
      dispatch('get_data').then(() => {
        commit('addPlot') // First plot added is the hidden fullscreen plot
        commit('updatePlotLayout', {id: 0, layout: {'height': window.innerHeight - 150}})
        commit('addPlot') // Second plot is the one shown on the main page
      })
    },
    update ({commit, dispatch}) {
      dispatch('get_data').then(() => {
        // Trigger plot rerenders here
        console.log('Rerender plots here')
      })
    },
    poll ({commit, dispatch}) {
      fetch(`${this.state.httpRoot}/poll`)
        .then(resp => resp.json())
        .then(body => {
          if (body.Updates === true) {
            console.log('updating')
            dispatch('update')
          }
          this.showModal = false
          commit('setCommunicationError', false)
          setTimeout(() => {
            dispatch('poll')
          }, 1000)
        }, error => {
          console.log('HTTP Polling Error, Status:', error.status, 'Message:', error.statusText)
          if (error.status === 0) {
            commit('sethttpError', {
              header: 'Internal Communication Error',
              body: `We seem to have lost communication with your
                    Gekko script. This means that we cannot get
                    any updates from your Gekko model.
                    Did you stop the script or did
                    it crash? If so, close this window and restart
                    it.`,
              report: `Please report any Gekko project errors as
                issues at https://github.com/BYU-PRISM/GEKKO`
            })
          } else {
            commit('sethttpError', {
              header: 'Internal Communication Error',
              body: `Please copy these details in an error report
                    to the Gekko developers. Error Code:
                    ${error.status}, Error: ${error.statusText}`,
              report: `Please report any Gekko project errors as
                issues at https://github.com/BYU-PRISM/GEKKO`
            })
          }
          commit('setCommunicationError', true)
        })
    }
  }
})

export default store
