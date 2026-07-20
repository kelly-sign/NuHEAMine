<template>
  <div class="main-layout">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>NuHEAMine</h1>
          <el-menu
            mode="horizontal"
            :router="true"
            :default-active="$route.path"
          >
            <el-menu-item index="/">Home</el-menu-item>
            <el-menu-item index="/search/material">Material Search</el-menu-item>
            <el-menu-item index="/search/process">Process Search</el-menu-item>
            <el-menu-item index="/search/property">Room Temperature Structure Properties</el-menu-item>
            <el-menu-item index="/search/htproperty">High-Temperature Mechanical Properties</el-menu-item>
            <el-menu-item index="/search/imptest">Impact Test Table</el-menu-item>
            <el-menu-item index="/search/cretest">Creep Test Table</el-menu-item>
            <el-menu-item index="/search/fattest">Fatigue Test Table</el-menu-item>
            <el-menu-item index="/search/irrcondition">Irradiation Condition Table</el-menu-item>
            <el-menu-item index="/search/microstructure">Microstructure Evolution Table</el-menu-item>
          </el-menu>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'MainLayout'
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
  background-color: #f5f7fa;
}

.el-container {
  height: 100%;
}

.el-header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12);
  padding: 0 20px;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

h1 {
  margin: 0;
  font-size: 20px;
}

.el-main {
  padding: 20px;
  background-color: #f5f7fa;
}
</style> 