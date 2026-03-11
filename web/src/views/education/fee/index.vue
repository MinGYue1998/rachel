<script setup>
import { computed, h, nextTick, onMounted, ref } from 'vue'
import { NButton, NCard, NDataTable, NInput, NInputNumber, NModal, NSelect, NTabPane, NTabs, NTag, NDatePicker, NSpace, NDescriptions, NDescriptionsItem, NDivider } from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'

import educationApi from '@/api/education'

defineOptions({ name: '费用管理' })

const $table = ref(null)
const queryItems = ref({})

// 缴费弹窗
const paymentModalVisible = ref(false)
const paymentForm = ref({ student_id: null, amount: 0, payment_method: 'cash', remark: '' })
const students = ref([])
const courses = ref([])

// 学生详情弹窗
const studentDetailVisible = ref(false)
const studentDetail = ref({})

// 欠费列表
const arrearsData = ref([])
// 当前标签
const activeTab = ref('records')

// 计算转换后的查询参数
const extraParams = computed(() => {
  const params = {}
  if (queryItems.value.dateRange && Array.isArray(queryItems.value.dateRange) && queryItems.value.dateRange.length === 2) {
    const [start, end] = queryItems.value.dateRange
    params.start_date = new Date(start).toISOString().split('T')[0]
    params.end_date = new Date(end).toISOString().split('T')[0]
  }
  return params
})

onMounted(async () => {
  const [studentRes, courseRes] = await Promise.all([
    educationApi.getActiveStudents(),
    educationApi.getActiveCourses(),
  ])
  students.value = studentRes.data || []
  courses.value = courseRes.data || []
  $table.value?.handleSearch()
  loadArrears()
})

// 标签切换时重新加载数据
async function handleTabChange(tab) {
  if (tab === 'records') {
    await nextTick()
    $table.value?.handleSearch()
  }
}

async function loadArrears() {
  const res = await educationApi.getArrearsStudents()
  arrearsData.value = res.data || []
}

const columns = [
  { title: '学生', key: 'student_name', width: 100 },
  { title: '课程', key: 'course_name', width: 100 },
  { title: '金额', key: 'amount', width: 100, render: (row) => `¥${Math.abs(row.amount)}` },
  { title: '备注', key: 'remark', width: 150 },
  { title: '时间', key: 'created_at', width: 150 },
]

// 处理筛选
function handleSearch() {
  $table.value?.handleSearch()
}

const arrearsColumns = [
  { 
    title: '学生', 
    key: 'student_name', 
    width: 100,
    render: (row) => h(NButton, { text: true, type: 'primary', onClick: () => viewStudentDetail(row.student_id) }, { default: () => row.student_name })
  },
  { title: '总费用', key: 'total_fee', width: 100, render: (row) => `¥${row.total_fee}` },
  { title: '已缴费', key: 'total_paid', width: 100, render: (row) => `¥${row.total_paid}` },
  { title: '欠费', key: 'balance', width: 100, render: (row) => h(NTag, { type: 'error' }, { default: () => `¥${row.balance}` }) },
  {
    title: '操作', key: 'actions', width: 120, render: (row) => h(NSpace, null, {
      default: () => [
        h(NButton, { size: 'small', type: 'primary', onClick: () => openPaymentModal(row) }, { default: () => '缴费' }),
        h(NButton, { size: 'small', onClick: () => viewStudentDetail(row.student_id) }, { default: () => '详情' }),
      ]
    })
  },
]

function openPaymentModal(row) {
  paymentForm.value = { student_id: row.student_id, amount: row.balance, payment_method: 'cash', remark: '' }
  paymentModalVisible.value = true
}

async function submitPayment() {
  await educationApi.createPayment({
    ...paymentForm.value,
    payment_time: new Date().toISOString(),
  })
  paymentModalVisible.value = false
  $table.value?.handleSearch()
  loadArrears()
}

async function viewStudentDetail(studentId) {
  const res = await educationApi.getStudentDetail({ student_id: studentId })
  studentDetail.value = res.data || {}
  studentDetailVisible.value = true
}
</script>

<template>
  <CommonPage show-footer title="费用管理">
    <NTabs v-model:value="activeTab" type="line" animated @update:value="handleTabChange">
      <NTabPane name="records" tab="费用记录">
        <CrudTable v-if="activeTab === 'records'" ref="$table" v-model:query-items="queryItems" :columns="columns" :get-data="educationApi.getFeeRecordList" :extra-params="extraParams">
          <template #queryBar>
            <QueryBarItem label="学生" :label-width="40">
              <NSelect v-model:value="queryItems.student_id" :options="students.map(s => ({ label: s.name, value: s.id }))" clearable placeholder="选择学生" @update:value="handleSearch" />
            </QueryBarItem>
            <QueryBarItem label="课程" :label-width="40">
              <NSelect v-model:value="queryItems.course_id" :options="courses.map(c => ({ label: c.name, value: c.id }))" clearable placeholder="选择课程" @update:value="handleSearch" />
            </QueryBarItem>
            <QueryBarItem label="时间" :label-width="40">
              <NDatePicker v-model:value="queryItems.dateRange" type="daterange" clearable @update:value="handleSearch" />
            </QueryBarItem>
          </template>
        </CrudTable>
      </NTabPane>
      <NTabPane name="arrears" tab="欠费学生">
        <NCard v-if="activeTab === 'arrears'">
          <NDataTable :columns="arrearsColumns" :data="arrearsData" :bordered="false" />
        </NCard>
      </NTabPane>
    </NTabs>

    <!-- 缴费弹窗 -->
    <NModal v-model:show="paymentModalVisible" preset="card" title="登记缴费" style="width: 400px">
      <NCard>
        <div class="mb-4">
          <div class="mb-2">缴费金额：</div>
          <NInputNumber v-model:value="paymentForm.amount" :min="0" :precision="2" style="width: 100%">
            <template #prefix>¥</template>
          </NInputNumber>
        </div>
        <div class="mb-4">
          <div class="mb-2">支付方式：</div>
          <NSelect v-model:value="paymentForm.payment_method" :options="[{ label: '现金', value: 'cash' }, { label: '微信', value: 'wechat' }, { label: '支付宝', value: 'alipay' }, { label: '银行转账', value: 'bank' }]" style="width: 100%" />
        </div>
        <div class="mb-4">
          <div class="mb-2">备注：</div>
          <NInput v-model:value="paymentForm.remark" type="textarea" placeholder="请输入备注信息" />
        </div>
        <NButton type="primary" block @click="submitPayment">确认缴费</NButton>
      </NCard>
    </NModal>

    <!-- 学生详情弹窗 -->
    <NModal v-model:show="studentDetailVisible" preset="card" title="学生详情" style="width: 800px">
      <NDescriptions label-placement="left" :column="2" bordered>
        <NDescriptionsItem label="姓名">{{ studentDetail.name }}</NDescriptionsItem>
        <NDescriptionsItem label="性别">{{ studentDetail.gender || '-' }}</NDescriptionsItem>
        <NDescriptionsItem label="电话">{{ studentDetail.phone || '-' }}</NDescriptionsItem>
        <NDescriptionsItem label="监护人">{{ studentDetail.guardian || '-' }}</NDescriptionsItem>
        <NDescriptionsItem label="监护人电话">{{ studentDetail.guardian_phone || '-' }}</NDescriptionsItem>
        <NDescriptionsItem label="状态">{{ studentDetail.is_active ? '在读' : '已结课' }}</NDescriptionsItem>
      </NDescriptions>

      <NDivider>费用汇总</NDivider>
      <NDescriptions v-if="studentDetail.fee_summary" label-placement="left" :column="4" bordered>
        <NDescriptionsItem label="总费用">¥{{ studentDetail.fee_summary?.total_fee || 0 }}</NDescriptionsItem>
        <NDescriptionsItem label="优惠金额">¥{{ studentDetail.fee_summary?.total_discount || 0 }}</NDescriptionsItem>
        <NDescriptionsItem label="已缴费">¥{{ studentDetail.fee_summary?.total_paid || 0 }}</NDescriptionsItem>
        <NDescriptionsItem label="欠费">
          <NTag v-if="studentDetail.fee_summary?.balance > 0" type="error">¥{{ studentDetail.fee_summary?.balance }}</NTag>
          <span v-else>¥0</span>
        </NDescriptionsItem>
      </NDescriptions>

      <NDivider>课程列表</NDivider>
      <NDataTable :columns="[
        { title: '课程名称', key: 'name' },
        { title: '授课老师', key: 'teacher' },
        { title: '课时单价', key: 'unit_price', render: (row) => `¥${row.unit_price}` },
        { title: '总课时', key: 'total_hours' },
        { title: '优惠金额', key: 'discount', render: (row) => `¥${row.discount}` },
        { title: '课程费用', key: 'total_fee', render: (row) => `¥${row.total_fee}` },
      ]" :data="studentDetail.courses || []" :bordered="false" size="small" />

      <NDivider>请假记录</NDivider>
      <NDataTable :columns="[
        { title: '课程', key: 'course_name' },
        { title: '请假日期', key: 'class_date' },
        { title: '请假课时', key: 'leave_hours' },
        { title: '请假原因', key: 'leave_reason' },
      ]" :data="studentDetail.leave_records || []" :bordered="false" size="small" />

      <NDivider>缴费记录</NDivider>
      <NDataTable :columns="[
        { title: '缴费金额', key: 'amount', render: (row) => `¥${row.amount}` },
        { title: '支付方式', key: 'payment_method', render: (row) => ({ cash: '现金', wechat: '微信', alipay: '支付宝', bank: '银行转账' }[row.payment_method] || row.payment_method) },
        { title: '缴费时间', key: 'payment_time' },
        { title: '备注', key: 'remark' },
      ]" :data="studentDetail.payment_records || []" :bordered="false" size="small" />
    </NModal>
  </CommonPage>
</template>
