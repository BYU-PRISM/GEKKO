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
      <transition name="fade">
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
      </transition>
      <transition name="fade">
        <template v-if="activeTab === 'Variables'">
          <div
            v-if="varsData"
            class="tab-table">
            <div style="overflow-y:auto; max-height:inherit">
              <ul
                v-for="(v, key) in varsData"
                :key="v.id"
                class="tab-table-item">
                <a
                  class="var-dropdown"
                  @click="toggle(v, key)">
                  {{ key }} {{ v.ishidden ? '►' : '&#9660;' }}
                </a>
                <transition name="fade">
                  <div
                    class="table-responsive"
                    v-if="!v.ishidden">
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
                          <td v-if="prop != 'ishidden'">{{ prop }}</td>
                          <td v-if="prop != 'ishidden'">{{ (Number.isInteger(value) && value <= 100000 && value > -100000) ? value : value.toExponential(4) /*eslint-disable-line*/}}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </transition>
              </ul>
            </div>
          </div>
        </template>
      </transition>
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
          this.varsData[key].ishidden = true
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
    toggle: function (v, prop) {
      v.ishidden = !v.ishidden
      // FIXME: Should try and find a softer way of getting the DOM to update
      this.$forceUpdate()
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

.var-dropdown {
  cursor: pointer;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity .5s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>
