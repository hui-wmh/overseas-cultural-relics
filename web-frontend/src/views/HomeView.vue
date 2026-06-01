<template>
  <div class="home-page">
    <!-- 顶部搜索区域 -->
    <section class="hero-section">
      <h1>海外藏中国文物知识服务平台</h1>
      <p>探索散落在世界各地的中华文明瑰宝</p>

      <div class="search-box">
        <el-input
          v-model="keyword"
          placeholder="搜索文物名称、朝代、类型..."
          clearable
          @keyup.enter="handleSearch"
        />
        <el-button @click="handleSearch">搜索</el-button>
      </div>
    </section>

    <!-- 统计卡片 -->
    <section class="stats-section">
      <el-card class="stat-card">
        <div class="stat-number">{{ artifactTotal }}</div>
        <div class="stat-label">件文物</div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-number">{{ museumTotal }}</div>
        <div class="stat-label">家博物馆</div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-number">{{ dynastyTotal }}</div>
        <div class="stat-label">个朝代</div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-number">{{ countryTotal }}</div>
        <div class="stat-label">个国家</div>
      </el-card>
    </section>

    <!-- 精选文物 -->
    <section class="featured-section">
      <h2>精选文物</h2>

      <el-empty
        v-if="artifacts.length === 0"
        description="暂无文物数据"
        style="margin-top: 40px"
      />

      <div v-else class="artifact-grid">
        <el-card
          v-for="item in artifacts"
          :key="item.id"
          class="artifact-card"
          shadow="hover"
          @click="goDetail(item.id)"
        >
          <img
            :src="item.imageUrl"
            :alt="item.titleZh"
            class="artifact-image"
            @error="handleImageError($event, item.id)"
          />

          <div class="artifact-info">
            <h3>{{ item.titleZh }}</h3>
            <p class="artifact-meta">
              {{ item.dynastyName || '未知朝代' }} · {{ item.typeName || '未知类型' }}
            </p>
            <p class="artifact-museum">
              {{ item.museumName || '未知博物馆' }}
            </p>
          </div>
        </el-card>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  getArtifacts,
  getMuseums,
  getDynasties
} from '../api/mockService.js'
import { ElMessage } from 'element-plus'

const router = useRouter()

const keyword = ref('')
const artifacts = ref([])

const artifactTotal = ref(0)
const museumTotal = ref(0)
const dynastyTotal = ref(0)
const countryTotal = ref(0)

const loadHomeData = async () => {
  try {
    const artifactRes = await getArtifacts({
      page: 1,
      pageSize: 6
    })

    artifacts.value = artifactRes.data?.records || []
    artifactTotal.value = artifactRes.data?.total || 0

    const museumRes = await getMuseums({
      page: 1,
      pageSize: 100
    })

    const museumRecords = museumRes.data?.records || []
    museumTotal.value = museumRes.data?.total || museumRecords.length

    const countries = new Set(
      museumRecords
        .map((item) => item.country)
        .filter((item) => item)
    )

    countryTotal.value = countries.size

    const dynastyRes = await getDynasties()
    dynastyTotal.value = dynastyRes.data?.length || 0
  } catch (error) {
    console.error(error)
    ElMessage.error('首页数据加载失败，请检查后端服务是否启动')
  }
}

const handleSearch = () => {
  const value = keyword.value.trim()

  if (!value) {
    router.push('/artifacts')
    return
  }

  router.push({
    path: '/artifacts',
    query: {
      keyword: value
    }
  })
}

const goDetail = (id) => {
  router.push(`/artifacts/${id}`)
}

const handleImageError = (event, id) => {
  event.target.src = `https://picsum.photos/400/300?random=${id}`
}

onMounted(async () => {
  await loadHomeData()
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f5f7fb;
  padding: 32px 0 60px;
}

/* 深蓝色搜索区：恢复图二风格 */
.hero-section {
  width: 1040px;
  margin: 0 auto;
  background: #203f73;
  border-radius: 14px;
  padding: 64px 40px;
  text-align: center;
  color: #ffffff;
}

.hero-section h1 {
  margin: 0 0 12px;
  font-size: 30px;
  font-weight: 600;
  color: #000000;
}

.hero-section p {
  margin: 0 0 28px;
  font-size: 20px;
  color: #ffffff;
}

.search-box {
  width: 560px;
  margin: 0 auto;
  display: flex;
}

.search-box :deep(.el-input__wrapper) {
  border-radius: 4px 0 0 4px;
}

.search-box .el-button {
  width: 80px;
  border-radius: 0 4px 4px 0;
}

/* 统计卡片 */
.stats-section {
  width: 1040px;
  margin: 28px auto 0;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-card {
  text-align: center;
  border-radius: 12px;
}

.stat-number {
  font-size: 36px;
  font-weight: 700;
  color: #203f73;
  line-height: 1.2;
}

.stat-label {
  margin-top: 4px;
  color: #606266;
  font-size: 15px;
}

/* 精选文物 */
.featured-section {
  width: 1040px;
  margin: 36px auto 0;
}

.featured-section h2 {
  text-align: center;
  margin: 0 0 24px;
  font-size: 28px;
  font-weight: 500;
  color: #000000;
}

.artifact-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 28px;
}

.artifact-card {
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
}

.artifact-card:hover {
  transform: translateY(-4px);
}

.artifact-image {
  width: 100%;
  height: 230px;
  object-fit: cover;
  display: block;
}

.artifact-info {
  padding: 18px 12px 20px;
  text-align: center;
}

.artifact-info h3 {
  margin: 0 0 10px;
  font-size: 18px;
  font-weight: 500;
  color: #606266;
}

.artifact-meta {
  margin: 0 0 12px;
  font-size: 14px;
  color: #555;
}

.artifact-museum {
  margin: 0;
  font-size: 14px;
  color: #999;
}

@media screen and (max-width: 1100px) {
  .hero-section,
  .stats-section,
  .featured-section {
    width: calc(100% - 48px);
  }
}

@media screen and (max-width: 800px) {
  .stats-section {
    grid-template-columns: repeat(2, 1fr);
  }

  .artifact-grid {
    grid-template-columns: 1fr;
  }

  .search-box {
    width: 100%;
  }
}
</style>