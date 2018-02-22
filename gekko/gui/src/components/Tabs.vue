<template class="tab-div">
  <div>
    <ul class="nav nav-tabs">
      <li class="nav-item tab">
        <a class="nav-link "
          @click="activeTab = 'Model'">Model</a>
      </li>
      <li class="nav-item tab">
        <a class="nav-link"
        @click="activeTab = 'Variables'">Variables</a>
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
              <tr v-for="(value, prop) in modelData" :key="prop.id">
                <td>{{prop}}</td>
                <td>{{value}}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
      <template v-if="activeTab === 'Variables'">
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
      activeTab: 'Variables',
      modelData: {},
      varsData: {}
    }
  },
  computed: {
    // activeTab = 'Variables'
  },

  created () {
    const ignoredProps = ['INFO', 'APM']
    let options
    this.$http.get('get_options')
      .then(response => response.json())
      .then(obj => {
        options = obj
        console.log('obj:', obj)
        this.modelData = obj['APM']
        return Object.keys(obj).filter(key => !ignoredProps.includes(key))
      })
      .then(keys => {
        keys.forEach(key => {
          console.log(options)
          this.varsData[key] = options[key]
          return null
        })
      }).then(() => {
        console.log('varsData:', this.varsData)
      })
    this.$http.get('get_model')
      .then(response => response.json())
      .then(model => {
        this.modelData = model
        console.log('model:', this.modelData)
      })
  }
}
</script>
<style lang="css">
.tab {
  cursor: pointer;
}
</style>
