<template>
  <div style="max-width:420px;margin:60px auto">
    <div style="background:white;border-radius:12px;padding:32px;border:0.5px solid #e0e0e0">
      <h2 style="text-align:center;margin-bottom:24px">{{ isLogin ? '用户登录' : '用户注册' }}</h2>

      <div style="margin-bottom:16px">
        <div style="font-size:13px;color:#666;margin-bottom:6px">用户名 *</div>
        <el-input v-model="form.username" placeholder="请输入用户名" />
        <div v-if="!isLogin" style="font-size:12px;color:#999;margin-top:4px">
        3-20位
        </div>
      </div>

      <div style="margin-bottom:16px">
        <div style="font-size:13px;color:#666;margin-bottom:6px">密码 *</div>
        <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        <div v-if="!isLogin" style="font-size:12px;color:#999;margin-top:4px">
        至少6位，需同时包含字母和数字
        </div>
      </div>

      <template v-if="!isLogin">
        <div style="margin-bottom:16px">
          <div style="font-size:13px;color:#666;margin-bottom:6px">昵称</div>
          <el-input v-model="form.nickname" placeholder="请输入昵称（选填）" />
        </div>
        <div style="margin-bottom:16px">
          <div style="font-size:13px;color:#666;margin-bottom:6px">邮箱</div>
          <el-input v-model="form.email" placeholder="请输入邮箱（选填）" />
        </div>
        <div style="margin-bottom:16px">
          <div style="font-size:13px;color:#666;margin-bottom:6px">手机号</div>
          <el-input v-model="form.phone" placeholder="请输入手机号（选填）" />
        </div>
        <div style="margin-bottom:20px">
          <div style="font-size:13px;color:#666;margin-bottom:8px">头像</div>
          <div style="display:flex;align-items:center;gap:12px">
            <div class="avatar-preview" :style="form.avatar ? `background-image:url(${form.avatar})` : ''">
              <span v-if="!form.avatar">{{ form.username?.[0] || '?' }}</span>
            </div>
            <div>
              <div style="font-size:12px;color:#999;margin-bottom:6px">选择头像风格</div>
              <div style="display:flex;gap:6px">
                <div
                  v-for="i in 6" :key="i"
                  class="avatar-option"
                  :class="{selected: form.avatar===`https://api.dicebear.com/7.x/fun-emoji/svg?seed=${i}`}"
                  @click="form.avatar=`https://api.dicebear.com/7.x/fun-emoji/svg?seed=${i}`"
                >
                  <img :src="`https://api.dicebear.com/7.x/fun-emoji/svg?seed=${i}`" style="width:32px;height:32px" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <el-button type="primary" style="width:100%;margin-bottom:12px" @click="submit" :loading="loading">
        {{ isLogin ? '登录' : '注册' }}
      </el-button>

      <div style="text-align:center;font-size:13px;color:#888">
        {{ isLogin ? '还没有账号？' : '已有账号？' }}
        <span style="color:#1a3a6b;cursor:pointer" @click="isLogin=!isLogin">
          {{ isLogin ? '立即注册' : '去登录' }}
        </span>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user.js'
import { login, register } from '../api/mockService.js'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const isLogin = ref(true)
const loading = ref(false)
const form = ref({ username: '', password: '', nickname: '', email: '', phone: '', avatar: '' })

const submit = async () => {
  if (!form.value.username) return ElMessage.warning('请输入用户名')
  if (!form.value.password) return ElMessage.warning('请输入密码')
  if (!form.value.username) return ElMessage.warning('请输入用户名')
  if (form.value.username.length < 3 || form.value.username.length > 20) return ElMessage.warning('用户名长度需在3-20位之间')
  if (!form.value.password) return ElMessage.warning('请输入密码')
  if (form.value.password.length < 6) return ElMessage.warning('密码长度不能少于6位')
  if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(form.value.password)) return ElMessage.warning('密码需同时包含字母和数字')
  if (!isLogin.value && form.value.email && !/^[\w.-]+@[\w.-]+\.\w+$/.test(form.value.email)) return ElMessage.warning('邮箱格式不正确')
  if (!isLogin.value && form.value.phone && !/^1\d{10}$/.test(form.value.phone)) return ElMessage.warning('手机号格式不正确')
  loading.value = true
  try {
    const fn = isLogin.value ? login : register
    const res = await fn(form.value)
    if (res.code !== 200) {
      ElMessage.error(res.message)
      return
    }
    userStore.setUser(res.data)
    ElMessage.success(isLogin.value ? '登录成功！' : '注册成功！')
    router.push('/')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.avatar-preview {
  width: 56px; height: 56px; border-radius: 50%;
  background: #1a3a6b; color: white;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; font-weight: bold;
  background-size: cover; background-position: center;
  border: 2px solid #e0e0e0;
}
.avatar-option {
  width: 40px; height: 40px; border-radius: 50%;
  border: 2px solid #e0e0e0; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden; transition: border-color .2s;
}
.avatar-option:hover { border-color: #1a3a6b; }
.avatar-option.selected { border-color: #1a3a6b; border-width: 3px; }
</style>