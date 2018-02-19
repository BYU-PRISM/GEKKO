<template>
  <div class="mainDiv">
    <div class="row">
      <div class="col-sm-3">
        <h4>Options Data</h4>
        <div class="tab-div">
          <!-- <tabs :options="{ useUrlFragment: false }">
            <tab name="APM">
              <p>The APM JSON goes here</p>
            </tab>
            <tab name="Other">
              <p>The other stuff could go here</p>
            </tab>
          </tabs> -->
        </div>
      </div>
      <div class="col-sm-9">
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
