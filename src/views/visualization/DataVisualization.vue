<template>
  <div class="visualization-container">
    <div class="element-visualization">
      <div class="element-header">
        <h2>Statistical Analysis of Alloying Elements</h2>
        <el-radio-group v-model="elementStatMode" size="small" @change="updateElementChart">
          <el-radio-button label="count">Occurrence Frequency</el-radio-button>
          <el-radio-button label="sum">Total Content</el-radio-button>
        </el-radio-group>
      </div>
      <div ref="elementChartRef" class="element-chart"></div>
    </div>

    <div class="hardness-visualization">
      <div class="element-header">
        <h2>Hardness Distribution of Alloys at Room Temperature</h2>
      </div>
      <div ref="hardnessScatterChartRef" class="hardness-scatter-chart"></div>
    </div>

    <div class="strength-ductility-visualization">
      <div class="element-header">
        <h2>Strength-Ductility Distribution of As-Cast Alloys at Room Temperature</h2>
      </div>
      <div ref="strengthDuctilityChartRef" class="strength-ductility-chart"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { getMaterials } from '@/api/material'
import { getRoomTempProperties } from '@/api/roomTempProperty'

const elementStatMode = ref('count')
const elementChartRef = ref(null)
const hardnessScatterChartRef = ref(null)
const strengthDuctilityChartRef = ref(null)
const elementStats = ref({ count: {}, sum: {} })
const roomTempScatterRows = ref([])
let elementChart = null
let hardnessScatterChart = null
let strengthDuctilityChart = null

const ELEMENTS = [
  'Al', 'C', 'Co', 'Cr', 'Cu', 'Fe', 'Hf', 'Mg', 'Mn', 'Mo', 'N', 'Nb',
  'Ni', 'Sc', 'Si', 'Sn', 'Ta', 'Ti', 'V', 'W', 'Y', 'Zn', 'Zr'
]

const parseMaterialRows = (response) => {
  if (!response || !response.data) return []
  const payload = response.data
  if (Array.isArray(payload)) return payload
  if (Array.isArray(payload.results)) return payload.results
  return []
}

const parseRoomTempRows = (response) => {
  if (!response) return []
  if (response.data) {
    if (Array.isArray(response.data)) return response.data
    if (Array.isArray(response.data.results)) return response.data.results
  }
  if (Array.isArray(response.results)) return response.results
  return []
}

const parseHardnessValue = (value) => {
  if (typeof value === 'number') {
    return Number.isFinite(value) ? value : null
  }
  if (typeof value !== 'string') return null
  const normalized = value.replace(/,/g, '').trim()
  if (!normalized) return null
  const matched = normalized.match(/-?\d+(\.\d+)?/)
  if (!matched) return null
  const parsed = Number(matched[0])
  return Number.isFinite(parsed) ? parsed : null
}

const parseNumericValue = (value) => {
  if (typeof value === 'number') return Number.isFinite(value) ? value : null
  if (typeof value !== 'string') return null
  const normalized = value.replace(/,/g, '').trim()
  if (!normalized) return null
  const matched = normalized.match(/-?\d+(\.\d+)?/)
  if (!matched) return null
  const parsed = Number(matched[0])
  return Number.isFinite(parsed) ? parsed : null
}

const updateElementChart = () => {
  if (!elementChartRef.value) return
  if (!elementChart) elementChart = echarts.init(elementChartRef.value)

  const mode = elementStatMode.value
  const currentStats = elementStats.value[mode] || {}
  const isCount = mode === 'count'

  elementChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 74, right: 24, top: 36, bottom: 72 },
    xAxis: { type: 'category', data: ELEMENTS, axisLabel: { rotate: 35 } },
    yAxis: {
      type: 'value',
      name: isCount ? 'Occurrence Frequency' : 'Total Content(%)',
      nameLocation: 'middle',
      nameGap: 56,
      nameTextStyle: { align: 'center', fontSize: 14 },
      minInterval: isCount ? 1 : 0
    },
    series: [{
      name: isCount ? 'Occurrence Frequency' : 'Total Content(%)',
      type: 'bar',
      barWidth: '55%',
      data: ELEMENTS.map((e) => {
        const v = Number(currentStats[e] || 0)
        return isCount ? v : Number(v.toFixed(2))
      }),
      itemStyle: { color: '#409EFF' }
    }]
  }, true)
}

const normalizePhaseStructure = (phaseStructure) => {
  const value = String(phaseStructure || '').trim().replace(/\s+/g, ' ')
  return value || 'Unknown Phase Structure'
}

const getDominantElementCluster = (row) => {
  const material = row?.material || {}
  let dominantElement = 'Unknown Composition Cluster'
  let maxValue = Number.NEGATIVE_INFINITY
  ELEMENTS.forEach((element) => {
    const key = `composition_${element.toLowerCase()}`
    const value = Number(material?.[key])
    if (!Number.isNaN(value) && value > maxValue) {
      maxValue = value
      dominantElement = `${element}-Dominant Cluster`
    }
  })
  return dominantElement
}

const updateHardnessScatterChart = () => {
  if (!hardnessScatterChartRef.value) return
  if (!hardnessScatterChart) hardnessScatterChart = echarts.init(hardnessScatterChartRef.value)

  const points = (roomTempScatterRows.value || [])
    .map((row) => {
      const hardness = parseHardnessValue(row?.hardness_value)
      if (hardness === null) return null
      return {
        cluster: getDominantElementCluster(row),
        phase: normalizePhaseStructure(row?.phase_structure),
        hardness,
        row
      }
    })
    .filter(Boolean)

  if (!points.length) {
    hardnessScatterChart.setOption({
      title: { text: 'No hardness data available', left: 'center', top: 'middle', textStyle: { color: '#909399', fontSize: 14 } },
      xAxis: { type: 'category', data: [] },
      yAxis: { type: 'value', name: 'Hardness(HV)' },
      series: []
    }, true)
    return
  }

  const phaseSymbols = ['circle', 'rect', 'triangle', 'diamond', 'pin', 'roundRect']
  const phaseColors = [
    '#5470C6', '#91CC75', '#FAC858', '#EE6666', '#73C0DE', '#3BA272',
    '#FC8452', '#9A60B4', '#EA7CCC', '#2F4554', '#61A0A8', '#D48265'
  ]
  const phaseToSymbol = {}
  const phaseToColor = {}
  let phaseIdx = 0
  points.forEach((item) => {
    if (!phaseToSymbol[item.phase]) {
      phaseToSymbol[item.phase] = phaseSymbols[phaseIdx % phaseSymbols.length]
      phaseToColor[item.phase] = phaseColors[phaseIdx % phaseColors.length]
      phaseIdx += 1
    }
  })

  const seriesByPhase = Object.keys(phaseToSymbol).map((phase) => ({
    name: phase,
    type: 'scatter',
    encode: { x: 0, y: 1, value: 2 },
    symbol: phaseToSymbol[phase],
    itemStyle: { color: phaseToColor[phase] },
    symbolSize: 11,
    data: points
      .filter((item) => item.phase === phase)
      .map((item) => [
        Number(item.hardness.toFixed(2)),
        Number(item.hardness.toFixed(2)),
        Number(item.hardness.toFixed(2)),
        item.cluster,
        item.row?.material?.material_id || item.row?.material_id || '-',
        item.row?.rtproperty_id || '-'
      ])
  }))

  hardnessScatterChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const [xHardness, yHardness, , cluster, materialId, rtpropertyId] = params.value || []
        return [
          `Composition Cluster: ${cluster}`,
          `X-Axis Hardness (HV): ${xHardness}`,
          `Y-Axis Hardness (HV): ${yHardness}`,
          `Phase Structure: ${params.seriesName}`,
          `Material ID: ${materialId}`,
          `Record ID: ${rtpropertyId}`
        ].join('<br/>')
      }
    },
    legend: { top: 10, type: 'scroll' },
    grid: { left: 90, right: 80, top: 56, bottom: 98 },
    xAxis: {
      type: 'value',
      name: 'Hardness(HV)',
      nameLocation: 'middle',
      nameGap: 38,
      nameTextStyle: { align: 'center', fontSize: 14 }
    },
    yAxis: {
      type: 'value',
      name: 'Hardness(HV)',
      nameLocation: 'middle',
      nameGap: 62,
      nameTextStyle: { align: 'center', fontSize: 14 }
    },
    series: seriesByPhase
  }, true)
}

const updateStrengthDuctilityChart = () => {
  if (!strengthDuctilityChartRef.value) return
  if (!strengthDuctilityChart) strengthDuctilityChart = echarts.init(strengthDuctilityChartRef.value)

  const bubbleData = (roomTempScatterRows.value || [])
    .map((row) => {
      const ys = parseNumericValue(row?.yield_strength_t)
      const uts = parseNumericValue(row?.ultimate_strength_t)
      const te = parseNumericValue(row?.total_elongation ?? row?.te ?? row?.fracture_strain_t)
      if (ys === null || uts === null || te === null) return null
      return {
        ys,
        uts,
        te,
        materialId: row?.material?.material_id || row?.material_id || '-',
        rtpropertyId: row?.rtproperty_id || '-',
        phase: normalizePhaseStructure(row?.phase_structure)
      }
    })
    .filter(Boolean)

  if (!bubbleData.length) {
    strengthDuctilityChart.setOption({
      title: { text: 'No complete YS/UTS/TE data available', left: 'center', top: 'middle', textStyle: { color: '#909399', fontSize: 14 } },
      xAxis: { type: 'value', name: 'Total Elongation TE(%)' },
      yAxis: { type: 'value', name: 'Tensile Strength UTS(MPa)' },
      series: []
    }, true)
    return
  }

  const ysValues = bubbleData.map((item) => item.ys)
  const ysMin = Math.min(...ysValues)
  const ysMax = Math.max(...ysValues)
  const toSymbolSize = (ys) => {
    if (ysMin === ysMax) return 14
    return 8 + ((ys - ysMin) / (ysMax - ysMin)) * 14
  }

  strengthDuctilityChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const [te, uts, ys, materialId, rtpropertyId, phase] = params.value || []
        return [
          `Material ID: ${materialId}`,
          `Record ID: ${rtpropertyId}`,
          `Phase Structure: ${phase}`,
          `TE(%): ${te}`,
          `UTS(MPa): ${uts}`,
          `YS(MPa): ${ys}`
        ].join('<br/>')
      }
    },
    grid: { left: 96, right: 30, top: 36, bottom: 96 },
    xAxis: {
      type: 'value',
      name: 'Total Elongation TE(%)',
      nameLocation: 'middle',
      nameGap: 42,
      nameTextStyle: { align: 'center', fontSize: 14 }
    },
    yAxis: {
      type: 'value',
      name: 'Tensile Strength UTS(MPa)',
      nameLocation: 'middle',
      nameGap: 72,
      nameTextStyle: { align: 'center', fontSize: 14 }
    },
    series: [{
      name: 'As-Cast Alloys',
      type: 'scatter',
      data: bubbleData.map((item) => [
        Number(item.te.toFixed(3)),
        Number(item.uts.toFixed(3)),
        Number(item.ys.toFixed(3)),
        item.materialId,
        item.rtpropertyId,
        item.phase
      ]),
      symbolSize: (value) => toSymbolSize(value[2]),
      itemStyle: { color: '#409EFF', opacity: 0.8 }
    }]
  }, true)
}

const fetchElementDistribution = async () => {
  const counts = Object.fromEntries(ELEMENTS.map((e) => [e, 0]))
  const sums = Object.fromEntries(ELEMENTS.map((e) => [e, 0]))
  const pageSize = 500
  let page = 1
  let fetched = 0
  let totalCount = null
  let hasMore = true

  while (hasMore) {
    const response = await getMaterials({ page, page_size: pageSize })
    const rows = parseMaterialRows(response)
    const payload = response?.data

    if (totalCount === null && payload && !Array.isArray(payload) && payload.count !== undefined) {
      totalCount = Number(payload.count) || 0
    }
    if (!rows.length) {
      hasMore = false
      continue
    }

    rows.forEach((row) => {
      ELEMENTS.forEach((element) => {
        const key = `composition_${element.toLowerCase()}`
        const value = parseFloat(row?.[key])
        if (!Number.isNaN(value) && value > 0) {
          counts[element] += 1
          sums[element] += value
        }
      })
    })

    fetched += rows.length
    if (Array.isArray(payload) || rows.length < pageSize || (totalCount !== null && fetched >= totalCount)) {
      hasMore = false
    } else {
      page += 1
    }
  }

  elementStats.value = { count: counts, sum: sums }
  updateElementChart()
}

const fetchRoomTempHardnessScatter = async () => {
  const pageSize = 100
  let page = 1
  let fetched = 0
  let totalCount = null
  const collected = []
  let hasMore = true

  while (hasMore) {
    const response = await getRoomTempProperties({ page, page_size: pageSize })
    const rows = parseRoomTempRows(response)
    const payload = response?.data || response

    if (totalCount === null && payload && !Array.isArray(payload) && payload.count !== undefined) {
      totalCount = Number(payload.count) || 0
    }
    if (!rows.length) {
      hasMore = false
      continue
    }

    collected.push(...rows)
    fetched += rows.length

    const hasNext = Boolean(payload?.next)
    if ((totalCount !== null && fetched >= totalCount) || (!hasNext && totalCount === null)) {
      hasMore = false
    } else {
      page += 1
    }
  }

  roomTempScatterRows.value = collected
  updateHardnessScatterChart()
  updateStrengthDuctilityChart()
}

onMounted(async () => {
  await fetchElementDistribution()
  await fetchRoomTempHardnessScatter()
})
</script>

<style scoped>
.visualization-container {
  width: 80%;
  margin: 0 auto;
  padding: 20px 0;
}

.element-visualization,
.hardness-visualization {
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

h2 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.element-chart {
  width: 100%;
  height: 360px;
}

.hardness-scatter-chart {
  width: 100%;
  height: 420px;
}

.strength-ductility-visualization {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 24px;
  margin-bottom: 24px;
}

.strength-ductility-chart {
  width: 100%;
  height: 420px;
}
</style>
