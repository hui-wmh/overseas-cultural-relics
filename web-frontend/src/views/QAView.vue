<template>
  <div>
    <h2 style="margin-bottom:8px">智能问答</h2>
    <p style="color:#888;margin-bottom:16px">基于知识图谱的文物知识问答</p>
    <div class="hot">
      <span style="font-size:13px;color:#666;margin-right:8px">热门问题：</span>
      <el-tag v-for="q in hotList" :key="q.question" style="margin:4px;cursor:pointer" @click="ask(q.question)">{{ q.question }}</el-tag>
    </div>
    <div class="chat-box">
      <div v-for="(msg,i) in messages" :key="i" :class="['msg', msg.role]">
        <div class="bubble">{{ msg.content }}</div>
      </div>
      <div v-if="loading" class="msg assistant"><div class="bubble">正在思考中...</div></div>
    </div>
    <div class="input-row">
      <el-input v-model="input" placeholder="请输入问题，如：青花瓷现藏于哪个博物馆？" @keyup.enter="ask(input)" />
      <el-button type="primary" @click="ask(input)" :loading="loading">提问</el-button>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { askQuestion, getHotQuestions } from '../api/mockService.js'
const input = ref(''), messages = ref([]), loading = ref(false), hotList = ref([])
onMounted(async () => { hotList.value = (await getHotQuestions()).data })
const ask = async (q) => {
  if (!q) return
  input.value = ''
  messages.value.push({ role: 'user', content: q })
  loading.value = true
  const res = await askQuestion({ question: q })
  messages.value.push({ role: 'assistant', content: res.data.answer })
  loading.value = false
}
</script>
<style scoped>
.hot { background:white; border-radius:8px; padding:12px 16px; margin-bottom:16px; border:0.5px solid #e0e0e0; }
.chat-box { background:white; border-radius:12px; padding:16px; min-height:300px; margin-bottom:16px; border:0.5px solid #e0e0e0; display:flex; flex-direction:column; gap:12px; }
.msg { display:flex; }
.msg.user { justify-content:flex-end; }
.bubble { max-width:70%; padding:10px 14px; border-radius:12px; font-size:14px; line-height:1.6; }
.user .bubble { background:#1a3a6b; color:white; }
.assistant .bubble { background:#f0f2f5; color:#333; }
.input-row { display:flex; gap:8px; }
</style>