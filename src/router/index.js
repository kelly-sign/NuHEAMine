import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'
import { getToken } from '@/utils/auth'
import MainLayout from '@/layout/MainLayout.vue'
import ProcessList from '@/views/process/ProcessList.vue'
import MaterialSearch from '@/views/data/MaterialSearch.vue'
import ProcessSearch from '@/views/process/ProcessSearch.vue'
import { predictionModuleConfigs } from '@/config/predictionModules'

// 路由懒加载
const Login = () => import('@/views/Login.vue')
const Register = () => import('@/views/Register.vue')
const Home = () => import('@/views/Home.vue')
const DataVisualization = () => import('@/views/visualization/DataVisualization.vue')
const NotFound = () => import('@/views/NotFound.vue')
const DataSearch = () => import('@/views/data/DataSearch.vue')
const PerformancePrediction = () => import('@/views/prediction/PerformancePrediction.vue')
const PredictionPage = () => import('@/views/prediction/components/PredictionPage.vue')

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { guest: true }
  },
  {
    path: '/search',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'material',
        name: 'MaterialSearch',
        component: () => import('@/views/data/MaterialSearch.vue'),
        meta: { title: 'Material Search', icon: 'el-icon-search' }
      },
      {
        path: 'process',
        name: 'ProcessSearch',
        component: () => import('@/views/process/ProcessSearch.vue'),
        meta: { title: 'Process Search', icon: 'el-icon-search' }
      },
      {
        path: 'property',
        name: 'PropertySearch',
        component: () => import('@/views/property/RoomTempPropertyList.vue'),
        meta: { title: 'Room Temperature Structure Properties', icon: 'el-icon-search' }
      },
      {
        path: 'htproperty',
        name: 'HTPropertySearch',
        component: () => import('@/views/htProperty/HTPropertyList.vue'),
        meta: { title: 'High-Temperature Mechanical Properties', icon: 'el-icon-search' }
      },
      {
        path: 'imptest',
        name: 'ImpTestSearch',
        component: () => import('@/views/impTest/ImpTestList.vue'),
        meta: { title: 'Impact Test Table', icon: 'el-icon-search' }
      },
      {
        path: 'cretest',
        name: 'CreTestSearch',
        component: () => import('@/views/creTest/CreTestList.vue'),
        meta: { title: 'Creep Test Table', icon: 'el-icon-search' }
      },
      {
        path: 'fattest',
        name: 'FatTestSearch',
        component: () => import('@/views/fatTest/FatTestList.vue'),
        meta: { title: 'Fatigue Test Table', icon: 'el-icon-search' }
      },
      {
        path: 'irrcondition',
        name: 'IrrConditionSearch',
        component: () => import('@/views/irrCondition/IrrConditionList.vue'),
        meta: { title: 'Irradiation Condition Table', icon: 'el-icon-search' }
      },
      {
        path: 'microstructure',
        name: 'MicrostructureSearch',
        component: () => import('@/views/microstructure/MicrostructureList.vue'),
        meta: { title: 'Microstructure Evolution Table', icon: 'el-icon-search' }
      },
      {
        path: 'hardening',
        name: 'HardeningSearch',
        component: () => import('@/views/hardening/HardeningList.vue'),
        meta: { title: 'Irradiation Hardening Table', icon: 'el-icon-search' }
      },
      {
        path: 'embrittlement',
        name: 'EmbrittlementSearch',
        component: () => import('@/views/embrittlement/EmbrittlementList.vue'),
        meta: { title: 'Irradiation Embrittlement Table', icon: 'el-icon-search' }
      },
      {
        path: 'irrcreep',
        name: 'IrrCreepSearch',
        component: () => import('@/views/irrCreep/IrrCreepList.vue'),
        meta: { title: 'Irradiation Creep Table', icon: 'el-icon-search' }
      },
      {
        path: 'document',
        name: 'DocumentSearch',
        component: () => import('@/views/document/DocumentList.vue'),
        meta: { title: 'Reference Documents Table', icon: 'el-icon-search' }
      }
    ]
  },
  {
    path: '/process',
    name: 'ProcessList',
    component: ProcessList,
    meta: {
      requiresAuth: true,
      title: 'Process List'
    }
  },
  // Preserve the original prediction entry while exposing one route per model.
  {
    path: '/prediction',
    redirect: predictionModuleConfigs.hardness.route
  },
  {
    path: predictionModuleConfigs.hardness.route,
    name: 'PerformancePrediction',
    component: PerformancePrediction,
    meta: { requiresAuth: true, title: predictionModuleConfigs.hardness.title }
  },
  {
    path: predictionModuleConfigs.yieldStrength.route,
    name: 'YieldStrengthPrediction',
    component: PredictionPage,
    props: predictionModuleConfigs.yieldStrength,
    meta: { requiresAuth: true, title: predictionModuleConfigs.yieldStrength.title }
  },
  {
    path: predictionModuleConfigs.tensileStrength.route,
    name: 'TensileStrengthPrediction',
    component: PredictionPage,
    props: predictionModuleConfigs.tensileStrength,
    meta: { requiresAuth: true, title: predictionModuleConfigs.tensileStrength.title }
  },
  {
    path: predictionModuleConfigs.phaseComposition.route,
    name: 'PhaseCompositionPrediction',
    component: PredictionPage,
    props: predictionModuleConfigs.phaseComposition,
    meta: { requiresAuth: true, title: predictionModuleConfigs.phaseComposition.title }
  },
  {
    path: predictionModuleConfigs.irradiationHardening.route,
    name: 'IrradiationHardeningPrediction',
    component: PredictionPage,
    props: predictionModuleConfigs.irradiationHardening,
    meta: { requiresAuth: true, title: predictionModuleConfigs.irradiationHardening.title }
  },
  {
    path: predictionModuleConfigs.irradiationEmbrittlement.route,
    name: 'IrradiationEmbrittlementPrediction',
    component: PredictionPage,
    props: predictionModuleConfigs.irradiationEmbrittlement,
    meta: { requiresAuth: true, title: predictionModuleConfigs.irradiationEmbrittlement.title }
  },
  {
    path: '/visualization',
    name: 'DataVisualization',
    component: DataVisualization,
    meta: { requiresAuth: true, title: 'Data Visualization' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  const token = getToken()
  const isAuthenticated = store.getters['user/isAuthenticated']
  
  // 如果有token但状态显示未认证，同步认证状态
  if (token && !isAuthenticated) {
    store.commit('user/SET_AUTH', true)
  }
  
  // 如果没有token但状态显示已认证，清除认证状态
  if (!token && isAuthenticated) {
    store.commit('user/CLEAR_USER_DATA')
  }
  
  // 需要登录的页面
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!token) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  } 
  // 游客页面（已登录User不能访问）
  else if (to.matched.some(record => record.meta.guest)) {
    if (token) {
      next({ path: '/' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router 
