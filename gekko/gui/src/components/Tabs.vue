<template class="tab-div">
  <div>
    <img
      src="/static/GekkoLogo.png"
      height="65px">
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
      open: false
    }
  },
  computed: {
    modelData () { return this.$store.state.modelData },
    varsData () { return this.$store.state.varsData }
  },
  methods: {
    toggle: function (v, prop) {
      v.ishidden = !v.ishidden
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
  max-height: 83vh;
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
