<template>
  <div>
    <div id="plot-div"></div>
    <button type="button" name="button" @click="update_error">Show Plot</button>
    <p class="error">{{ error }}</p>
  </div>
</template>

<script>
import Plotly from 'plotly.js'

export default {
  name: 'Plot',
  data () {
    return {
      error: ''
    }
  },

  methods: {
    update_error () {
      this.error = 'No Errors!'
    }
  },

  created () {
    this.$http.headers.common['Access-Control-Allow-Origin'] = '*'
    this.$http.get('get_data')
      .then(response => {
        return response.json()
      })
      .then(data => {
        console.log(data)
        var plotArray = []
        for (var key in data) {
          if (data.hasOwnProperty(key)) {
            console.log(data[key])
            if (key !== 'time') {
              plotArray.push({
                x: data.time,
                y: data[key],
                mode: 'lines+markers',
                type: 'scatter',
                name: key
              })
            }
          }
        }
        Plotly.newPlot('plot-div', plotArray)
      })
  },
  mounted () {
    Plotly.newPlot('plot-div', [{
      x: [1, 2, 3, 4],
      y: [56, 34, 87, 12]
    }])
  }
}
</script>

<style lang="css">
.error{
    color: red;
}
</style>
