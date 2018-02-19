<template>
  <div class="mainDiv">
    <div class="row">
      <div class="col-sm-3">
        <tabs/>
      </div>
      <div class="col-sm-9">
        <plot/>
      </div>
    </div>
  </div>
</template>

<script>
import Plot from './Plot'
import Tabs from './Tabs'

export default {
  name: 'Main',
  components: {'plot': Plot, 'tabs': Tabs},
  data () {
    return {
      activeTab: 'Model'
    }
  }
}
</script>
