// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import VueRx from 'vue-rx'
import App from './App'
import Plot from './components/Plot'
import Tabs from './components/Tabs'
import VueResource from 'vue-resource'
import router from './router'
import { Observable } from 'rxjs/Observable'

Vue.use(VueRx, { Observable })
Vue.use(VueResource)
Vue.config.productionTip = false

// This configures the api root for development and production
if (process.env.NODE_ENV === 'development') {
  Vue.http.options.root = 'http://localhost:8050'
} else {
  Vue.http.options.root = 'http://' + location.hostname + ':' + location.port
}

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App, Plot, Tabs },
  template: '<App/>'
})
