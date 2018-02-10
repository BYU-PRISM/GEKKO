<template>
  <div class="mainDiv">
    <div class="row">
      <div class="col-sm-3">
        <h4>Options Data</h4>
      </div>
      <div class="col-sm-9">
        <h4>Plot Here</h4>
        <plot/>
      </div>
    </div>
  </div>
</template>

<script>
import Plot from './Plot'
export default {
  name: 'Main',
  components: {'plot': Plot},
  data () {
    return {
      test_string: 'Can you see me now?'
    }
  }
}
</script>

<style lang="css">
</style>
