<script setup>
import { h, onMounted, ref, resolveDirective, withDirectives } from 'vue'
import {
  NButton,
  NDataTable,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NModal,
  NPopconfirm,
  NSelect,
  NTag,
} from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import CrudTable from '@/components/table/CrudTable.vue'

import { renderIcon } from '@/utils'
import { useCRUD } from '@/composables'
import educationApi from '@/api/education'
import TheIcon from '@/components/icon/TheIcon.vue'

defineOptions({ name: '课程管理' })

const $table = ref(null)
const queryItems = ref({})
const vPermission = resolveDirective('permission')

const {
  modalVisible,
  modalTitle,
  modalAction,
  modalLoading,
  handleSave,
  modalForm,
  modalFormRef,
  handleEdit,
  handleDelete,
  handleAdd,
} = useCRUD({
  name: '课程',
  initForm: {},
  doCreate: educationApi.createCourse,
  doUpdate: educationApi.updateCourse,
  doDelete: educationApi.deleteCourse,
  refresh: () => $table.value?.handleSearch(),
})

// 学生管理相关
const studentModalVisible = ref(false)
const currentCourseId = ref(null)
const courseStudents = ref([])
const allStudents = ref([])
const addStudentForm = ref({ student_id: null, discount: 0 })

// 编辑学生优惠金额
const editStudentVisible = ref(false)
const editStudentForm = ref({ student_id: null, discount: 0 })

onMounted(() => {
  $table.value?.handleSearch()
})

const columns = [
  {
    title: '课程名称',
    key: 'name',
    width: 120,
    align: 'center',
  },
  {
    title: '课时单价',
    key: 'unit_price',
    width: 80,
    align: 'center',
    render(row) {
      return `¥${row.unit_price}`
    },
  },
  {
    title: '授课老师',
    key: 'teacher',
    width: 80,
    align: 'center',
  },
  {
    title: '状态',
    key: 'status',
    width: 60,
    align: 'center',
    render(row) {
      return h(NTag, { type: row.status === 'active' ? 'success' : 'warning' }, { default: () => row.status === 'active' ? '启用' : '停用' })
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    align: 'center',
    fixed: 'right',
    render(row) {
      return [
        withDirectives(
          h(NButton, { size: 'small', type: 'info', style: 'margin-right: 8px;', onClick: () => openStudentModal(row) }, { default: () => '学生' }),
          [[vPermission, 'get/api/v1/education/courses/{course_id}/students']]
        ),
        withDirectives(
          h(NButton, { size: 'small', type: 'primary', style: 'margin-right: 8px;', onClick: () => handleEdit(row) }, { default: () => '编辑' }),
          [[vPermission, 'post/api/v1/education/courses/update']]
        ),
        h(
          NPopconfirm,
          { onPositiveClick: () => handleDelete({ course_id: row.id }, false) },
          {
            trigger: () => withDirectives(h(NButton, { size: 'small', type: 'error' }, { default: () => '删除' }), [[vPermission, 'delete/api/v1/education/courses/delete']]),
            default: () => h('div', {}, '确定删除该课程吗?'),
          }
        ),
      ]
    },
  },
]

const studentColumns = [
  { title: '学生姓名', key: 'student_name', width: 100 },
  { title: '联系电话', key: 'phone', width: 100 },
  { title: '报名日期', key: 'enroll_date', width: 100 },
  { title: '优惠金额', key: 'discount', width: 80, render: (row) => `¥${row.discount || 0}` },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    render(row) {
      return [
        h(NButton, { size: 'small', type: 'primary', style: 'margin-right: 8px;', onClick: () => openEditStudent(row) }, { default: () => '编辑' }),
        h(NPopconfirm, { onPositiveClick: () => removeStudent(row.student_id) }, {
          trigger: () => h(NButton, { size: 'small', type: 'error' }, { default: () => '移除' }),
          default: () => h('div', {}, '确定移除该学生吗?'),
        }),
      ]
    },
  },
]

async function openStudentModal(row) {
  currentCourseId.value = row.id
  const [studentsRes, courseStudentsRes] = await Promise.all([
    educationApi.getActiveStudents(),
    educationApi.getCourseStudents(row.id),
  ])
  allStudents.value = studentsRes.data || []
  courseStudents.value = courseStudentsRes.data || []
  studentModalVisible.value = true
}

async function addStudent() {
  if (!addStudentForm.value.student_id) return
  await educationApi.addStudentToCourse(currentCourseId.value, addStudentForm.value)
  addStudentForm.value = { student_id: null, discount: 0 }
  const res = await educationApi.getCourseStudents(currentCourseId.value)
  courseStudents.value = res.data || []
}

async function removeStudent(studentId) {
  await educationApi.removeStudentFromCourse(currentCourseId.value, studentId)
  const res = await educationApi.getCourseStudents(currentCourseId.value)
  courseStudents.value = res.data || []
}

function openEditStudent(row) {
  editStudentForm.value = { student_id: row.student_id, discount: row.discount || 0 }
  editStudentVisible.value = true
}

async function saveEditStudent() {
  await educationApi.updateCourseStudent(currentCourseId.value, editStudentForm.value.student_id, { discount: editStudentForm.value.discount })
  editStudentVisible.value = false
  const res = await educationApi.getCourseStudents(currentCourseId.value)
  courseStudents.value = res.data || []
}

const rules = {
  name: [{ required: true, message: '请输入课程名称', trigger: ['input', 'blur'] }],
  unit_price: [{ required: true, type: 'number', message: '请输入课时单价', trigger: ['input', 'blur'] }],
}
</script>

<template>
  <CommonPage show-footer title="课程列表">
    <template #action>
      <NButton v-permission="'post/api/v1/education/courses/create'" type="primary" @click="handleAdd">
        <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />新建课程
      </NButton>
    </template>

    <CrudTable ref="$table" v-model:query-items="queryItems" :columns="columns" :get-data="educationApi.getCourseList">
      <template #queryBar>
        <QueryBarItem label="课程名称" :label-width="60">
          <NInput v-model:value="queryItems.name" clearable placeholder="请输入课程名称" @keypress.enter="$table?.handleSearch()" />
        </QueryBarItem>
        <QueryBarItem label="老师" :label-width="40">
          <NInput v-model:value="queryItems.teacher" clearable placeholder="请输入授课老师" @keypress.enter="$table?.handleSearch()" />
        </QueryBarItem>
      </template>
    </CrudTable>

    <CrudModal v-model:visible="modalVisible" :title="modalTitle" :loading="modalLoading" @save="handleSave">
      <NForm ref="modalFormRef" label-placement="left" label-align="left" :label-width="80" :model="modalForm" :rules="rules">
        <NFormItem label="课程名称" path="name">
          <NInput v-model:value="modalForm.name" clearable placeholder="请输入课程名称" />
        </NFormItem>
        <NFormItem label="课时单价" path="unit_price">
          <NInputNumber v-model:value="modalForm.unit_price" :min="0" :precision="2" clearable placeholder="请输入课时单价" />
        </NFormItem>
        <NFormItem label="授课老师" path="teacher">
          <NInput v-model:value="modalForm.teacher" clearable placeholder="请输入授课老师" />
        </NFormItem>
        <NFormItem label="课程描述" path="description">
          <NInput v-model:value="modalForm.description" type="textarea" clearable placeholder="请输入课程描述" />
        </NFormItem>
        <NFormItem v-if="modalAction === 'edit'" label="状态" path="status">
          <NSelect v-model:value="modalForm.status" :options="[{ label: '启用', value: 'active' }, { label: '停用', value: 'inactive' }]" />
        </NFormItem>
      </NForm>
    </CrudModal>

    <!-- 学生管理弹窗 -->
    <NModal v-model:show="studentModalVisible" preset="card" title="课程学生管理" style="width: 700px">
      <div class="mb-4 flex gap-2 items-center">
        <NSelect v-model:value="addStudentForm.student_id" :options="allStudents.map(s => ({ label: s.name, value: s.id }))" placeholder="选择学生" clearable filterable style="width: 150px" />
        <span class="text-gray-500">优惠金额：</span>
        <NInputNumber v-model:value="addStudentForm.discount" :min="0" :precision="2" placeholder="0" style="width: 120px">
          <template #prefix>¥</template>
        </NInputNumber>
        <NButton type="primary" @click="addStudent">添加学生</NButton>
      </div>
      <NDataTable :columns="studentColumns" :data="courseStudents" :bordered="false" />
    </NModal>

    <!-- 编辑学生优惠金额弹窗 -->
    <NModal v-model:show="editStudentVisible" preset="card" title="编辑优惠金额" style="width: 400px">
      <NForm label-placement="left" label-width="80">
        <NFormItem label="优惠金额">
          <NInputNumber v-model:value="editStudentForm.discount" :min="0" :precision="2" placeholder="0" style="width: 200px">
            <template #prefix>¥</template>
          </NInputNumber>
        </NFormItem>
      </NForm>
      <template #footer>
        <div class="flex justify-end gap-2">
          <NButton @click="editStudentVisible = false">取消</NButton>
          <NButton type="primary" @click="saveEditStudent">保存</NButton>
        </div>
      </template>
    </NModal>
  </CommonPage>
</template>
