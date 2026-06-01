<template>
  <div>
    <h2 style="margin-bottom:16px">搜索文物</h2>
    <el-input v-model="keyword" placeholder="输入文物名称、朝代、类型..." @keyup.enter="search" style="margin-bottom:16px">
      <template #append><el-button @click="search">搜索</el-button></template>
    </el-input>
    <div v-if="list.length" class="grid">
      <div class="card" v-for="a in list" :key="a.id" @click="router.push('/artifacts/'+a.id)">
        <div class="img-box"><img :src="a.imageUrl" @error="e=>e.target.src='https://via.placeholder.com/300x200?text=暂无图片'" /></div>
        <div class="card-body">
          <div class="title">{{ a.titleZh }}</div>
          <div class="meta">{{ a.dynastyName }} · {{ a.typeName }} · {{ a.museumName }}</div>
        </div>
      </div>
    </div>
    <el-empty v-else-if="searched" description="未找到相关文物" />
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { searchArtifacts } from '../api/mockService.js'
const router = useRouter(), route = useRoute()
const keyword = ref(''), list = ref([]), searched = ref(false)
const search = async () => {
  if (!keyword.value) return
  const res = await searchArtifacts({ keyword: keyword.value })
  list.value = res.data.records
  searched.value = true
}
onMounted(() => {
  if (route.query.keyword) { keyword.value = route.query.keyword; search() }
})
</script>
<style scoped>
.grid { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; }
.card { background:white; border-radius:12px; overflow:hidden; border:0.5px solid #e0e0e0; cursor:pointer; transition:transform .2s; }
.card:hover { transform:translateY(-4px); }
.img-box { height:160px; overflow:hidden; }
.img-box img { width:100%; height:100%; object-fit:cover; }
.card-body { padding:12px 16px; }
.title { font-size:15px; font-weight:500; }
.meta { font-size:12px; color:#888; margin-top:4px; }
</style>