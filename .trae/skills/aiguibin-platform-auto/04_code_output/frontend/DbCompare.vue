<template>
  <div class="db-compare">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据库比对</span>
          <div class="header-actions">
            <el-button type="primary" @click="executeCompare('DEV')">DEV环境比对</el-button>
            <el-button type="success" @click="executeCompare('SIT')">SIT环境比对</el-button>
            <el-button type="warning" @click="executeCompare('UAT')">UAT环境比对</el-button>
            <el-button type="danger" @click="executeCompare('ALL')">全环境比对</el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="recordList" v-loading="loading" stripe>
        <el-table-column prop="recordNo" label="记录编号" width="180" />
        <el-table-column prop="env" label="环境" width="80" />
        <el-table-column prop="dbName" label="数据库" width="150" />
        <el-table-column prop="triggerType" label="触发类型" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tableDiffCount" label="表差异" width="80" />
        <el-table-column prop="columnDiffCount" label="字段差异" width="80" />
        <el-table-column prop="indexDiffCount" label="索引差异" width="80" />
        <el-table-column prop="createTime" label="执行时间" width="180" />
        <el-table-column label="操作" fixed="right" width="120">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pageNum"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadRecords"
        @current-change="loadRecords"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { executeCompareApi, getRecordListApi } from '@/api/dbcompare'

const loading = ref(false)
const recordList = ref<any[]>([])
const pageNum = ref(1)
const pageSize = ref(10)
const total = ref(0)

const getStatusType = (status: string) => {
  switch (status) {
    case 'SUCCESS': return 'success'
    case 'RUNNING': return 'warning'
    case 'FAILED': return 'danger'
    default: return 'info'
  }
}

const executeCompare = async (env: string) => {
  loading.value = true
  try {
    await executeCompareApi(env)
    ElMessage.success(`${env}环境比对任务已启动`)
    loadRecords()
  } catch (error: any) {
    ElMessage.error(error.message || '执行失败')
  } finally {
    loading.value = false
  }
}

const loadRecords = async () => {
  try {
    const res = await getRecordListApi({ pageNum: pageNum.value, pageSize: pageSize.value })
    recordList.value = res.data.records
    total.value = res.data.total
  } catch (error: any) {
    ElMessage.error(error.message || '加载失败')
  }
}

const viewDetail = (row: any) => {
  console.log('查看详情', row)
}

onMounted(() => {
  loadRecords()
})
</script>

<style scoped>
.db-compare {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}
</style>
