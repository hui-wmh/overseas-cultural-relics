<template>
  <div class="timeline-page">
    <div class="page-header">
      <div>
        <h2>文物时间轴</h2>
        <p>按历史时期展示海外文物分布，支持朝代筛选和自定义时间段筛选。</p>
      </div>
    </div>

    <el-card class="filter-card">
      <el-form :inline="true">
        <el-form-item label="朝代">
          <el-select
            v-model="filter.dynastyId"
            placeholder="全部朝代"
            clearable
            style="width: 180px"
          >
            <el-option
              v-for="item in dynasties"
              :key="item.id"
              :label="item.nameZh"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="开始年份">
          <el-input-number
            v-model="filter.startYear"
            :min="-3000"
            :max="2100"
            placeholder="开始年份"
          />
        </el-form-item>

        <el-form-item label="结束年份">
          <el-input-number
            v-model="filter.endYear"
            :min="-3000"
            :max="2100"
            placeholder="结束年份"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="loadTimeline">
            筛选
          </el-button>

          <el-button @click="resetFilter">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <div class="content-layout">
      <el-card>
        <template #header>
          <span>各历史时期文物数量分布</span>
        </template>

        <div ref="chartRef" class="bar-chart"></div>
      </el-card>

      <el-card>
        <template #header>
          <span>历史时间轴</span>
        </template>

        <el-empty
          v-if="timelineList.length === 0"
          description="暂无符合条件的文物"
        />

        <el-timeline v-else>
          <el-timeline-item
            v-for="item in timelineList"
            :key="item.dynastyId"
            :timestamp="formatYearRange(item.startYear, item.endYear)"
            placement="top"
          >
            <div class="timeline-item" @click="goArtifactList(item)">
              <div class="timeline-title">
                <h3>{{ item.dynastyName }}</h3>
                <el-tag type="success">
                  {{ item.count }} 件文物
                </el-tag>
              </div>

              <p class="timeline-desc">
                {{ item.dynastyName }}时期共有 {{ item.count }} 件代表性海外文物。
                点击该时间节点可进入对应文物列表。
              </p>

              <div class="artifact-list">
                <div
                  v-for="artifact in item.artifacts"
                  :key="artifact.id"
                  class="artifact-card"
                  @click.stop="goArtifactDetail(artifact.id)"
                >
                  <img
                    :src="artifact.imageUrl"
                    :alt="artifact.titleZh"
                    @error="handleImageError($event, artifact.id)"
                  />

                  <div>
                    <h4>{{ artifact.titleZh }}</h4>
                    <p>{{ artifact.typeName || '未知类型' }}</p>
                    <p>{{ artifact.museumName || '未知博物馆' }}</p>
                  </div>
                </div>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import {
  getArtifacts,
  getDynasties
} from '../api/mockService.js'
import { ElMessage } from 'element-plus'

const router = useRouter()

const chartRef = ref(null)
let chart = null

const dynasties = ref([])
const allArtifacts = ref([])
const timelineList = ref([])

const filter = reactive({
  dynastyId: null,
  startYear: null,
  endYear: null
})

const formatYear = (year) => {
  if (year < 0) {
    return `公元前${Math.abs(year)}年`
  }

  return `公元${year}年`
}

const formatYearRange = (start, end) => {
  return `${formatYear(start)} - ${formatYear(end)}`
}

const initChart = async () => {
  await nextTick()

  chart = echarts.init(chartRef.value)

  chart.on('click', (params) => {
    const item = timelineList.value[params.dataIndex]

    if (item) {
      goArtifactList(item)
    }
  })

  window.addEventListener('resize', resizeChart)
}

const resizeChart = () => {
  if (chart) {
    chart.resize()
  }
}

const renderChart = () => {
  if (!chart) {
    return
  }

  const names = timelineList.value.map((item) => item.dynastyName)
  const counts = timelineList.value.map((item) => item.count)

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const item = timelineList.value[params[0].dataIndex]

        return `
          ${item.dynastyName}<br/>
          时间：${formatYearRange(item.startYear, item.endYear)}<br/>
          文物数量：${item.count}
        `
      }
    },
    grid: {
      left: 40,
      right: 20,
      top: 30,
      bottom: 40
    },
    xAxis: {
      type: 'category',
      data: names,
      axisLabel: {
        interval: 0
      }
    },
    yAxis: {
      type: 'value',
      minInterval: 1
    },
    series: [
      {
        name: '文物数量',
        type: 'bar',
        data: counts,
        barWidth: 36
      }
    ]
  })
}

const loadBaseData = async () => {
  const dynastyRes = await getDynasties()

  const artifactRes = await getArtifacts({
    page: 1,
    pageSize: 100
  })

  dynasties.value = dynastyRes.data || []
  allArtifacts.value = artifactRes.data?.records || []
}

const loadTimeline = async () => {
  // 时间轴不新增后端接口，使用 /api/artifacts 和 /api/dynasties 的数据在前端组合生成。
  let result = dynasties.value.map((dynasty) => {
    const matchedArtifacts = allArtifacts.value.filter((artifact) => {
      return artifact.dynastyName === dynasty.nameZh
    })

    return {
      dynastyId: dynasty.id,
      dynastyName: dynasty.nameZh,
      dynastyNameEn: dynasty.nameEn,
      startYear: dynasty.startYear,
      endYear: dynasty.endYear,
      count: matchedArtifacts.length,
      artifacts: matchedArtifacts
    }
  })

  if (filter.dynastyId) {
    result = result.filter((item) => item.dynastyId === filter.dynastyId)
  }

  if (filter.startYear !== null && filter.startYear !== undefined) {
    result = result.filter((item) => item.endYear >= filter.startYear)
  }

  if (filter.endYear !== null && filter.endYear !== undefined) {
    result = result.filter((item) => item.startYear <= filter.endYear)
  }

  timelineList.value = result.filter((item) => item.count > 0)

  renderChart()
}

const resetFilter = async () => {
  filter.dynastyId = null
  filter.startYear = null
  filter.endYear = null

  await loadTimeline()
}

const goArtifactList = (item) => {
  router.push({
    path: '/artifacts',
    query: {
      dynastyId: item.dynastyId
    }
  })
}

const goArtifactDetail = (id) => {
  router.push(`/artifacts/${id}`)
}

const handleImageError = (event, id) => {
  event.target.src = `https://picsum.photos/400/300?random=${id}`
}

onMounted(async () => {
  try {
    await loadBaseData()
    await initChart()
    await loadTimeline()
  } catch (error) {
    console.error(error)
    ElMessage.error('时间轴加载失败，请检查后端服务是否启动')
  }
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
.timeline-page {
  padding: 24px;
  background: #f5f7fb;
  min-height: 100vh;
}

.page-header {
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

.filter-card {
  margin-bottom: 16px;
}

.content-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.bar-chart {
  width: 100%;
  height: 360px;
}

.timeline-item {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.timeline-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
}

.timeline-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.timeline-title h3 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.timeline-desc {
  color: #606266;
  margin: 10px 0 14px;
}

.artifact-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

.artifact-card {
  display: flex;
  gap: 10px;
  background: #f8fafc;
  border-radius: 10px;
  padding: 10px;
  cursor: pointer;
}

.artifact-card:hover {
  background: #eef5ff;
}

.artifact-card img {
  width: 70px;
  height: 58px;
  border-radius: 8px;
  object-fit: cover;
}

.artifact-card h4 {
  margin: 0 0 6px;
  color: #303133;
}

.artifact-card p {
  margin: 2px 0;
  color: #606266;
  font-size: 13px;
}
</style>