<template class="tab-div">
  <div>
    <ul class="nav nav-tabs">
      <li class="nav-item tab">
        <a class="nav-link active" @click="activeTab = 'Model'">Model</a>
      </li>
      <li class="nav-item tab">
        <a class="nav-link" @click="activeTab = 'Results'">Results</a>
      </li>
    </ul>
    <div class="tab-div">
      <template v-if="activeTab === 'Model'">
        <div class="table-responsive">
          <table class="table table-striped table-sm">
            <thead>
              <tr>
                <th>Property</th>
                <th>Value</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(value, prop) in APMdata" :key="prop.id">
                <td>{{prop}}</td>
                <td>{{value}}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
      <template v-if="activeTab === 'Results'">
        Results tab here
      </template>
    </div>
  </div>
</template>
<script>
export default {
  name: 'Tabs',
  data () {
    return {
      activeTab: 'Model',
      APMdata: {}
    }
  },
  created () {
    this.$http.get('get_options')
      .then(response => response.json())
      .then(options => {
        this.APMdata = options.APM
        console.log('Options', options)
      })
  }
}
</script>
<style lang="css">
.tab {
  cursor: pointer;
}
</style>
