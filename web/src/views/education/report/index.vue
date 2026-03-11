<script setup>
import { h, onMounted, ref } from 'vue'
import { NButton, NCard, NDataTable, NDatePicker, NSelect, NTabPane, NTabs, NSpace } from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'

import educationApi from '@/api/education'

defineOptions({ name: '统计报表' })

const monthlyData = ref([])
const studentDetailData = ref([])
const students = ref([])
const courses = ref([])

// 筛选条件
const monthlyFilter = ref({ year: null })
const studentFilter = ref({ student_id: null, course_id: null, year: null, month: null })

// 月份选项
const monthOptions = [
  { label: '1月', value: 1 },
  { label: '2月', value: 2 },
  { label: '3月', value: 3 },
  { label: '4月', value: 4 },
  { label: '5月', value: 5 },
  { label: '6月', value: 6 },
  { label: '7月', value: 7 },
  { label: '8月', value: 8 },
  { label: '9月', value: 9 },
  { label: '10月', value: 10 },
  { label: '11月', value: 11 },
  { label: '12月', value: 12 },
]

onMounted(async () => {
  const [studentRes, courseRes] = await Promise.all([
    educationApi.getActiveStudents(),
    educationApi.getActiveCourses(),
  ])
  students.value = studentRes.data || []
  courses.value = courseRes.data || []
  loadMonthlyReport()
  loadStudentDetailReport()
})

async function loadMonthlyReport() {
  const params = {}
  if (monthlyFilter.value.year) {
    const date = new Date(monthlyFilter.value.year)
    params.year = date.getFullYear()
  }
  const res = await educationApi.getMonthlyReport(params)
  monthlyData.value = res.data || []
}

async function loadStudentDetailReport() {
  const params = {}
  if (studentFilter.value.student_id) params.student_id = studentFilter.value.student_id
  if (studentFilter.value.course_id) params.course_id = studentFilter.value.course_id
  if (studentFilter.value.year) {
    const date = new Date(studentFilter.value.year)
    params.year = date.getFullYear()
  }
  if (studentFilter.value.month) params.month = studentFilter.value.month
  const res = await educationApi.getStudentDetailReport(params)
  studentDetailData.value = res.data || []
}

const monthlyColumns = [
  { title: '月份', key: 'month', width: 100 },
  { title: '课时费合计', key: 'total_class_fee', width: 120, render: (row) => `¥${row.total_class_fee}` },
  { title: '缴费合计', key: 'total_payment', width: 120, render: (row) => `¥${row.total_payment}` },
  { title: '上课次数', key: 'class_count', width: 100 },
  { title: '学生人数', key: 'student_count', width: 100 },
]

const studentColumns = [
  { title: '学生', key: 'student_name', width: 100 },
  { title: '课程', key: 'course_name', width: 100 },
  { title: '上课次数', key: 'class_count', width: 80 },
  { title: '总课时', key: 'total_hours', width: 80 },
  { title: '总费用', key: 'total_fee', width: 100, render: (row) => `¥${row.total_fee}` },
  { title: '优惠金额', key: 'total_discount', width: 100, render: (row) => `¥${row.total_discount}` },
  { title: '已缴费', key: 'total_paid', width: 100, render: (row) => `¥${row.total_paid}` },
  { title: '欠费', key: 'balance', width: 100, render: (row) => `¥${row.balance}` },
]

async function exportMonthly() {
  const res = await educationApi.exportReport({ report_type: 'monthly' })
  downloadFile(res, 'monthly_report.csv')
}

async function exportMonthlyExcel() {
  const res = await educationApi.exportReportExcel({ report_type: 'monthly' })
  downloadFile(res, 'monthly_report.xlsx')
}

async function exportStudentDetail() {
  const res = await educationApi.exportReport({ report_type: 'student-detail' })
  downloadFile(res, 'student_detail_report.csv')
}

async function exportStudentDetailExcel() {
  const params = { report_type: 'student-detail' }
  if (studentFilter.value.student_id) params.student_id = studentFilter.value.student_id
  if (studentFilter.value.course_id) params.course_id = studentFilter.value.course_id
  if (studentFilter.value.year) {
    const date = new Date(studentFilter.value.year)
    params.year = date.getFullYear()
  }
  if (studentFilter.value.month) params.month = studentFilter.value.month
  const res = await educationApi.exportReportExcel(params)
  downloadFile(res, 'student_detail_report.xlsx')
}

function downloadFile(blob, filename) {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  window.URL.revokeObjectURL(url)
}
</script>

<template>
  <CommonPage show-footer title="统计报表">
    <NTabs type="line" animated>
      <NTabPane name="monthly" tab="月度汇总">
        <div class="mb-4 flex gap-4 items-center">
          <NDatePicker v-model:value="monthlyFilter.year" type="year" clearable placeholder="选择年份" @update:value="loadMonthlyReport" />
          <NButton type="primary" @click="exportMonthly">导出CSV</NButton>
          <NButton type="info" @click="exportMonthlyExcel">导出Excel</NButton>
        </div>
        <NCard>
          <NDataTable :columns="monthlyColumns" :data="monthlyData" :bordered="false" />
        </NCard>
      </NTabPane>
      <NTabPane name="student" tab="学生明细">
        <div class="mb-4 flex gap-4 items-center flex-wrap">
          <NSelect v-model:value="studentFilter.student_id" :options="students.map(s => ({ label: s.name, value: s.id }))" clearable placeholder="选择学生" style="width: 150px" @update:value="loadStudentDetailReport" />
          <NSelect v-model:value="studentFilter.course_id" :options="courses.map(c => ({ label: c.name, value: c.id }))" clearable placeholder="选择课程" style="width: 150px" @update:value="loadStudentDetailReport" />
          <NDatePicker v-model:value="studentFilter.year" type="year" clearable placeholder="选择年份" @update:value="loadStudentDetailReport" />
          <NSelect v-model:value="studentFilter.month" :options="monthOptions" clearable placeholder="选择月份" style="width: 100px" @update:value="loadStudentDetailReport" />
          <NButton type="primary" @click="exportStudentDetail">导出CSV</NButton>
          <NButton type="info" @click="exportStudentDetailExcel">导出Excel</NButton>
        </div>
        <NCard>
          <NDataTable :columns="studentColumns" :data="studentDetailData" :bordered="false" />
        </NCard>
      </NTabPane>
    </NTabs>
  </CommonPage>
</template>
