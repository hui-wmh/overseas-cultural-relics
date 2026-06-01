<template>
  <div style="max-width:600px;margin:0 auto">
    <div style="background:white;border-radius:12px;padding:32px;border:0.5px solid #e0e0e0">

      <!-- 头像 + 基本信息 -->
      <div style="display:flex;align-items:center;gap:20px;margin-bottom:28px">
        <div class="avatar" :style="userStore.userInfo.avatar ? `background-image:url(${userStore.userInfo.avatar});background-size:cover` : ''">
          <span v-if="!userStore.userInfo.avatar" style="font-size:28px;font-weight:bold;color:white">
            {{ userStore.userInfo.nickname?.[0] }}
          </span>
        </div>
        <div>
          <h2>{{ userStore.userInfo.nickname }}</h2>
          <p style="color:#888;font-size:14px">@{{ userStore.userInfo.username }}</p>
        </div>
      </div>

      <!-- 编辑信息 -->
      <div v-if="!editing">
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="昵称">{{ userStore.userInfo.nickname }}</el-descriptions-item>
          <el-descriptions-item label="用户名">{{ userStore.userInfo.username }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ userStore.userInfo.email || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ userStore.userInfo.phone || '未设置' }}</el-descriptions-item>
        </el-descriptions>
        <div style="margin-top:16px;display:flex;gap:12px">
          <el-button type="primary" @click="startEdit">编辑个人信息</el-button>
          <el-button type="danger" plain @click="logout">退出登录</el-button>
        </div>
      </div>

      <!-- 编辑表单 -->
      <div v-else>
        <div style="margin-bottom:14px">
          <div style="font-size:13px;color:#666;margin-bottom:6px">昵称</div>
          <el-input v-model="editForm.nickname" />
        </div>
        <div style="margin-bottom:14px">
          <div style="font-size:13px;color:#666;margin-bottom:6px">邮箱</div>
          <el-input v-model="editForm.email" />
        </div>
        <div style="margin-bottom:14px">
          <div style="font-size:13px;color:#666;margin-bottom:6px">手机号</div>
          <el-input v-model="editForm.phone" />
        </div>
        <div style="margin-bottom:20px">
          <div style="font-size:13px;color:#666;margin-bottom:8px">更换头像</div>
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            <div
              v-for="i in 6" :key="i"
              class="avatar-option"
              :class="{selected: editForm.avatar===`https://api.dicebear.com/7.x/fun-emoji/svg?seed=${i}`}"
              @click="editForm.avatar=`https://api.dicebear.com/7.x/fun-emoji/svg?seed=${i}`"
            >
              <img :src="`https://api.dicebear.com/7.x/fun-emoji/svg?seed=${i}`" style="width:36px;height:36px" />
            </div>
          </div>
        </div>
        <div style="display:flex;gap:12px">
          <el-button type="primary" @click="saveEdit">保存修改</el-button>
          <el-button @click="editing=false">取消</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user.js'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const editing = ref(false)
const editForm = ref({})

const startEdit = () => {
  editForm.value = { ...userStore.userInfo }
  editing.value = true
}
const saveEdit = () => {
  userStore.updateInfo(editForm.value)
  editing.value = false
  ElMessage.success('个人信息已更新！')
}
const logout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/')
}
</script>

<style scoped>
.avatar {
  width: 72px; height: 72px; border-radius: 50%;
  background: #1a3a6b;
  display: flex; align-items: center; justify-content: center;
  border: 2px solid #e0e0e0; flex-shrink: 0;
  background-size: cover; background-position: center;
}
.avatar-option {
  width: 44px; height: 44px; border-radius: 50%;
  border: 2px solid #e0e0e0; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden; transition: border-color .2s;
}
.avatar-option:hover { border-color: #1a3a6b; }
.avatar-option.selected { border-color: #1a3a6b; border-width: 3px; }
</style>