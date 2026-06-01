<template>
  <div class="graph-page">
    <div class="page-header">
      <div>
        <h2>文物知识图谱关系图</h2>
        <p>基于文物、博物馆、朝代、类型、材质等关系构建力导向图。</p>
      </div>

      <div class="graph-tools">
        <el-input
          v-model="keyword"
          placeholder="搜索文物 / 朝代 / 博物馆"
          clearable
          style="width: 280px"
          @keyup.enter="handleSearch"
        />

        <el-button type="primary" @click="handleSearch">
          搜索
        </el-button>

        <el-button @click="loadDefaultGraph">
          重置
        </el-button>
      </div>
    </div>

    <el-alert
      title="操作提示：鼠标悬停节点可查看信息；滚轮缩放；拖动节点调整布局；单击文物节点展开关联；双击文物节点进入详情页。"
      type="info"
      show-icon
      :closable="false"
      class="tip"
    />

    <div class="main-layout">
      <div ref="chartRef" class="graph-chart"></div>

      <el-card class="side-card">
        <template #header>
          <span>节点说明</span>
        </template>

        <div class="legend-item">
          <span class="dot artifact"></span> 文物
        </div>

        <div class="legend-item">
          <span class="dot museum"></span> 博物馆
        </div>

        <div class="legend-item">
          <span class="dot dynasty"></span> 朝代
        </div>

        <div class="legend-item">
          <span class="dot type"></span> 类型
        </div>

        <div class="legend-item">
          <span class="dot material"></span> 材质
        </div>

        <el-divider />

        <p class="summary">节点数：{{ graphData.nodes.length }}</p>
        <p class="summary">关系数：{{ graphData.links.length }}</p>
      </el-card>
    </div>

    <el-drawer
      v-model="drawerVisible"
      title="节点信息"
      size="360px"
    >
      <div v-if="selectedNode">
        <h3>{{ selectedNode.name }}</h3>
        <p class="node-type">类型：{{ getGroupText(normalizeGroup(selectedNode)) }}</p>

        <el-descriptions
          :column="1"
          border
          size="small"
        >
          <el-descriptions-item label="节点 ID">
            {{ selectedNode.id }}
          </el-descriptions-item>

          <el-descriptions-item label="节点标签">
            {{ selectedNode.label || selectedNode.group || '暂无' }}
          </el-descriptions-item>

          <el-descriptions-item label="节点名称">
            {{ selectedNode.name }}
          </el-descriptions-item>
        </el-descriptions>

        <el-button
          v-if="normalizeGroup(selectedNode) === 'artifact'"
          type="primary"
          style="margin-top: 16px"
          @click="goArtifactDetail(selectedNode)"
        >
          查看文物详情
        </el-button>

        <el-button
          v-if="normalizeGroup(selectedNode) === 'museum'"
          type="primary"
          style="margin-top: 16px"
          @click="expandMuseum(selectedNode)"
        >
          展开博物馆文物
        </el-button>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import {
  getArtifacts,
  getArtifactGraph,
  getMuseumGraph,
  searchGraph
} from '../api/mockService.js'
import { ElMessage } from 'element-plus'

const router = useRouter()

const chartRef = ref(null)
const keyword = ref('')
const drawerVisible = ref(false)
const selectedNode = ref(null)

const graphData = ref({
  nodes: [],
  links: []
})

let chart = null

const categoryList = [
  { name: '文物' },
  { name: '博物馆' },
  { name: '朝代' },
  { name: '类型' },
  { name: '材质' }
]

const categoryIndexMap = {
  artifact: 0,
  museum: 1,
  dynasty: 2,
  type: 3,
  material: 4
}

const sizeMap = {
  artifact: 48,
  museum: 58,
  dynasty: 52,
  type: 44,
  material: 42
}

const colorMap = {
  artifact: '#5470c6',
  museum: '#91cc75',
  dynasty: '#fac858',
  type: '#ee6666',
  material: '#73c0de'
}

const relationTextMap = {
  COLLECTED_BY: '收藏于',
  BELONGS_TO_DYNASTY: '所属朝代',
  HAS_TYPE: '文物类型',
  HAS_MATERIAL: '使用材质'
}

const getRelationText = (relation) => {
  return relationTextMap[relation] || relation || '关联'
}

const normalizeGroup = (node) => {
  // 后端图谱接口按照 API 文档返回 label 字段，前端根据 label / id 自动识别节点类型并恢复颜色。
  const label = String(node?.group || node?.label || '').toLowerCase()
  const id = String(node?.id || '')

  if (label === 'artifact' || id.startsWith('artifact_')) return 'artifact'
  if (label === 'museum' || id.startsWith('museum_')) return 'museum'
  if (label === 'dynasty' || id.startsWith('dynasty_')) return 'dynasty'
  if (label === 'type' || id.startsWith('type_')) return 'type'
  if (label === 'material' || id.startsWith('material_')) return 'material'

  return 'artifact'
}

const getGroupText = (group) => {
  const map = {
    artifact: '文物',
    museum: '博物馆',
    dynasty: '朝代',
    type: '类型',
    material: '材质'
  }

  return map[group] || group
}

const getArtifactIdFromNode = (node) => {
  const id = String(node?.id || '')

  if (id.startsWith('artifact_')) {
    return Number(id.replace('artifact_', ''))
  }

  if (id.startsWith('a')) {
    return Number(id.replace('a', ''))
  }

  return null
}

const getMuseumIdFromNode = (node) => {
  const id = String(node?.id || '')

  if (id.startsWith('museum_')) {
    return Number(id.replace('museum_', ''))
  }

  if (id.startsWith('m')) {
    return Number(id.replace('m', ''))
  }

  return null
}

const initChart = async () => {
  await nextTick()

  chart = echarts.init(chartRef.value)

  chart.on('click', async (params) => {
    if (params.dataType !== 'node') {
      return
    }

    const raw = params.data.raw
    selectedNode.value = raw
    drawerVisible.value = true

    const group = normalizeGroup(raw)

    if (group === 'artifact') {
      await expandArtifact(raw)
    }
  })

  chart.on('dblclick', (params) => {
    if (params.dataType !== 'node') {
      return
    }

    const raw = params.data.raw
    const group = normalizeGroup(raw)

    if (group === 'artifact') {
      goArtifactDetail(raw)
    }
  })

  window.addEventListener('resize', resizeChart)
}

const resizeChart = () => {
  if (chart) {
    chart.resize()
  }
}

const formatTooltip = (params) => {
  if (params.dataType === 'edge') {
    return `
      ${params.data.sourceName || params.data.source}
      →
      ${params.data.targetName || params.data.target}
      <br/>关系：${getRelationText(params.data.relation)}
    `
  }

  const raw = params.data.raw || {}
  const group = normalizeGroup(raw)

  return `
    <strong>${raw.name || ''}</strong><br/>
    类型：${getGroupText(group)}<br/>
    ID：${raw.id || ''}
  `
}

const renderGraph = () => {
  if (!chart) {
    return
  }

  const nodes = graphData.value.nodes.map((node) => {
    const group = normalizeGroup(node)

    return {
      id: node.id,
      name: node.name,
      raw: {
        ...node,
        group
      },
      category: categoryIndexMap[group] ?? 0,
      symbolSize: sizeMap[group] || 42,
      draggable: true,
      itemStyle: {
        color: colorMap[group] || '#999'
      },
      label: {
        show: true
      }
    }
  })

  const nodeNameMap = {}

  nodes.forEach((node) => {
    nodeNameMap[node.id] = node.name
  })

  const links = graphData.value.links.map((link) => {
    return {
      source: link.source,
      target: link.target,
      relation: link.relation,
      sourceName: nodeNameMap[link.source],
      targetName: nodeNameMap[link.target],
      label: {
        show: true,
        formatter: getRelationText(link.relation),
        fontSize: 11
      }
    }
  })

  chart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: formatTooltip
    },
    legend: [
      {
        data: categoryList.map((item) => item.name),
        top: 10
      }
    ],
    animationDurationUpdate: 500,
    series: [
      {
        type: 'graph',
        layout: 'force',
        categories: categoryList,
        data: nodes,
        links,
        roam: true,
        draggable: true,
        focusNodeAdjacency: true,
        label: {
          show: true,
          position: 'right',
          formatter: '{b}',
          fontSize: 12
        },
        edgeSymbol: ['none', 'arrow'],
        edgeSymbolSize: [0, 8],
        lineStyle: {
          width: 1.5,
          curveness: 0.15,
          opacity: 0.8
        },
        force: {
          repulsion: 260,
          gravity: 0.08,
          edgeLength: [90, 170]
        }
      }
    ]
  })
}

const mergeGraph = (newGraph) => {
  const nodeMap = {}
  const linkMap = {}

  graphData.value.nodes.forEach((node) => {
    nodeMap[node.id] = node
  })

  graphData.value.links.forEach((link) => {
    linkMap[`${link.source}-${link.target}-${link.relation}`] = link
  })

  ;(newGraph.nodes || []).forEach((node) => {
    nodeMap[node.id] = {
      ...nodeMap[node.id],
      ...node
    }
  })

  ;(newGraph.links || []).forEach((link) => {
    linkMap[`${link.source}-${link.target}-${link.relation}`] = link
  })

  graphData.value = {
    nodes: Object.values(nodeMap),
    links: Object.values(linkMap)
  }
}

const loadDefaultGraph = async () => {
  keyword.value = ''

  try {
    const artifactRes = await getArtifacts({
      page: 1,
      pageSize: 8
    })

    const records = artifactRes.data?.records || []

    graphData.value = {
      nodes: [],
      links: []
    }

    const graphResults = await Promise.all(
      records.map((item) => getArtifactGraph(item.id))
    )

    graphResults.forEach((res) => {
      if (res.data) {
        mergeGraph(res.data)
      }
    })

    renderGraph()
  } catch (error) {
    console.error(error)
    ElMessage.error('知识图谱加载失败，请检查后端服务是否启动')
  }
}

const handleSearch = async () => {
  const value = keyword.value.trim()

  if (!value) {
    await loadDefaultGraph()
    return
  }

  try {
    const res = await searchGraph({
      keyword: value
    })

    graphData.value = res.data || {
      nodes: [],
      links: []
    }

    renderGraph()

    if (!graphData.value.nodes.length) {
      ElMessage.warning('没有找到相关图谱节点')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('搜索失败，请检查后端服务是否启动')
  }
}

const expandArtifact = async (node) => {
  const artifactId = getArtifactIdFromNode(node)

  if (!artifactId) {
    return
  }

  const res = await getArtifactGraph(artifactId)

  if (res.data) {
    mergeGraph(res.data)
    renderGraph()
  }
}

const expandMuseum = async (node) => {
  const museumId = getMuseumIdFromNode(node)

  if (!museumId) {
    return
  }

  const res = await getMuseumGraph(museumId)

  if (res.data) {
    mergeGraph(res.data)
    renderGraph()
  }
}

const goArtifactDetail = (node) => {
  const artifactId = getArtifactIdFromNode(node)

  if (artifactId) {
    router.push(`/artifacts/${artifactId}`)
  }
}

onMounted(async () => {
  await initChart()
  await loadDefaultGraph()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)

  if (chart) {
    chart.dispose()
    chart = null
  }
})
</script>

<style scoped>
.graph-page {
  padding: 24px;
  background: #f5f7fb;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0;
  font-size: 26px;
  color: #1f2d3d;
}

.page-header p {
  margin: 8px 0 0;
  color: #606266;
}

.graph-tools {
  display: flex;
  gap: 10px;
}

.tip {
  margin-bottom: 16px;
}

.main-layout {
  display: grid;
  grid-template-columns: 1fr 260px;
  gap: 16px;
}

.graph-chart {
  height: 680px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
}

.side-card {
  height: fit-content;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  color: #303133;
}

.dot {
  width: 13px;
  height: 13px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 8px;
}

.dot.artifact {
  background: #5470c6;
}

.dot.museum {
  background: #91cc75;
}

.dot.dynasty {
  background: #fac858;
}

.dot.type {
  background: #ee6666;
}

.dot.material {
  background: #73c0de;
}

.summary {
  color: #606266;
  margin: 8px 0;
}


.node-type {
  color: #606266;
  margin-bottom: 16px;
}

@media screen and (max-width: 900px) {
  .page-header {
    display: block;
  }

  .graph-tools {
    margin-top: 16px;
    flex-wrap: wrap;
  }

  .main-layout {
    grid-template-columns: 1fr;
  }
}
</style>