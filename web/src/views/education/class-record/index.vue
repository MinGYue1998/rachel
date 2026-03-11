<script setup>
import { computed, h, onMounted, ref, resolveDirective, watch, withDirectives } from 'vue'
import {
  NButton,
  NCalendar,
  NDatePicker,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NModal,
  NPopconfirm,
  NSelect,
  NDataTable,
  NTag,
  NTimePicker,
} from 'naive-ui'
import dayjs from 'dayjs'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import CrudTable from '@/components/table/CrudTable.vue'

import { formatDate, renderIcon } from '@/utils'
import { useCRUD } from '@/composables'
import educationApi from '@/api/education'
import TheIcon from '@/components/icon/TheIcon.vue'

defineOptions({ name: '上课记录' })

const $table = ref(null)
const queryItems = ref({})
const vPermission = resolveDirective('permission')

const courses = ref([])
const students = ref([])

// 考勤数据
const attendanceList = ref([])
const selectedStudent = ref(null)

const {
  modalVisible,
  modalTitle,
  modalAction,
  modalLoading,
  handleSave: baseHandleSave,
  modalForm,
  modalFormRef,
  handleEdit: baseHandleEdit,
  handleDelete,
  handleAdd,
} = useCRUD({
  name: '上课记录',
  initForm: { course_id: null, class_date: null, start_time: null, end_time: null, class_hours: 1, attendances: [] },
  doCreate: async (data) => {
    const submitData = { ...data }
    // 将时间戳转换为日期字符串（使用本地时间避免时区偏移）
    if (submitData.class_date && typeof submitData.class_date === 'number') {
      const date = new Date(submitData.class_date)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      submitData.class_date = `${year}-${month}-${day}`
    }
    // 转换开始时间（使用本地时间）
    if (submitData.start_time && typeof submitData.start_time === 'number') {
      const date = new Date(submitData.start_time)
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      submitData.start_time = `${hours}:${minutes}`
    }
    // 转换结束时间（使用本地时间）
    if (submitData.end_time && typeof submitData.end_time === 'number') {
      const date = new Date(submitData.end_time)
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      submitData.end_time = `${hours}:${minutes}`
    }
    submitData.attendances = attendanceList.value
    return educationApi.createClassRecord(submitData)
  },
  doUpdate: async (data) => {
    const submitData = { ...data }
    // 将时间戳转换为日期字符串（使用本地时间避免时区偏移）
    if (submitData.class_date && typeof submitData.class_date === 'number') {
      const date = new Date(submitData.class_date)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      submitData.class_date = `${year}-${month}-${day}`
    }
    // 转换开始时间（使用本地时间）
    if (submitData.start_time && typeof submitData.start_time === 'number') {
      const date = new Date(submitData.start_time)
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      submitData.start_time = `${hours}:${minutes}`
    }
    // 转换结束时间（使用本地时间）
    if (submitData.end_time && typeof submitData.end_time === 'number') {
      const date = new Date(submitData.end_time)
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      submitData.end_time = `${hours}:${minutes}`
    }
    // 添加考勤数据
    submitData.attendances = attendanceList.value
    return educationApi.updateClassRecord(submitData)
  },
  doDelete: educationApi.deleteClassRecord,
  refresh: () => $table.value?.handleSearch(),
})

// 保存前验证
function handleSave() {
  // 验证学生考勤
  if (modalAction.value === 'add' && attendanceList.value.length > 0) {
    const classHours = Number(modalForm.value.class_hours) || 0
    for (let i = 0; i < attendanceList.value.length; i++) {
      const item = attendanceList.value[i]
      const actualHours = Number(item.actual_hours) || 0
      const leaveHours = Number(item.leave_hours) || 0
      const totalHours = actualHours + leaveHours
      const studentName = students.value.find(s => s.id === item.student_id)?.name || `第${i + 1}个学生`
      if (totalHours !== classHours) {
        $message.warning(`学生「${studentName}」的实际课时(${actualHours}) + 请假课时(${leaveHours}) = ${totalHours}，不等于课时数(${classHours})，请检查`)
        return
      }
    }
  }
  baseHandleSave()
}

// 编辑上课记录
async function handleEdit(row) {
  // 转换日期字符串为时间戳
  const formData = { ...row }
  if (formData.class_date && typeof formData.class_date === 'string') {
    formData.class_date = new Date(formData.class_date).getTime()
  }
  // 转换时间字符串为时间戳
  if (formData.start_time && typeof formData.start_time === 'string') {
    const [hours, minutes] = formData.start_time.split(':').map(Number)
    const date = new Date()
    date.setHours(hours, minutes, 0, 0)
    formData.start_time = date.getTime()
  }
  if (formData.end_time && typeof formData.end_time === 'string') {
    const [hours, minutes] = formData.end_time.split(':').map(Number)
    const date = new Date()
    date.setHours(hours, minutes, 0, 0)
    formData.end_time = date.getTime()
  }
  baseHandleEdit(formData)
  
  // 加载考勤列表
  const res = await educationApi.getClassRecordById({ record_id: row.id })
  attendanceList.value = (res.data?.attendances || []).map(att => ({
    student_id: att.student_id,
    actual_hours: att.actual_hours,
    leave_hours: att.leave_hours,
    leave_reason: att.leave_reason || '',
  }))
}

onMounted(async () => {
  $table.value?.handleSearch()
  const [courseRes, studentRes] = await Promise.all([
    educationApi.getActiveCourses(),
    educationApi.getActiveStudents(),
  ])
  courses.value = courseRes.data || []
  students.value = studentRes.data || []
})

// 监听弹窗关闭，重置表单
watch(modalVisible, (val) => {
  if (!val) {
    // 弹窗关闭时重置时间字段为 null
    modalForm.value.start_time = null
    modalForm.value.end_time = null
    modalForm.value.class_date = null
  }
})

const columns = [
  {
    title: '课程',
    key: 'course_name',
    width: 120,
    align: 'center',
  },
  {
    title: '授课老师',
    key: 'teacher',
    width: 80,
    align: 'center',
  },
  {
    title: '上课日期',
    key: 'class_date',
    width: 100,
    align: 'center',
  },
  {
    title: '开始时间',
    key: 'start_time',
    width: 80,
    align: 'center',
  },
  {
    title: '结束时间',
    key: 'end_time',
    width: 80,
    align: 'center',
  },
  {
    title: '课时数',
    key: 'class_hours',
    width: 60,
    align: 'center',
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    align: 'center',
    fixed: 'right',
    render(row) {
      return [
        withDirectives(
          h(NButton, { size: 'small', type: 'primary', style: 'margin-right: 8px;', onClick: () => handleEdit(row) }, { default: () => '编辑' }),
          [[vPermission, 'post/api/v1/education/class-records/update']]
        ),
        withDirectives(
          h(NButton, { size: 'small', type: 'info', style: 'margin-right: 8px;', onClick: () => viewDetail(row) }, { default: () => '详情' }),
          [[vPermission, 'get/api/v1/education/class-records/get']]
        ),
        h(
          NPopconfirm,
          { onPositiveClick: () => handleDelete({ record_id: row.id }, false) },
          {
            trigger: () => withDirectives(h(NButton, { size: 'small', type: 'error' }, { default: () => '删除' }), [[vPermission, 'delete/api/v1/education/class-records/delete']]),
            default: () => h('div', {}, '确定删除该记录吗?'),
          }
        ),
      ]
    },
  },
]

const attendanceColumns = [
  { title: '学生', key: 'student_name', width: 120, render: (row) => students.value.find(s => s.id === row.student_id)?.name || '' },
  { 
    title: '实际课时', 
    key: 'actual_hours', 
    width: 100, 
    render: (row, i) => h(NInputNumber, { 
      value: Number(row.actual_hours) || 0, 
      min: 0, 
      max: Number(modalForm.value?.class_hours) || 1,
      step: 0.5,
      precision: 1,
      style: { width: '80px' },
      onUpdateValue: (v) => { 
        attendanceList.value[i].actual_hours = v
      } 
    }) 
  },
  { 
    title: '请假课时', 
    key: 'leave_hours', 
    width: 100, 
    render: (row, i) => h(NInputNumber, { 
      value: Number(row.leave_hours) || 0, 
      min: 0, 
      max: (Number(modalForm.value?.class_hours) || 1) - (Number(row.actual_hours) || 0),
      step: 0.5,
      precision: 1,
      style: { width: '80px' },
      onUpdateValue: (v) => { 
        attendanceList.value[i].leave_hours = v
      } 
    }) 
  },
  { title: '请假原因', key: 'leave_reason', width: 150, render: (row, i) => h(NInput, { value: row.leave_reason || '', placeholder: '请输入原因', onUpdateValue: (v) => { attendanceList.value[i].leave_reason = v } }) },
  { 
    title: '操作', 
    key: 'actions', 
    width: 80,
    render: (row, i) => h(NButton, { size: 'small', type: 'error', onClick: () => removeStudent(i) }, { default: () => '移除' })
  },
]

// 添加学生到考勤列表
function addStudent(studentId) {
  if (!studentId) return
  // 检查是否已存在
  if (attendanceList.value.some(a => a.student_id === studentId)) {
    $message.warning('该学生已在列表中')
    return
  }
  attendanceList.value.push({
    student_id: studentId,
    actual_hours: modalForm.value.class_hours || 1,
    leave_hours: 0,
    leave_reason: '',
  })
  selectedStudent.value = null
}

// 移除学生
function removeStudent(index) {
  attendanceList.value.splice(index, 1)
}

// 获取可选的学生列表（排除已添加的）
const availableStudents = computed(() => {
  const addedIds = attendanceList.value.map(a => a.student_id)
  return students.value.filter(s => !addedIds.includes(s.id))
})

// 详情弹窗
const detailModalVisible = ref(false)
const detailData = ref({})

// 批量新增弹窗
const batchModalVisible = ref(false)
const batchForm = ref({ course_id: null, start_time: null, end_time: null, class_hours: 1, content: '' })
const batchAttendanceList = ref([])
const batchSelectedStudent = ref(null)
// 多选日期
const selectedDates = ref([])
const calendarValue = ref(new Date())

async function viewDetail(row) {
  const res = await educationApi.getClassRecordById({ record_id: row.id })
  detailData.value = res.data || {}
  detailModalVisible.value = true
}

function handleAddNew() {
  modalForm.value = { course_id: null, class_date: null, start_time: null, end_time: null, class_hours: 1, content: '', attendances: [] }
  attendanceList.value = []
  handleAdd()
}

async function onCourseChange(courseId) {
  // 清空当前考勤列表
  attendanceList.value = []
  if (courseId) {
    // 自动加载课程学生
    const res = await educationApi.getCourseStudents(courseId)
    const defaultHours = modalForm.value.class_hours || 1
    attendanceList.value = (res.data || []).map(s => ({
      student_id: s.student_id,
      actual_hours: defaultHours,
      leave_hours: 0,
      leave_reason: '',
    }))
  }
}

const rules = {
  course_id: [{ required: true, type: 'number', message: '请选择课程' }],
  class_date: [{ required: true, message: '请选择上课日期' }],
}

// 批量新增相关函数
function handleBatchAdd() {
  batchForm.value = { course_id: null, start_time: null, end_time: null, class_hours: 1, content: '' }
  batchAttendanceList.value = []
  selectedDates.value = []
  batchModalVisible.value = true
}

// 日历点击处理 - 多选日期
function handleCalendarClick(date) {
  const dateStr = dayjs(date).format('YYYY-MM-DD')
  const index = selectedDates.value.indexOf(dateStr)
  if (index > -1) {
    // 已选中则取消
    selectedDates.value.splice(index, 1)
  } else {
    // 未选中且少于10个则添加
    if (selectedDates.value.length < 10) {
      selectedDates.value.push(dateStr)
      selectedDates.value.sort() // 保持日期有序
    } else {
      $message.warning('最多只能选择10个日期')
    }
  }
}

// 判断日期是否被选中
function isDateSelected(date) {
  const dateStr = dayjs(date).format('YYYY-MM-DD')
  return selectedDates.value.includes(dateStr)
}

// 移除已选日期
function removeSelectedDate(dateStr) {
  const index = selectedDates.value.indexOf(dateStr)
  if (index > -1) {
    selectedDates.value.splice(index, 1)
  }
}

async function onBatchCourseChange(courseId) {
  batchAttendanceList.value = []
  if (courseId) {
    const res = await educationApi.getCourseStudents(courseId)
    const defaultHours = batchForm.value.class_hours || 1
    batchAttendanceList.value = (res.data || []).map(s => ({
      student_id: s.student_id,
      actual_hours: defaultHours,
      leave_hours: 0,
      leave_reason: '',
    }))
  }
}

function addBatchStudent(studentId) {
  if (!studentId) return
  if (batchAttendanceList.value.some(a => a.student_id === studentId)) {
    $message.warning('该学生已在列表中')
    return
  }
  batchAttendanceList.value.push({
    student_id: studentId,
    actual_hours: batchForm.value.class_hours || 1,
    leave_hours: 0,
    leave_reason: '',
  })
  batchSelectedStudent.value = null
}

function removeBatchStudent(index) {
  batchAttendanceList.value.splice(index, 1)
}

const availableBatchStudents = computed(() => {
  const addedIds = batchAttendanceList.value.map(a => a.student_id)
  return students.value.filter(s => !addedIds.includes(s.id))
})

async function submitBatchCreate() {
  if (!batchForm.value.course_id) {
    $message.warning('请选择课程')
    return
  }
  
  if (selectedDates.value.length === 0) {
    $message.warning('请至少选择一个上课日期')
    return
  }
  
  const classDates = [...selectedDates.value]
  
  // 验证学生考勤
  const classHours = Number(batchForm.value.class_hours) || 0
  for (let i = 0; i < batchAttendanceList.value.length; i++) {
    const item = batchAttendanceList.value[i]
    const actualHours = Number(item.actual_hours) || 0
    const leaveHours = Number(item.leave_hours) || 0
    const totalHours = actualHours + leaveHours
    const studentName = students.value.find(s => s.id === item.student_id)?.name || `第${i + 1}个学生`
    if (totalHours !== classHours) {
      $message.warning(`学生「${studentName}」的实际课时(${actualHours}) + 请假课时(${leaveHours}) = ${totalHours}，不等于课时数(${classHours})，请检查`)
      return
    }
  }
  
  // 转换时间（使用本地时间）
  let startTime = null
  let endTime = null
  if (batchForm.value.start_time && typeof batchForm.value.start_time === 'number') {
    const date = new Date(batchForm.value.start_time)
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    startTime = `${hours}:${minutes}`
  }
  if (batchForm.value.end_time && typeof batchForm.value.end_time === 'number') {
    const date = new Date(batchForm.value.end_time)
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    endTime = `${hours}:${minutes}`
  }
  
  try {
    await educationApi.batchCreateClassRecord({
      course_id: batchForm.value.course_id,
      class_dates: classDates,
      teacher: null,
      start_time: startTime,
      end_time: endTime,
      class_hours: batchForm.value.class_hours,
      content: batchForm.value.content,
      attendances: batchAttendanceList.value,
    })
    $message.success('批量创建成功')
    batchModalVisible.value = false
    $table.value?.handleSearch()
  } catch (e) {
    $message.error('批量创建失败')
  }
}

// 批量新增考勤表格列
const batchAttendanceColumns = [
  { title: '学生', key: 'student_name', width: 100, render: (row) => students.value.find(s => s.id === row.student_id)?.name || '' },
  { 
    title: '实际课时', 
    key: 'actual_hours', 
    width: 100, 
    render: (row, i) => h(NInputNumber, { 
      value: Number(row.actual_hours) || 0, 
      min: 0, 
      max: (Number(batchForm.value?.class_hours) || 1) - (Number(row.leave_hours) || 0),
      step: 0.5,
      precision: 1,
      style: { width: '80px' },
      onUpdateValue: (v) => { 
        batchAttendanceList.value[i].actual_hours = v
      } 
    }) 
  },
  { 
    title: '请假课时', 
    key: 'leave_hours', 
    width: 100, 
    render: (row, i) => h(NInputNumber, { 
      value: Number(row.leave_hours) || 0, 
      min: 0, 
      max: (Number(batchForm.value?.class_hours) || 1) - (Number(row.actual_hours) || 0),
      step: 0.5,
      precision: 1,
      style: { width: '80px' },
      onUpdateValue: (v) => { 
        batchAttendanceList.value[i].leave_hours = v
      } 
    }) 
  },
  { title: '请假原因', key: 'leave_reason', width: 150, render: (row, i) => h(NInput, { value: row.leave_reason || '', placeholder: '请输入原因', onUpdateValue: (v) => { batchAttendanceList.value[i].leave_reason = v } }) },
  { 
    title: '操作', 
    key: 'actions', 
    width: 80,
    render: (row, i) => h(NButton, { size: 'small', type: 'error', onClick: () => removeBatchStudent(i) }, { default: () => '移除' })
  },
]
</script>

<template>
  <CommonPage show-footer title="上课记录">
    <template #action>
      <NButton v-permission="'post/api/v1/education/class-records/batch-create'" type="info" @click="handleBatchAdd" style="margin-right: 8px;">
        <TheIcon icon="material-symbols:add-box" :size="18" class="mr-5" />批量新增
      </NButton>
      <NButton v-permission="'post/api/v1/education/class-records/create'" type="primary" @click="handleAddNew">
        <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />新建记录
      </NButton>
    </template>

    <CrudTable ref="$table" v-model:query-items="queryItems" :columns="columns" :get-data="educationApi.getClassRecordList">
      <template #queryBar>
        <QueryBarItem label="课程" :label-width="40">
          <NSelect v-model:value="queryItems.course_id" :options="courses.map(c => ({ label: c.name, value: c.id }))" clearable placeholder="选择课程" />
        </QueryBarItem>
        <QueryBarItem label="日期范围" :label-width="60">
          <NDatePicker v-model:value="queryItems.dateRange" type="daterange" clearable />
        </QueryBarItem>
      </template>
    </CrudTable>

    <CrudModal v-model:visible="modalVisible" :title="modalTitle" :loading="modalLoading" @save="handleSave" style="width: 800px">
      <NForm ref="modalFormRef" label-placement="left" label-align="left" :label-width="80" :model="modalForm" :rules="rules">
        <NFormItem label="课程" path="course_id">
          <NSelect v-model:value="modalForm.course_id" :options="courses.map(c => ({ label: c.name, value: c.id }))" placeholder="选择课程" @update:value="onCourseChange" />
        </NFormItem>
        <NFormItem label="上课日期" path="class_date">
          <NDatePicker v-model:value="modalForm.class_date" type="date" clearable />
        </NFormItem>
        <NFormItem label="开始时间" path="start_time">
          <NTimePicker v-model:value="modalForm.start_time" format="HH:mm" clearable />
        </NFormItem>
        <NFormItem label="结束时间" path="end_time">
          <NTimePicker v-model:value="modalForm.end_time" format="HH:mm" clearable />
        </NFormItem>
        <NFormItem label="课时数" path="class_hours">
          <NInputNumber v-model:value="modalForm.class_hours" :min="0" :precision="1" />
        </NFormItem>
        <NFormItem label="上课内容" path="content">
          <NInput v-model:value="modalForm.content" type="textarea" clearable placeholder="请输入上课内容" />
        </NFormItem>
        <NFormItem label="学生考勤">
          <div class="w-full">
            <div class="mb-2 flex gap-2 items-center">
              <NSelect 
                v-model:value="selectedStudent" 
                :options="availableStudents.map(s => ({ label: s.name, value: s.id }))" 
                clearable 
                filterable
                placeholder="选择学生添加" 
                style="width: 200px" 
                @update:value="addStudent"
              />
              <span class="text-gray-400 text-sm">选择课程后自动加载学生，也可手动添加/移除</span>
            </div>
            <NDataTable :columns="attendanceColumns" :data="attendanceList" :bordered="false" size="small" />
          </div>
        </NFormItem>
      </NForm>
    </CrudModal>

    <!-- 详情弹窗 -->
    <NModal v-model:show="detailModalVisible" preset="card" title="上课记录详情" style="width: 700px">
      <div class="mb-4">
        <p><strong>课程：</strong>{{ detailData.course_name }}</p>
        <p><strong>日期：</strong>{{ detailData.class_date }}</p>
        <p><strong>课时数：</strong>{{ detailData.class_hours }}</p>
        <p><strong>内容：</strong>{{ detailData.content }}</p>
      </div>
      <NDataTable :columns="[{ title: '学生', key: 'student_name' }, { title: '实际课时', key: 'actual_hours' }, { title: '请假课时', key: 'leave_hours' }, { title: '费用', key: 'fee', render: (row) => `¥${Math.max(0, row.fee)}` }]" :data="detailData.attendances || []" :bordered="false" />
    </NModal>

    <!-- 批量新增弹窗 -->
    <NModal v-model:show="batchModalVisible" preset="card" title="批量新增上课记录" style="width: 800px">
      <NForm label-placement="left" label-width="80">
        <NFormItem label="课程" required>
          <NSelect v-model:value="batchForm.course_id" :options="courses.map(c => ({ label: c.name, value: c.id }))" placeholder="选择课程" @update:value="onBatchCourseChange" />
        </NFormItem>
        <NFormItem label="上课日期" required>
          <div class="w-full">
            <div class="mb-2">
              <NCalendar 
                v-model:value="calendarValue"
                class="batch-calendar"
                #default="{ year, month, date }"
              >
                <div 
                  :style="isDateSelected(new Date(year, month - 1, date)) ? { 
                    backgroundColor: '#2080f0', 
                    color: '#fff', 
                    borderRadius: '50%',
                    width: '28px',
                    height: '28px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    margin: 'auto'
                  } : { cursor: 'pointer', width: '28px', height: '28px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: 'auto' }"
                  @click.stop="handleCalendarClick(new Date(year, month - 1, date))"
                >
                  {{ date }}
                </div>
              </NCalendar>
            </div>
            <div class="mt-6 p-3 bg-gray-50 rounded-lg">
              <div class="text-sm text-gray-500" style="margin-bottom: 20px;">已选日期（最多10个）：</div>
              <div class="flex flex-wrap gap-2">
                <NTag 
                  v-for="d in selectedDates" 
                  :key="d" 
                  closable 
                  type="primary" 
                  @close="removeSelectedDate(d)"
                >
                  {{ d }}
                </NTag>
                <span v-if="selectedDates.length === 0" class="text-gray-400 text-sm">点击日历选择日期</span>
              </div>
            </div>
          </div>
        </NFormItem>
        <NFormItem label="开始时间">
          <NTimePicker v-model:value="batchForm.start_time" format="HH:mm" clearable />
        </NFormItem>
        <NFormItem label="结束时间">
          <NTimePicker v-model:value="batchForm.end_time" format="HH:mm" clearable />
        </NFormItem>
        <NFormItem label="课时数">
          <NInputNumber v-model:value="batchForm.class_hours" :min="0" :precision="1" />
        </NFormItem>
        <NFormItem label="上课内容">
          <NInput v-model:value="batchForm.content" type="textarea" clearable placeholder="请输入上课内容" />
        </NFormItem>
        <NFormItem label="学生考勤">
          <div class="w-full">
            <div class="mb-2 flex gap-2 items-center">
              <NSelect 
                v-model:value="batchSelectedStudent" 
                :options="availableBatchStudents.map(s => ({ label: s.name, value: s.id }))" 
                clearable 
                filterable
                placeholder="选择学生添加" 
                style="width: 200px" 
                @update:value="addBatchStudent"
              />
              <span class="text-gray-400 text-sm">选择课程后自动加载学生，也可手动添加/移除</span>
            </div>
            <NDataTable :columns="batchAttendanceColumns" :data="batchAttendanceList" :bordered="false" size="small" />
          </div>
        </NFormItem>
      </NForm>
      <template #footer>
        <div class="flex justify-end gap-2">
          <NButton @click="batchModalVisible = false">取消</NButton>
          <NButton type="primary" @click="submitBatchCreate">批量创建</NButton>
        </div>
      </template>
    </NModal>
  </CommonPage>
</template>

<style scoped>
.batch-calendar :deep(.n-calendar-header__btn) {
  font-size: 13px;
}

.batch-calendar :deep(.n-calendar-header__btn svg) {
  display: none;
}

/* 隐藏默认的日期数字（不影响星期标识） */
.batch-calendar :deep(.n-calendar-date .n-calendar-date__date) {
  display: none;
}
</style>

<style>
.batch-calendar .n-calendar-header__btn:first-of-type::before {
  content: '上个月';
}

.batch-calendar .n-calendar-header__btn:last-of-type::before {
  content: '下个月';
}
</style>
