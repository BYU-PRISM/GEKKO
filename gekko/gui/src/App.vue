<template>
  <div id="app">
    <transition name="modal">
      <div
        v-if="showModal"
        class="modal-mask">
        <div class="modal-wrapper">
          <div class="modal-container">

            <div class="modal-header">
              <slot name="header">
                {{ httpError.header }}
              </slot>
            </div>

            <div class="modal-body">
              <slot name="body">
                {{ httpError.body }}
              </slot>
            </div>
            <div class="modal-body">
              <slot name="error-reporting">
                {{ httpError.report }}
              </slot>
            </div>

            <div class="modal-footer">
              <slot name="footer">
                <button
                  class="modal-default-button"
                  @click="showModal = false">
                  OK
                </button>
              </slot>
            </div>
          </div>
        </div>
      </div>
    </transition>
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App',
  data () {
    return {
      showModal: false,
      httpError: {
        header: '',
        body: '',
        report: `Please report any Gekko project errors as
          issues at https://github.com/BYU-PRISM/GEKKO`
      }
    }
  },
  mounted () {
    setTimeout(this.poll, 1000)
  },
  methods: {
    poll () {
      this.$http.headers.common['Access-Control-Allow-Origin'] = '*'
      this.$http.get('poll')
        .then(resp => {
          // Will implement updating here
          this.showModal = false
        }, error => {
          console.log('HTTP Polling Error, Status:', error.status, 'Message:', error.statusText)
          if (error.status === 0) {
            this.httpError.header = 'Internal Communication Error'
            this.httpError.body = `We seem to have lost communication with your
                                  Gekko script. This means that we cannot get
                                  any updates from your Gekko model.
                                  Did you stop the script or did
                                  it crash? If so, close this window and restart
                                  it.`
          } else {
            this.httpError.header = 'Internal Communication Error'
            this.httpError.body = `Please copy these details in an error report
                                  to the Gekko developers. Error Code:
                                  ${error.status}, Error: ${error.statusText}`
          }
          this.showModal = true
        })
      setTimeout(this.poll, 1000)
    }
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin-left: 10px;
  margin-top: 10px;
  margin-bottom: 10px;
  max-width: 98vw;
}

.modal-mask {
  position: fixed;
  z-index: 9998;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, .5);
  display: table;
  transition: opacity .3s ease;
}

.modal-wrapper {
  display: table-cell;
  vertical-align: middle;
}

.modal-container {
  width: 500px;
  margin: 0px auto;
  padding: 20px 30px;
  background-color: #fff;
  border-radius: 2px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, .33);
  transition: all .3s ease;
  font-family: Helvetica, Arial, sans-serif;
}

.modal-header h3 {
  margin-top: 0;
  color: #42b983;
}

.modal-body {
  margin: 20px 0;
}

.modal-default-button {
  float: right;
}

/*
 * The following styles are auto-applied to elements with
 * transition="modal" when their visibility is toggled
 * by Vue.js.
 *
 * You can easily play with the modal transition by editing
 * these styles.
 */

.modal-enter {
  opacity: 0;
}

.modal-leave-active {
  opacity: 0;
}

.modal-enter .modal-container,
.modal-leave-active .modal-container {
  -webkit-transform: scale(1.1);
  transform: scale(1.1);
}
</style>
