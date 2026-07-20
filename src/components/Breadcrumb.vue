<template>
  <el-breadcrumb class="breadcrumb">
    <el-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="index" :to="item.path">
      {{ item.meta?.title || item.name }}
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const breadcrumbs = ref([])

// 生成面包屑数据
const getBreadcrumbs = () => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  const first = matched[0]
  
  if (!first) {
    return []
  }

  const crumbs = [{
    path: '/',
    name: 'Home'
  }]

  matched.forEach(item => {
    if (item.path === '/') return
    crumbs.push({
      path: item.path,
      name: item.name,
      meta: item.meta
    })
  })

  return crumbs
}

// 监听路由变化更新面包屑
watch(
  () => route.path,
  () => {
    breadcrumbs.value = getBreadcrumbs()
  },
  { immediate: true }
)
</script>

<style scoped>
.breadcrumb {
  margin-left: 20px;
}
</style> 