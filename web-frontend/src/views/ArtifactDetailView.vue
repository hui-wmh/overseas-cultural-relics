<template>
  <div v-if="artifact">
    <el-button @click="router.back()" style="margin-bottom:16px">← 返回</el-button>

    <div class="detail-layout">
      <!-- 左侧图片 -->
      <div class="img-side">
        <img
          :src="artifact.imageUrl"
          :alt="artifact.titleZh"
          class="main-img"
          @error="handleImageError"
          @click="showFullImg = true"
        />
        <div style="text-align:center;margin-top:8px;color:#888;font-size:13px">
          点击图片可全屏查看
        </div>
      </div>

      <!-- 右侧信息 -->
      <div class="info-side">
        <h1>{{ artifact.titleZh }}</h1>
        <p style="color:#888;margin-bottom:16px;font-size:14px">
          {{ artifact.title }}
        </p>

        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="朝代">
            {{ artifact.dynastyName || '暂无' }}
          </el-descriptions-item>

          <el-descriptions-item label="文物类型">
            {{ artifact.typeName || '暂无' }}
          </el-descriptions-item>

          <el-descriptions-item label="材质">
            {{ artifact.materialName || '暂无' }}
          </el-descriptions-item>

          <el-descriptions-item label="年代">
            {{ artifact.period || '暂无' }}
          </el-descriptions-item>

          <el-descriptions-item label="作者">
            {{ artifact.artistName || '未知' }}
          </el-descriptions-item>

          <el-descriptions-item label="收藏博物馆">
            {{ artifact.museumName || '暂无' }}
          </el-descriptions-item>

          <el-descriptions-item label="收藏地点">
            {{ artifact.location || '暂无' }}
          </el-descriptions-item>

          <el-descriptions-item label="来源详情页">
            <a
              v-if="artifact.detailUrl"
              :href="artifact.detailUrl"
              target="_blank"
              rel="noopener noreferrer"
            >
              查看原始页面
            </a>
            <span v-else>暂无</span>
          </el-descriptions-item>
        </el-descriptions>

        <div style="margin-top:20px">
          <h3 style="margin-bottom:8px">文物介绍</h3>
          <p style="line-height:1.9;color:#444;font-size:14px">
            {{ artifact.descriptionZh || '暂无介绍' }}
          </p>
        </div>
      </div>
    </div>

    <!-- 知识图谱关联实体 -->
    <div class="section" v-if="graphNodes.length || graphLinks.length">
      <h3>🔗 知识图谱关联实体</h3>
      <p style="color:#888;font-size:13px;margin:8px 0 16px">
        该文物在知识图谱中的关联关系
      </p>

      <div class="triples" v-if="displayGraphLinks.length">
        <div class="triple-item" v-for="(link, i) in displayGraphLinks" :key="i">
          <span class="node artifact">{{ artifact.titleZh }}</span>
          <span class="arrow">──{{ getRelationText(link.relation) }}──▶</span>
          <span class="node" :class="getNodeClass(getOtherNodeId(link))">
            {{ getNodeName(getOtherNodeId(link)) }}
          </span>
        </div>
      </div>

      <el-empty
        v-else
        description="暂无关联关系"
        :image-size="60"
      />

      <div class="related-tags" style="margin-top:16px" v-if="graphNodes.length">
        <span style="font-size:13px;color:#666;margin-right:8px">关联节点：</span>

        <el-tag
          v-for="node in graphNodes"
          :key="node.id"
          :type="getTagType(node.label)"
          style="margin:4px"
        >
          {{ node.name }}
        </el-tag>
      </div>
    </div>

    <!-- 相关文物推荐 -->
    <div class="section" v-if="recommendedArtifacts.length">
      <h3>✨ 相关文物推荐</h3>
      <p style="color:#888;font-size:13px;margin:8px 0 16px">
        根据馆藏、朝代、类型、材质等特征推荐相近文物
      </p>

      <div class="recommend-grid">
        <div
          class="recommend-card"
          v-for="item in recommendedArtifacts"
          :key="item.id"
          @click="goArtifactDetail(item.id)"
        >
          <img
            :src="item.imageUrl"
            :alt="item.titleZh"
            @error="handleRecommendImageError"
          />

          <div class="recommend-body">
            <div class="recommend-title">{{ item.titleZh }}</div>
            <div class="recommend-meta">
              {{ item.dynastyName || '暂无朝代' }} / {{ item.typeName || '暂无类型' }} / {{ item.materialName || '暂无材质' }}
            </div>
            <div class="recommend-museum">{{ item.museumName || '暂无馆藏' }}</div>
            <el-tag size="small" type="success" style="margin-top:8px">
              {{ item.recommendReason || '相似文物' }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 评论区 -->
    <div class="section">
      <h3>💬 用户评论</h3>

      <div v-if="comments.length">
        <div class="comment" v-for="c in comments" :key="c.id">
          <div class="comment-header">
            <span class="nickname">{{ c.nickname || '匿名用户' }}</span>
            <span class="time">{{ c.createdAt }}</span>
          </div>
          <p style="margin-top:6px;color:#444;font-size:14px">
            {{ c.content }}
          </p>
        </div>
      </div>

      <el-empty v-else description="暂无评论" :image-size="60" />

      <div style="margin-top:16px">
        <el-input
          v-model="newComment"
          type="textarea"
          :rows="3"
          placeholder="发表你的评论..."
        />

        <el-button
          type="primary"
          style="margin-top:8px"
          @click="submitComment"
        >
          提交评论
        </el-button>
      </div>
    </div>

    <!-- 全屏图片弹窗 -->
    <el-dialog v-model="showFullImg" width="80%" align-center>
      <img
        :src="artifact.imageUrl"
        style="width:100%;border-radius:8px"
        @error="handleDialogImageError"
      />
    </el-dialog>
  </div>

  <el-empty
    v-else
    description="正在加载文物详情..."
    style="margin-top:80px"
  />
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getArtifactDetail,
  getComments,
  addComment,
  getArtifactGraph,
  getArtifactRecommendations
} from '../api/mockService.js'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const artifact = ref(null)
const comments = ref([])
const newComment = ref('')
const showFullImg = ref(false)

const graphNodes = ref([])
const graphLinks = ref([])
const recommendedArtifacts = ref([])

const artifactNodeId = computed(() => {
  return `artifact_${route.params.id}`
})

const displayGraphLinks = computed(() => {
  return graphLinks.value.filter((link) => {
    return link.source === artifactNodeId.value || link.target === artifactNodeId.value
  })
})

const relationTextMap = {
  COLLECTED_BY: '收藏于',
  BELONGS_TO_DYNASTY: '所属朝代',
  HAS_TYPE: '文物类型',
  HAS_MATERIAL: '使用材质'
}

const getRelationText = (relation) => {
  return relationTextMap[relation] || relation || '关联'
}

const getOtherNodeId = (link) => {
  if (link.source === artifactNodeId.value) {
    return link.target
  }

  if (link.target === artifactNodeId.value) {
    return link.source
  }

  return link.target
}

const getNodeName = (nodeId) => {
  const node = graphNodes.value.find((item) => item.id === nodeId)
  return node ? node.name : nodeId
}

const getNodeClass = (nodeId) => {
  const node = graphNodes.value.find((item) => item.id === nodeId)

  if (!node) {
    return ''
  }

  const label = String(node.label || '').toLowerCase()

  if (label === 'museum') return 'museum'
  if (label === 'dynasty') return 'dynasty'
  if (label === 'type') return 'type'
  if (label === 'material') return 'material'
  if (label === 'artifact') return 'artifact'

  return ''
}

const getTagType = (label) => {
  const key = String(label || '').toLowerCase()

  const map = {
    museum: '',
    dynasty: 'success',
    type: 'warning',
    material: 'info',
    artifact: 'primary'
  }

  return map[key] || 'info'
}

const loadArtifactDetail = async () => {
  const id = Number(route.params.id)

  const res = await getArtifactDetail(id)
  artifact.value = res.data
}

const loadComments = async () => {
  const id = Number(route.params.id)

  const res = await getComments({
    artifactId: id,
    page: 1,
    pageSize: 20
  })

  comments.value = res.data?.records || []
}

const loadArtifactGraph = async () => {
  const id = Number(route.params.id)

  const graphRes = await getArtifactGraph(id)
  const nodes = graphRes.data?.nodes || []
  const links = graphRes.data?.links || []

  graphNodes.value = nodes.filter((node) => {
    return node.id !== `artifact_${id}`
  })

  graphLinks.value = links
}

const loadArtifactRecommendations = async () => {
  const id = Number(route.params.id)

  const res = await getArtifactRecommendations(id, {
    limit: 4
  })

  recommendedArtifacts.value = res.data || []
}

const submitComment = async () => {
  if (!newComment.value.trim()) {
    return ElMessage.warning('请输入评论内容')
  }

  await addComment({
    userId: 1,
    artifactId: Number(route.params.id),
    content: newComment.value.trim()
  })

  ElMessage.success('评论提交成功，等待审核！')
  newComment.value = ''

  await loadComments()
}

const handleImageError = (event) => {
  event.target.src = `https://picsum.photos/400/300?random=${artifact.value?.id || 1}`
}

const handleDialogImageError = (event) => {
  event.target.src = `https://picsum.photos/800/600?random=${artifact.value?.id || 1}`
}

const handleRecommendImageError = (event) => {
  const id = event.target.alt || artifact.value?.id || 1
  event.target.src = `https://picsum.photos/320/220?random=${id}`
}

const goArtifactDetail = (id) => {
  router.push(`/artifacts/${id}`)
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

const loadPageData = async () => {
  artifact.value = null
  comments.value = []
  graphNodes.value = []
  graphLinks.value = []
  recommendedArtifacts.value = []

  await loadArtifactDetail()
  await loadComments()
  await loadArtifactGraph()
  await loadArtifactRecommendations()
}

watch(
  () => route.params.id,
  async () => {
    await loadPageData()
  },
  {
    immediate: true
  }
)
</script>

<style scoped>
.detail-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  margin-bottom: 32px;
}

.main-img {
  width: 100%;
  border-radius: 12px;
  object-fit: cover;
  cursor: zoom-in;
  transition: opacity 0.2s;
}

.main-img:hover {
  opacity: 0.9;
}

h1 {
  font-size: 22px;
  margin-bottom: 4px;
}

h3 {
  font-size: 16px;
  font-weight: 500;
}

.section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-top: 24px;
  border: 0.5px solid #e0e0e0;
}

.section h3 {
  margin-bottom: 4px;
}

.triples {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.triple-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  flex-wrap: wrap;
}

.node {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.node.artifact {
  background: #e8f0fe;
  color: #1a3a6b;
}

.node.museum {
  background: #e6f4ea;
  color: #1e7e34;
}

.node.dynasty {
  background: #fff3e0;
  color: #e65100;
}

.node.type {
  background: #f3e5f5;
  color: #6a1b9a;
}

.node.material {
  background: #e0f7fa;
  color: #006064;
}

.arrow {
  color: #888;
  font-size: 13px;
}

.recommend-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.recommend-card {
  background: #fafafa;
  border: 0.5px solid #e0e0e0;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.recommend-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.08);
}

.recommend-card img {
  width: 100%;
  height: 130px;
  object-fit: cover;
  display: block;
}

.recommend-body {
  padding: 12px;
}

.recommend-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 6px;
  line-height: 1.4;
}

.recommend-meta {
  font-size: 12px;
  color: #666;
  line-height: 1.5;
}

.recommend-museum {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  line-height: 1.5;
}

.comment {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px 16px;
  margin-top: 12px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nickname {
  font-weight: 500;
  font-size: 14px;
}

.time {
  font-size: 12px;
  color: #999;
}

@media screen and (max-width: 900px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }

  .recommend-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media screen and (max-width: 560px) {
  .recommend-grid {
    grid-template-columns: 1fr;
  }
}
</style>
