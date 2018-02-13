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
