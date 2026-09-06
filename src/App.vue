<script setup>
import NavBar from '../src/views/Home/NavBar.vue'
</script>

<template>
  <div class="nav"><NavBar /></div>

<router-view></router-view>
</template>

<style>
@font-face {font-family: 'iconfont';
    src: url('iconfont.eot');
    src: url('iconfont.eot?#iefix') format('embedded-opentype'),
    url('iconfont.woff') format('woff'),
    url('iconfont.ttf') format('truetype'),
    url('iconfont.svg#iconfont') format('svg');
}
.iconfont{
    font-family:"iconfont" !important;
    font-size:16px;font-style:normal;
    -webkit-font-smoothing: antialiased;
    -webkit-text-stroke-width: 0.2px;
    -moz-osx-font-smoothing: grayscale;}
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
.nav{
  position: fixed;
  top: 0;
  left: 0;
  z-index: 100;
}
</style>
