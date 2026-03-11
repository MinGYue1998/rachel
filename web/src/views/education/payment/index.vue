<script setup>
import { computed, onMounted, ref } from 'vue'
import { NDatePicker, NSelect } from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'

import educationApi from '@/api/education'

defineOptions({ name: '缴费记录' })

const $table = ref(null)
const queryItems = ref({})
const students = ref([])

// 格式化日期为本地时间字符串（避免时区偏移）
function formatLocalDate(timestamp) {
  const date = new Date(timestamp)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 计算转换后的查询参数
const extraParams = computed(() => {
  const params = {}
  if (queryItems.value.dateRange && Array.isArray(queryItems.value.dateRange) && queryItems.value.dateRange.length === 2) {
    const [start, end] = queryItems.value.dateRange
    params.start_date = formatLocalDate(start)
    params.end_date = formatLocalDate(end)
  }
  return params
})

const columns = [
  { title: '学生', key: 'student_name', width: 100 },
  { title: '缴费金额', key: 'amount', width: 100, render: (row) => `¥${row.amount}` },
  { 
    title: '支付方式', 
    key: 'payment_method', 
    width: 100,
    render: (row) => {
      const methodMap = { cash: '现金', wechat: '微信', alipay: '支付宝', bank: '银行转账' }
      return methodMap[row.payment_method] || row.payment_method
    }
  },
  { title: '缴费时间', key: 'payment_time', width: 150 },
  { title: '备注', key: 'remark', width: 200 },
  { title: '创建时间', key: 'created_at', width: 150 },
]

onMounted(async () => {
  const studentRes = await educationApi.getActiveStudents()
  students.value = studentRes.data || []
  $table.value?.handleSearch()
})

function handleSearch() {
  $table.value?.handleSearch()
}
</script>

<template>
  <CommonPage show-footer title="缴费记录">
    <CrudTable ref="$table" v-model:query-items="queryItems" :columns="columns" :get-data="educationApi.getPaymentList" :extra-params="extraParams">
      <template #queryBar>
        <QueryBarItem label="学生" :label-width="40">
          <NSelect v-model:value="queryItems.student_id" :options="students.map(s => ({ label: s.name, value: s.id }))" clearable placeholder="选择学生" @update:value="handleSearch" />
        </QueryBarItem>
        <QueryBarItem label="支付方式" :label-width="60">
          <NSelect v-model:value="queryItems.payment_method" :options="[{ label: '现金', value: 'cash' }, { label: '微信', value: 'wechat' }, { label: '支付宝', value: 'alipay' }, { label: '银行转账', value: 'bank' }]" clearable placeholder="选择支付方式" @update:value="handleSearch" />
        </QueryBarItem>
        <QueryBarItem label="时间" :label-width="40">
          <NDatePicker v-model:value="queryItems.dateRange" type="daterange" clearable @update:value="handleSearch" />
        </QueryBarItem>
      </template>
    </CrudTable>
  </CommonPage>
</template>
