<template>
  <div class="artifacts-page">
  <div class="page-header">
    <div class="page-header-text">
      <h2>文物浏览</h2>
      <p>支持列表/卡片视图切换，并可按名称、年代、类型、博物馆、材质等条件筛选。</p>
    </div>

    <div class="view-switch">
      <el-button-group>
        <el-button
          :type="viewMode === 'card' ? 'primary' : 'default'"
          @click="viewMode = 'card'"
        >
          卡片视图
        </el-button>
        <el-button
          :type="viewMode === 'list' ? 'primary' : 'default'"
          @click="viewMode = 'list'"
        >
          列表视图
        </el-button>
      </el-button-group>
    </div>
  </div>

    <el-card class="filter-card">
      <el-form :inline="true">
        <el-form-item label="关键词">
          <el-input
            v-model="filter.keyword"
            placeholder="请输入文物关键词"
            clearable
            style="width: 220px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item label="朝代">
          <el-select
            v-model="filter.dynastyId"
            placeholder="全部朝代"
            clearable
            style="width: 150px"
            @change="handleSearch"
          >
            <el-option
              v-for="item in dynasties"
              :key="item.id"
              :label="item.nameZh"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="类型">
          <el-select
            v-model="filter.typeId"
            placeholder="全部类型"
            clearable
            style="width: 150px"
            @change="handleSearch"
          >
            <el-option
              v-for="item in types"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="博物馆">
          <el-select
            v-model="filter.museumId"
            placeholder="全部博物馆"
            clearable
            style="width: 170px"
            @change="handleSearch"
          >
            <el-option
              v-for="item in museums"
              :key="item.id"
              :label="item.nameZh"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="材质">
          <el-select
            v-model="filter.materialId"
            placeholder="全部材质"
            clearable
            style="width: 150px"
            @change="handleSearch"
          >
            <el-option
              v-for="item in materials"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="排序">
          <el-select
            v-model="filter.sortBy"
            placeholder="默认排序"
            clearable
            style="width: 150px"
            @change="handleSearch"
          >
            <el-option label="按名称排序" value="name" />
            <el-option label="按年代排序" value="dynasty" />
            <el-option label="按更新时间" value="date" />
            <el-option label="按博物馆排序" value="museum" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button @click="advancedVisible = !advancedVisible">
            {{ advancedVisible ? '收起高级查询' : '高级查询' }}
          </el-button>
        </el-form-item>

        <template v-if="advancedVisible">
          <el-form-item label="年代范围">
            <el-input-number
              v-model="filter.yearStart"
              :min="-3000"
              :max="2026"
              placeholder="起始年"
              controls-position="right"
              style="width: 130px"
            />
            <span class="range-separator">至</span>
            <el-input-number
              v-model="filter.yearEnd"
              :min="-3000"
              :max="2026"
              placeholder="结束年"
              controls-position="right"
              style="width: 130px"
            />
          </el-form-item>
        </template>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            搜索
          </el-button>

          <el-button @click="resetFilter">
            重置
          </el-button>

          <el-button type="success" @click="handleExport">
            导出结果
          </el-button>

          <el-button
            type="warning"
            :disabled="selectedArtifactIds.length < 2"
            @click="openCompare"
          >
            对比已选 {{ selectedArtifactIds.length }} 个
          </el-button>

          <el-button
            v-if="selectedArtifactIds.length"
            @click="clearSelected"
          >
            清空选择
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-empty
      v-if="artifacts.length === 0"
      description="暂无符合条件的文物"
      style="margin-top: 80px"
    />

  <template v-else>
    <!-- 卡片视图 -->
    <div v-if="viewMode === 'card'" class="artifact-grid">
      <el-card
        v-for="item in artifacts"
        :key="item.id"
        class="artifact-card"
        shadow="hover"
        @click="goDetail(item.id)"
      >
        <el-checkbox
          class="compare-checkbox"
          :model-value="isSelected(item.id)"
          @click.stop
          @change="checked => toggleCompareSelection(item, checked)"
        >
          对比
        </el-checkbox>

        <img
          :src="item.imageUrl"
          :alt="item.titleZh"
          class="artifact-img"
          @error="handleImageError($event, item.id)"
        />

        <div class="artifact-info">
          <h3>{{ item.titleZh }}</h3>
          <p class="title-en">{{ item.title }}</p>

          <div class="meta">
            <el-tag size="small" type="success">
              {{ item.dynastyName || '未知朝代' }}
            </el-tag>
            <el-tag size="small" type="warning">
              {{ item.typeName || '未知类型' }}
            </el-tag>
            <el-tag size="small">
              {{ item.materialName || '未知材质' }}
            </el-tag>
          </div>

          <p class="museum">{{ item.museumName }}</p>
        </div>
      </el-card>
    </div>

<div v-else class="artifact-table-wrapper">
  <el-table
    :data="artifacts"
    class="artifact-table"
    style="width: 100%"
    :row-style="{ cursor: 'pointer' }"
    @row-click="row => goDetail(row.id)"
    >
        <el-table-column label="对比" width="80">
          <template #default="{ row }">
            <el-checkbox
              :model-value="isSelected(row.id)"
              @click.stop
              @change="checked => toggleCompareSelection(row, checked)"
            />
          </template>
        </el-table-column>

        <el-table-column label="文物名称" min-width="220">
          <template #default="{ row }">
            <div class="list-title-cell">
              <img
                :src="row.imageUrl"
                :alt="row.titleZh"
                class="list-thumb"
                @error="handleImageError($event, row.id)"
              />
              <div>
                <div class="list-title">{{ row.titleZh }}</div>
                <div class="list-subtitle">{{ row.title }}</div>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="dynastyName" label="朝代" width="100" />
        <el-table-column prop="typeName" label="类型" width="100" />
        <el-table-column prop="materialName" label="材质" width="100" />
        <el-table-column prop="museumName" label="所属博物馆" min-width="170" />
        <el-table-column prop="location" label="收藏地" min-width="130" />
        <el-table-column prop="crawlDate" label="更新时间" width="120" />

        <el-table-column label="操作" width="90">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              text
              @click.stop="goDetail(row.id)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </template>

    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="filter.page"
        v-model:page-size="filter.pageSize"
        :page-sizes="[8, 12, 20, 40]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="loadArtifacts"
        @current-change="loadArtifacts"
      />
    </div>

    <el-drawer
      v-model="compareVisible"
      title="文物横向对比"
      size="70%"
    >
      <el-alert
        title="仅展示所选文物之间存在差异的属性"
        type="info"
        show-icon
        :closable="false"
        style="margin-bottom: 16px"
      />

      <el-table
        v-if="diffRows.length"
        :data="diffRows"
        border
        style="width: 100%"
      >
        <el-table-column prop="label" label="属性" width="140" />

        <el-table-column
          v-for="item in compareItems"
          :key="item.id"
          :label="item.titleZh"
          min-width="180"
        >
          <template #default="{ row }">
            {{ item[row.key] || '暂无' }}
          </template>
        </el-table-column>
      </el-table>

      <el-empty
        v-else
        description="所选文物在当前对比字段中暂无明显差异"
      />
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getArtifacts,
  getArtifactDetail,
  exportArtifacts,
  getDynasties,
  getArtifactTypes,
  getMuseums,
  getMaterials
} from '../api/mockService.js'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const artifacts = ref([])
const total = ref(0)

const viewMode = ref('card')
const advancedVisible = ref(false)

const dynasties = ref([])
const types = ref([])
const museums = ref([])
const materials = ref([])

const selectedArtifactIds = ref([])
const compareVisible = ref(false)
const compareItems = ref([])

const filter = ref({
  page: 1,
  pageSize: 12,
  keyword: '',
  dynastyId: null,
  typeId: null,
  museumId: null,
  materialId: null,
  sortBy: '',
  yearStart: null,
  yearEnd: null
})

const compareFields = [
  { key: 'dynastyName', label: '朝代' },
  { key: 'typeName', label: '文物类型' },
  { key: 'materialName', label: '材质' },
  { key: 'period', label: '年代' },
  { key: 'artistName', label: '作者' },
  { key: 'museumName', label: '收藏博物馆' },
  { key: 'location', label: '收藏地点' },
  { key: 'dimensions', label: '尺寸' },
  { key: 'accessionNumber', label: '馆藏编号' }
]

const diffRows = computed(() => {
  return compareFields.filter((field) => {
    const values = compareItems.value.map((item) => item[field.key] || '暂无')
    return new Set(values).size > 1
  })
})

const buildParams = () => {
  const params = {
    page: filter.value.page,
    pageSize: filter.value.pageSize
  }

  const appendParam = (key) => {
    const value = filter.value[key]
    if (value !== null && value !== undefined && value !== '') {
      params[key] = value
    }
  }

  appendParam('keyword')
  appendParam('dynastyId')
  appendParam('typeId')
  appendParam('museumId')
  appendParam('materialId')
  appendParam('sortBy')
  appendParam('yearStart')
  appendParam('yearEnd')

  return params
}

const buildExportParams = () => {
  const params = buildParams()
  delete params.page
  delete params.pageSize
  return params
}

const loadArtifacts = async () => {
  try {
    const res = await getArtifacts(buildParams())

    artifacts.value = res.data?.records || []
    total.value = res.data?.total || 0
  } catch (error) {
    console.error(error)
    ElMessage.error('文物列表加载失败，请检查后端服务是否启动')
  }
}

const loadDictionaries = async () => {
  const dynastyRes = await getDynasties()
  const typeRes = await getArtifactTypes()
  const museumRes = await getMuseums({
    page: 1,
    pageSize: 100
  })
  const materialRes = await getMaterials()

  dynasties.value = dynastyRes.data || []
  types.value = typeRes.data || []
  museums.value = museumRes.data?.records || museumRes.data || []
  materials.value = materialRes.data || []
}

const handleSearch = async () => {
  filter.value.page = 1
  clearSelected()
  await loadArtifacts()
}

const resetFilter = async () => {
  filter.value = {
    page: 1,
    pageSize: 12,
    keyword: '',
    dynastyId: null,
    typeId: null,
    museumId: null,
    materialId: null,
    sortBy: '',
    yearStart: null,
    yearEnd: null
  }

  clearSelected()
  await loadArtifacts()
}

const isSelected = (id) => {
  return selectedArtifactIds.value.includes(id)
}

const toggleCompareSelection = (item, checked) => {
  if (checked) {
    if (selectedArtifactIds.value.length >= 3) {
      ElMessage.warning('最多只能选择 3 个文物进行对比')
      return
    }

    selectedArtifactIds.value.push(item.id)
    return
  }

  selectedArtifactIds.value = selectedArtifactIds.value.filter((id) => {
    return id !== item.id
  })
}

const clearSelected = () => {
  selectedArtifactIds.value = []
  compareItems.value = []
}

const openCompare = async () => {
  if (selectedArtifactIds.value.length < 2) {
    ElMessage.warning('请至少选择 2 个文物进行对比')
    return
  }

  const resList = await Promise.all(
    selectedArtifactIds.value.map((id) => getArtifactDetail(id))
  )

  compareItems.value = resList.map((res) => res.data).filter(Boolean)
  compareVisible.value = true
}

const escapeCsvValue = (value) => {
  const text = value === null || value === undefined ? '' : String(value)
  return `"${text.replace(/"/g, '""')}"`
}

const handleExport = async () => {
  const res = await exportArtifacts(buildExportParams())
  const records = res.data || []

  if (!records.length) {
    ElMessage.warning('当前查询条件下暂无可导出的文物')
    return
  }

  const columns = [
    { key: 'id', label: 'ID' },
    { key: 'titleZh', label: '中文名称' },
    { key: 'title', label: '英文名称' },
    { key: 'dynastyName', label: '朝代' },
    { key: 'typeName', label: '类型' },
    { key: 'materialName', label: '材质' },
    { key: 'period', label: '年代' },
    { key: 'artistName', label: '作者' },
    { key: 'museumName', label: '收藏博物馆' },
    { key: 'location', label: '收藏地点' },
    { key: 'dimensions', label: '尺寸' },
    { key: 'accessionNumber', label: '馆藏编号' },
    { key: 'detailUrl', label: '来源链接' }
  ]

  const header = columns.map((column) => escapeCsvValue(column.label)).join(',')
  const rows = records.map((item) => {
    return columns.map((column) => escapeCsvValue(item[column.key])).join(',')
  })

  const csvContent = [header, ...rows].join('\n')
  const blob = new Blob(['\uFEFF' + csvContent], {
    type: 'text/csv;charset=utf-8;'
  })

  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  const date = new Date().toISOString().slice(0, 10)

  link.href = url
  link.download = `文物查询结果_${date}.csv`
  link.click()

  URL.revokeObjectURL(url)
  ElMessage.success('导出成功')
}

const goDetail = (id) => {
  router.push(`/artifacts/${id}`)
}

const handleImageError = (event, id) => {
  event.target.src = `https://picsum.photos/400/300?random=${id}`
}

onMounted(async () => {
  if (route.query.dynastyId) {
    filter.value.dynastyId = Number(route.query.dynastyId)
  }

  if (route.query.museumId) {
    filter.value.museumId = Number(route.query.museumId)
  }

  await loadDictionaries()
  await loadArtifacts()
})
</script>

<style scoped>
.artifacts-page {
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
  margin-bottom: 20px;
}

.artifact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 18px;
}

.artifact-card {
  position: relative;
  cursor: pointer;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;
}

.artifact-card:hover {
  transform: translateY(-3px);
}

.compare-checkbox {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 2;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.92);
  border-radius: 6px;
}

.artifact-img {
  width: 100%;
  height: 190px;
  object-fit: cover;
  border-radius: 8px;
}

.artifact-info {
  padding-top: 12px;
}

.artifact-info h3 {
  margin: 0 0 6px;
  font-size: 18px;
  color: #303133;
}

.title-en {
  margin: 0 0 10px;
  color: #909399;
  font-size: 13px;
  min-height: 18px;
}

.meta {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}

.museum {
  color: #606266;
  font-size: 14px;
  margin: 0;
}

.pagination-wrapper {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

.page-header {
  position: relative;
  margin-bottom: 24px;
}

.page-header-text {
  text-align: center;
}

.page-header-text h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.page-header-text p {
  margin: 12px auto 0;
  max-width: 900px;
  text-align: center;
  color: #606266;
  line-height: 1.8;
}

.view-switch {
  position: absolute;
  right: 0;
  top: 0;
}

.range-separator {
  margin: 0 8px;
  color: #909399;
}

.artifact-table {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
}

.list-title-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.list-thumb {
  width: 52px;
  height: 52px;
  object-fit: cover;
  border-radius: 8px;
  flex-shrink: 0;
}

.list-title {
  font-weight: 600;
  color: #303133;
}

.list-subtitle {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.artifact-table-wrapper {
  width: 100%;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-sizing: border-box;
}

.artifact-table {
  width: 100%;
}

</style>