// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import Plot from './components/Plot'
import Tabs from './components/Tabs'
import router from './router.js'
import store from './store.js'

Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  el: '#app',
  store,
  router,
  components: { App, Plot, Tabs },
  template: '<App/>'
})
