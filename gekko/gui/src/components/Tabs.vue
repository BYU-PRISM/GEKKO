<template class="tab-div">
  <div>
    <ul class="nav nav-tabs">
      <li class="nav-item tab">
        <a
          class="nav-link "
          @click="activeTab = 'Model'"
          :class="{ active: activeTab == 'Model'}">Model</a>
      </li>
      <li class="nav-item tab">
        <a
          class="nav-link"
          @click="activeTab = 'Variables'"
          :class="{ active: activeTab == 'Variables'}">Variables</a>
      </li>
    </ul>
    <div class="tab-div">
      <template v-if="activeTab === 'Model'">
        <div class="table-responsive tab-table">
          <table class="table table-striped table-sm">
            <thead>
              <tr>
                <th>Property</th>
                <th>Value</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(value, prop) in modelData"
                :key="prop.id">
                <td>{{ prop }}</td>
                <td>{{ value }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
      <template v-if="activeTab === 'Variables'">
        <div
          v-if="varsData"
          class="tab-table">
          <div style="overflow-y:auto; max-height:inherit">
            <ul
              v-for="(v, key) in varsData"
              :key="v.id"
              class="tab-table-item">
              <a>
                {{ key }}
              </a>
              <div class="table-responsive">
                <table class="table table-striped table-sm">
                  <thead>
                    <tr>
                      <th>Property</th>
                      <th>Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="(value, prop) in v"
                      :key="prop.id">
                      <td>{{ prop }}</td>
                      <td>{{ value }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </ul>
          </div>
        </div>
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
      modelData: {},
      varsData: {},
      open: false
    }
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
  },

  methods: {
    toggle: function () {
      this.open = !this.open
    }
  }
}
</script>
<style lang="css">
.tab {
  cursor: pointer;
}
.tab-table {
  max-height: 87vh;
}
.tab-table-item {
  padding-left: 0px;
}
</style>
