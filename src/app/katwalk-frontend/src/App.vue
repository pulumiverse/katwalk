<template>
  <ChatView />
</template>

<script>
import ChatView from './components/ChatView.vue'

export default {
  name: 'App',
  components: {
    ChatView
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

*{
  background: #191825;
}
</style>
