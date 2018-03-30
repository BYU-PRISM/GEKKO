<template lang="html">
  <transition name="modal">
    <div class="modal-mask">
      <div class="modal-wrapper">
        <div class="modal-fullscreen-container">
          <div class="modal-body">
            <slot name="body">
              <plot :external-id="0"/>
            </slot>
          </div>
          <div class="modal-footer">
            <slot name="footer">
              <button @click="$emit('close', {})">Close</button>
            </slot>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
import Plot from './Plot'
export default {
  components: { 'plot': Plot },
  data () {
    return { }
  }
}
</script>

<style lang="css">
.modal-fullscreen-container {
  width: 90%vw;
  margin: 0px auto;
  padding: 20px 30px;
  background-color: #fff;
  border-radius: 2px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, .33);
  transition: all .3s ease;
  font-family: Helvetica, Arial, sans-serif;
}
</style>
