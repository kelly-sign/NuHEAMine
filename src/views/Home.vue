<template>
  <div class="home-container">
    <header class="header">
      <div class="logo">A Nuclear-use High-Entropy Alloy Data Management and Mining Platform</div>
      <div class="user-info">
        <span>Welcome, {{ username }}</span>
        <button class="logout-button" @click="handleLogout">Log Out</button>
      </div>
    </header>
    
    <nav class="main-nav">
      <ul class="nav-list">
        <li class="nav-item active">
          <i class="nav-icon">📊</i>
          <span>Home</span>
        </li>
        <li class="data-nav-host">
          <el-popover
            v-model:visible="showDropdown"
            trigger="click"
            placement="bottom-start"
            :width="520"
            popper-class="data-nav-popper"
          >
            <template #reference>
              <div
                class="nav-item data-nav-item"
                :class="{ 'is-open': showDropdown }"
              >
                <i class="nav-icon">🔍</i>
                <span>Data Management</span>
                <span class="data-nav-caret" aria-hidden="true">▾</span>
              </div>
            </template>

            <div class="data-menu-panel">
              <button type="button" class="data-menu-item" @click="goToMaterialSearch">
                <i class="menu-icon">📋</i>
                <span>Material</span>
              </button>
              <button type="button" class="data-menu-item" @click="goToProcessSearch">
                <i class="menu-icon">⚙️</i>
                <span>Processing</span>
              </button>
              <button type="button" class="data-menu-item" @click="goToPropertySearch">
                <i class="menu-icon">📊</i>
                <span>Room-Temperature</span>
              </button>
              <button type="button" class="data-menu-item" @click="goToHTPropertySearch">
                <i class="menu-icon">🔥</i>
                <span>High-Temperature</span>
              </button>
              <button type="button" class="data-menu-item" @click="goToImpTestSearch">
                <i class="menu-icon">🔨</i>
                <span>Impact Test</span>
              </button>
              <button type="button" class="data-menu-item" @click="goToCreTestSearch">
                <i class="menu-icon">⏱️</i>
                <span>Creep Test</span>
              </button>
              <button type="button" class="data-menu-item" @click="goToFatTestSearch">
                <i class="menu-icon">🔄</i>
                <span>Fatigue Test</span>
              </button>
              <button type="button" class="data-menu-item" @click="goToIrrConditionSearch">
                <i class="menu-icon">☢️</i>
                <span>Irradiation Conditions</span>
              </button>
              <button type="button" class="data-menu-item" @click="goToMicrostructureSearch">
                <i class="menu-icon">🔬</i>
                <span>Microstructure Evolution</span>
              </button>
              <button type="button" class="data-menu-item" @click="goToHardeningSearch">
                <i class="menu-icon">🛡️</i>
                <span>Irradiation Hardening</span>
              </button>
              <button type="button" class="data-menu-item" @click="goToEmbrittlementSearch">
                <i class="menu-icon">🧩</i>
                <span>Irradiation Embrittlement</span>
              </button>
              <button type="button" class="data-menu-item" @click="goToIrrCreepSearch">
                <i class="menu-icon">☢️</i>
                <span>Irradiation Creep</span>
              </button>
              <button type="button" class="data-menu-item" @click="goToDocumentSearch">
                <i class="menu-icon">📚</i>
                <span>References</span>
              </button>
            </div>
          </el-popover>
        </li>
        <!-- Render prediction entries from shared metadata so future models need no menu rewrite. -->
        <li class="prediction-nav-host">
          <el-popover
            v-model:visible="predictionMenuVisible"
            trigger="click"
            placement="bottom-start"
            :width="680"
            popper-class="prediction-nav-popper"
          >
            <template #reference>
              <div
                class="nav-item prediction-nav-item"
                :class="{ 'is-open': predictionMenuVisible }"
              >
                <i class="nav-icon">🧪</i>
                <span>Performance Prediction</span>
                <span class="prediction-nav-caret" aria-hidden="true">▾</span>
              </div>
            </template>

            <div class="prediction-menu-panel">
              <section
                v-for="group in predictionMenuGroups"
                :key="group.key"
                class="prediction-menu-group"
              >
                <div class="prediction-menu-heading">
                  <span class="prediction-menu-group-icon" aria-hidden="true">{{ group.icon }}</span>
                  <span>{{ group.title }}</span>
                </div>
                <button
                  v-for="item in group.items"
                  :key="item.key"
                  type="button"
                  class="prediction-menu-item"
                  @click="goToPredictionPage(item.route)"
                >
                  <span>{{ item.title }}</span>
                  <span class="prediction-menu-arrow" aria-hidden="true">›</span>
                </button>
              </section>
            </div>
          </el-popover>
        </li>
        <li class="nav-item" @click="goToVisualization">
          <i class="nav-icon">📈</i>
          <span>Data Visualization</span>
        </li>
        <li class="nav-item">
          <i class="nav-icon">📝</i>
          <span>Report Generation</span>
        </li>
        <li class="nav-item">
          <i class="nav-icon">⚙️</i>
          <span>System Settings</span>
        </li>
      </ul>
    </nav>

    <main class="main-content">
      <div class="dashboard">
        <div class="dashboard-header">
          <h1>Data Overview</h1>
          <div class="date-info">{{ currentDate }}</div>
        </div>
        
        <div class="stats-cards">
          <div class="stat-card" @click="goToDataList">
            <div class="stat-icon materials-icon">🧪</div>
            <div class="stat-info">
              <div class="stat-value">{{ materialsCount }}</div>
              <div class="stat-label">Material Data</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon predictions-icon">📈</div>
            <div class="stat-info">
              <div class="stat-value">567</div>
              <div class="stat-label">Prediction Records</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon reports-icon">📝</div>
            <div class="stat-info">
              <div class="stat-value">89</div>
              <div class="stat-label">Analysis Reports</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon users-icon">👥</div>
            <div class="stat-info">
              <div class="stat-value">45</div>
              <div class="stat-label">Active Users</div>
            </div>
          </div>
        </div>

        <div class="quick-actions">
          <h2>Quick Actions</h2>
          <div class="action-buttons">
            <el-button type="primary" @click="goToDataList">
              <el-icon><Search /></el-icon>
              Data Query
            </el-button>
            <el-button>
              <el-icon><Upload /></el-icon>
              Data Import
            </el-button>
            <el-button @click="goToPrediction">
              <el-icon><TrendCharts /></el-icon>
              Performance Prediction
            </el-button>
            <el-button>
              <el-icon><Document /></el-icon>
              Generate Report
            </el-button>
          </div>
        </div>
        
        <div class="recent-activity">
          <h2>Recent Activities</h2>
          <div class="activity-list">
            <div class="activity-item">
              <div class="activity-time">10:30</div>
              <div class="activity-content">
                <div class="activity-title">New High-Entropy Alloy Data Added</div>
                <div class="activity-desc">10 new composition entries of high-entropy alloys have been added</div>
              </div>
            </div>
            
            <div class="activity-item">
              <div class="activity-time">09:15</div>
              <div class="activity-content">
                <div class="activity-title">Performance Prediction Completed</div>
                <div class="activity-desc">Hardness prediction for 3 high-entropy alloy samples has been finished</div>
              </div>
            </div>
            
            <div class="activity-item">
              <div class="activity-time">Yesterday</div>
              <div class="activity-content">
                <div class="activity-title">Analysis Report Generated</div>
                <div class="activity-desc">A comparative analysis report of high-entropy alloy properties has been generated</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
    
    <footer class="footer">
      <div>Copyright 2025 A Nuclear-use High-Entropy Alloy Data Management and Mining Platform. All rights reserved.</div>
    </footer>
  </div>
</template>

<script>
import { computed, ref, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { Search, Upload, TrendCharts, Document } from '@element-plus/icons-vue';
import { getMaterials } from '@/api/material';
import { ElMessage } from 'element-plus';
import { predictionMenuGroups, predictionModuleConfigs } from '@/config/predictionModules';

export default {
  name: 'Home',
  components: {
    Search,
    Upload,
    TrendCharts,
    Document
  },
  setup() {
    const store = useStore();
    const router = useRouter();
    const materialsCount = ref(0);
    const showDropdown = ref(false);
    const predictionMenuVisible = ref(false);
    
    const username = computed(() => {
      const user = store.getters['user/currentUser'];
      return user ? user.username : 'User';
    });
    
    const currentDate = ref(new Date().toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long'
    }));
    
    const handleLogout = async () => {
      await store.dispatch('user/logout');
      router.push('/login');
    };

    const goToDataList = () => {
      router.push('/search/material')
    };

    const goToMaterialSearch = () => {
      try {
        router.push('/search/material');
        showDropdown.value = false;
      } catch (error) {
        console.error('Navigation failed:');
        ElMessage.error('Navigation failed. Please try again later.');
      }
    };

    const goToProcessSearch = () => {
      try {
        router.push('/search/process');
        showDropdown.value = false;
      } catch (error) {
        console.error('Navigation failed:');
        ElMessage.error('Navigation failed. Please try again later.');
      }
    };

    const goToPropertySearch = () => {
      try {
        router.push('/search/property');
        showDropdown.value = false;
      } catch (error) {
        console.error('Navigation failed:');
        ElMessage.error('Navigation failed. Please try again later.');
      }
    };

    const goToHTPropertySearch = () => {
      try {
        router.push('/search/htproperty');
        showDropdown.value = false;
      } catch (error) {
        console.error('Navigation failed:');
        ElMessage.error('Navigation failed. Please try again later.');
      }
    };

    const goToImpTestSearch = () => {
      try {
        router.push('/search/imptest');
        showDropdown.value = false;
      } catch (error) {
        console.error('Navigation failed:');
        ElMessage.error('Navigation failed. Please try again later.');
      }
    };

    const goToCreTestSearch = () => {
      try {
        router.push('/search/cretest');
        showDropdown.value = false;
      } catch (error) {
        console.error('Navigation failed:');
        ElMessage.error('Navigation failed. Please try again later.');
      }
    };

    const goToFatTestSearch = () => {
      try {
        router.push('/search/fattest');
        showDropdown.value = false;
      } catch (error) {
        console.error('Navigation failed:');
        ElMessage.error('Navigation failed. Please try again later.');
      }
    };

    const goToIrrConditionSearch = () => {
      try {
        router.push('/search/irrcondition');
        showDropdown.value = false;
      } catch (error) {
        console.error('Navigation failed:');
        ElMessage.error('Navigation failed. Please try again later.');
      }
    };

    const goToMicrostructureSearch = () => {
      try {
        router.push('/search/microstructure');
        showDropdown.value = false;
      } catch (error) {
        console.error('Navigation failed:');
        ElMessage.error('Navigation failed. Please try again later.');
      }
    };

    const goToHardeningSearch = () => {
      try {
        router.push('/search/hardening');
        showDropdown.value = false;
      } catch {
        ElMessage.error('Failed to open the irradiation hardening table');
      }
    };

    const goToEmbrittlementSearch = () => {
      try {
        router.push('/search/embrittlement');
        showDropdown.value = false;
      } catch (error) {
        console.error('Navigation failed:');
        ElMessage.error('Navigation failed. Please try again later.');
      }
    };

    const goToIrrCreepSearch = () => {
      try {
        router.push('/search/irrcreep');
        showDropdown.value = false;
      } catch (error) {
        console.error('Navigation failed:');
        ElMessage.error('Navigation failed. Please try again later.');
      }
    };

    const goToDocumentSearch = () => {
      try {
        router.push('/search/document');
        showDropdown.value = false;
      } catch (error) {
        console.error('Navigation failed:');
        ElMessage.error('Navigation failed. Please try again later.');
      }
    };

    const goToPredictionPage = async (path) => {
      predictionMenuVisible.value = false
      try {
        await router.push(path)
        showDropdown.value = false
      } catch (error) {
        console.error('Navigation failed:')
        ElMessage.error('Navigation failed. Please try again later.')
      }
    }

    const goToPrediction = () => {
      // The dashboard shortcut continues to open the deployed hardness model.
      goToPredictionPage(predictionModuleConfigs.hardness.route)
    }

    const goToVisualization = () => {
      router.push('/visualization');
    };

    onMounted(async () => {
      try {
        const response = await getMaterials({ page: 1, page_size: 1 });
        if (response && response.data) {
          if (response.data.count !== undefined) {
            materialsCount.value = response.data.count;
          } 
          else if (Array.isArray(response.data.results)) {
            materialsCount.value = response.data.results.length;
          }
          else if (Array.isArray(response.data)) {
            materialsCount.value = response.data.length;
          }
          else {
            console.warn('Unexpected material-count response format.');
            materialsCount.value = 0;
          }
        } else {
          console.warn('Invalid material-count response.');
          materialsCount.value = 0;
        }
      } catch (error) {
        console.error('Failed to load the material count:');
        materialsCount.value = 0;
      }

    });
    
    return {
      username,
      currentDate,
      handleLogout,
      goToDataList,
      materialsCount,
      showDropdown,
      predictionMenuVisible,
      predictionMenuGroups,
      goToMaterialSearch,
      goToProcessSearch,
      goToPropertySearch,
      goToHTPropertySearch,
      goToImpTestSearch,
      goToCreTestSearch,
      goToFatTestSearch,
      goToIrrConditionSearch,
      goToMicrostructureSearch,
      goToHardeningSearch,
      goToEmbrittlementSearch,
      goToIrrCreepSearch,
      goToDocumentSearch,
      goToPrediction,
      goToPredictionPage,
      goToVisualization
    };
  }
};
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: #409eff;
  color: white;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logo {
  font-size: 22px;
  font-weight: bold;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-info span {
  margin-right: 16px;
  font-size: 16px;
}

.logout-button {
  background-color: transparent;
  border: 1px solid white;
  color: white;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  font-size: 15px;
}

.logout-button:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.main-nav {
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.nav-list {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  overflow-x: auto;
}

.nav-item {
  padding: 16px 24px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.3s;
  white-space: nowrap;
  position: relative;
  font-size: 16px;
}

.nav-item:hover {
  background-color: #ecf5ff;
}

.nav-item.active {
  background-color: #ecf5ff;
  color: #409eff;
  border-bottom: 2px solid #409eff;
}

.nav-icon {
  margin-right: 8px;
  font-size: 19px;
}

.data-nav-host {
  display: flex;
  list-style: none;
}

.data-nav-item {
  height: 100%;
  box-sizing: border-box;
}

.data-nav-caret {
  margin-left: 8px;
  color: #909399;
  font-size: 13px;
  transition: transform 0.2s ease;
}

.data-nav-item:hover .data-nav-caret {
  color: #409eff;
}

.data-nav-item.is-open {
  background-color: #ecf5ff;
  color: #409eff;
}

.data-nav-item.is-open .data-nav-caret {
  color: #409eff;
  transform: rotate(180deg);
}

.data-menu-panel {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.data-menu-item {
  min-height: 44px;
  padding: 10px 14px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  background-color: #fff;
  color: #606266;
  cursor: pointer;
  display: flex;
  align-items: center;
  font: inherit;
  font-size: 14px;
  text-align: left;
  transition: color 0.2s ease, border-color 0.2s ease, background-color 0.2s ease;
}

.data-menu-item:hover,
.data-menu-item:focus-visible {
  outline: none;
  border-color: #a0cfff;
  background-color: #ecf5ff;
  color: #409eff;
}

:global(.data-nav-popper.el-popover) {
  padding: 12px;
  border-color: #dcdfe6;
  max-width: calc(100vw - 24px);
  box-shadow: 0 8px 24px rgba(48, 49, 51, 0.14);
}

@media (max-width: 600px) {
  .data-menu-panel {
    grid-template-columns: 1fr;
    max-height: 70vh;
    overflow-y: auto;
  }
}

.prediction-nav-host {
  display: flex;
  list-style: none;
}

.prediction-nav-item {
  height: 100%;
  box-sizing: border-box;
}

.prediction-nav-caret {
  margin-left: 8px;
  color: #909399;
  font-size: 13px;
  transition: transform 0.2s ease;
}

.prediction-nav-item:hover .prediction-nav-caret {
  color: #409eff;
}

.prediction-nav-item.is-open {
  background-color: #ecf5ff;
  color: #409eff;
}

.prediction-nav-item.is-open .prediction-nav-caret {
  color: #409eff;
  transform: rotate(180deg);
}

.prediction-menu-panel {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.prediction-menu-group {
  overflow: hidden;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background-color: #fff;
}

.prediction-menu-heading {
  display: flex;
  align-items: center;
  min-height: 42px;
  padding: 0 14px;
  border-bottom: 1px solid #ebeef5;
  background-color: #f5f7fa;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.3;
}

.prediction-menu-group-icon {
  margin-right: 8px;
  font-size: 17px;
}

.prediction-menu-item {
  width: 100%;
  min-height: 42px;
  padding: 9px 14px;
  border: 0;
  border-bottom: 1px solid #f0f2f5;
  background-color: #fff;
  color: #606266;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font: inherit;
  font-size: 14px;
  text-align: left;
  transition: color 0.2s ease, background-color 0.2s ease;
}

.prediction-menu-item:last-child {
  border-bottom: 0;
}

.prediction-menu-item:hover,
.prediction-menu-item:focus-visible {
  outline: none;
  background-color: #ecf5ff;
  color: #409eff;
}

.prediction-menu-arrow {
  color: #a8abb2;
  font-size: 20px;
  line-height: 1;
}

.prediction-menu-item:hover .prediction-menu-arrow,
.prediction-menu-item:focus-visible .prediction-menu-arrow {
  color: #409eff;
}

:global(.prediction-nav-popper.el-popover) {
  padding: 14px;
  border-color: #dcdfe6;
  max-width: calc(100vw - 24px);
  box-shadow: 0 8px 24px rgba(48, 49, 51, 0.14);
}

@media (max-width: 767px) {
  .prediction-menu-panel {
    grid-template-columns: 1fr;
    max-height: 70vh;
    overflow-y: auto;
  }
}

.menu-icon {
  margin-right: 8px;
  font-size: 16px;
}

.main-content {
  margin-top: 40px;
  flex: 1;
  padding: 24px;
  background-color: #f5f7fa;
  position: relative;
  z-index: 1;
}

.dashboard {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 24px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.dashboard-header h1 {
  margin: 0;
  font-size: 26px;
  color: #303133;
}

.date-info {
  color: #909399;
  font-size: 15px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  padding: 20px;
  display: flex;
  align-items: center;
  border: 1px solid #ebeef5;
}

.stat-icon {
  font-size: 32px;
  margin-right: 16px;
  padding: 12px;
  border-radius: 8px;
}

.materials-icon {
  background-color: #ecf5ff;
  color: #409eff;
}

.predictions-icon {
  background-color: #f0f9eb;
  color: #67c23a;
}

.reports-icon {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.users-icon {
  background-color: #f5f7fa;
  color: #909399;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 26px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  color: #909399;
  font-size: 15px;
}

.element-visualization {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 24px;
  margin-bottom: 24px;
}

.element-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
}

.element-visualization h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.element-chart {
  width: 100%;
  height: 360px;
}

.data-visualization-section {
  width: 100%;
}

.hardness-visualization {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 24px;
  margin-bottom: 24px;
}

.hardness-scatter-chart {
  width: 100%;
  height: 420px;
}

.quick-actions {
  background-color: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.action-buttons {
  display: flex;
  gap: 16px;
  margin-top: 16px;
}

.recent-activity {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  padding: 20px;
  border: 1px solid #ebeef5;
}

.recent-activity h2 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 20px;
  color: #303133;
}

.activity-item {
  display: flex;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-time {
  width: 80px;
  color: #909399;
  font-size: 15px;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: bold;
  margin-bottom: 4px;
  color: #303133;
  font-size: 16px;
}

.activity-desc {
  color: #606266;
  font-size: 15px;
}

.footer {
  background-color: #f5f7fa;
  color: #909399;
  text-align: center;
  padding: 16px;
  border-top: 1px solid #e4e7ed;
  font-size: 15px;
}
</style> 
