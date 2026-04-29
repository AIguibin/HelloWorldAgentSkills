<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2>架构管理平台</h2>
      </template>
      
      <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading">登录</el-button>
        </el-form-item>
      </el-form>
      
      <el-dialog v-model="showOrgDialog" title="选择机构" width="400px">
        <el-radio-group v-model="selectedOrg">
          <el-radio v-for="org in orgList" :key="org.orgCode" :label="org.orgCode">
            {{ org.orgName }}
          </el-radio>
        </el-radio-group>
        <template #footer>
          <el-button type="primary" @click="handleSelectOrg">确认</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { loginApi, selectOrgApi } from '@/api/auth'

const router = useRouter()
const loginFormRef = ref()
const loading = ref(false)
const showOrgDialog = ref(false)
const orgList = ref<any[]>([])
const selectedOrg = ref('')
const tempToken = ref('')

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  const valid = await loginFormRef.value?.validate()
  if (!valid) return
  
  loading.value = true
  try {
    const res = await loginApi(loginForm)
    tempToken.value = res.data.tempToken
    orgList.value = res.data.orgList
    
    if (orgList.value.length === 1) {
      selectedOrg.value = orgList.value[0].orgCode
      await handleSelectOrg()
    } else {
      showOrgDialog.value = true
    }
  } catch (error: any) {
    ElMessage.error(error.message || '登录失败')
  } finally {
    loading.value = false
  }
}

const handleSelectOrg = async () => {
  if (!selectedOrg.value) {
    ElMessage.warning('请选择机构')
    return
  }
  
  try {
    const res = await selectOrgApi({
      tempToken: tempToken.value,
      orgCode: selectedOrg.value
    })
    
    localStorage.setItem('accessToken', res.data.accessToken)
    localStorage.setItem('refreshToken', res.data.refreshToken)
    localStorage.setItem('userInfo', JSON.stringify(res.data.userInfo))
    
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error: any) {
    ElMessage.error(error.message || '选择机构失败')
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
}

.login-card h2 {
  text-align: center;
  margin: 0;
  color: #303133;
}
</style>
