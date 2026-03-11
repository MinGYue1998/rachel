<script setup>
import { h, onMounted, ref, resolveDirective, withDirectives } from 'vue'
import {
  NButton,
  NDataTable,
  NDatePicker,
  NDescriptions,
  NDescriptionsItem,
  NDivider,
  NForm,
  NFormItem,
  NInput,
  NModal,
  NPopconfirm,
  NRadio,
  NRadioGroup,
  NSwitch,
  NTag,
} from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import CrudTable from '@/components/table/CrudTable.vue'

import { formatDate, renderIcon } from '@/utils'
import { useCRUD } from '@/composables'
import educationApi from '@/api/education'
import TheIcon from '@/components/icon/TheIcon.vue'

defineOptions({ name: '学生管理' })

const $table = ref(null)
const queryItems = ref({})
const vPermission = resolveDirective('permission')

const {
  modalVisible,
  modalTitle,
  modalAction,
  modalLoading,
  handleSave: baseHandleSave,
  modalForm,
  modalFormRef,
  handleEdit,
  handleDelete,
  handleAdd,
} = useCRUD({
  name: '学生',
  initForm: {},
  doCreate: educationApi.createStudent,
  doUpdate: educationApi.updateStudent,
  doDelete: educationApi.deleteStudent,
  refresh: () => $table.value?.handleSearch(),
})

// 学生详情弹窗
const studentDetailVisible = ref(false)
const studentDetail = ref({})

async function viewStudentDetail(studentId) {
  const res = await educationApi.getStudentDetail({ student_id: studentId })
  studentDetail.value = res.data || {}
  studentDetailVisible.value = true
}

// 转换日期格式后保存
function handleSave() {
  const form = { ...modalForm.value }
  // 将时间戳转换为日期字符串（使用本地时间避免时区偏移）
  if (form.birthday && typeof form.birthday === 'number') {
    const date = new Date(form.birthday)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    form.birthday = `${year}-${month}-${day}`
  }
  modalForm.value = form
  baseHandleSave()
}

onMounted(() => {
  $table.value?.handleSearch()
})

const columns = [
  {
    title: '姓名',
    key: 'name',
    width: 80,
    align: 'center',
    render: (row) => h(NButton, { text: true, type: 'primary', onClick: () => viewStudentDetail(row.id) }, { default: () => row.name }),
  },
  {
    title: '性别',
    key: 'gender',
    width: 60,
    align: 'center',
  },
  {
    title: '出生日期',
    key: 'birthday',
    width: 100,
    align: 'center',
  },
  {
    title: '联系电话',
    key: 'phone',
    width: 100,
    align: 'center',
  },
  {
    title: '监护人',
    key: 'guardian',
    width: 80,
    align: 'center',
  },
  {
    title: '监护人电话',
    key: 'guardian_phone',
    width: 100,
    align: 'center',
  },
  {
    title: '状态',
    key: 'is_active',
    width: 60,
    align: 'center',
    render(row) {
      return h(NTag, { type: row.is_active ? 'success' : 'warning' }, { default: () => row.is_active ? '在读' : '离校' })
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    align: 'center',
    fixed: 'right',
    render(row) {
      return [
        h(NButton, { size: 'small', type: 'info', style: 'margin-right: 8px;', onClick: () => viewStudentDetail(row.id) }, { default: () => '详情' }),
        withDirectives(
          h(
            NButton,
            {
              size: 'small',
              type: 'primary',
              style: 'margin-right: 8px;',
              onClick: () => handleEdit(row),
            },
            { default: () => '编辑', icon: renderIcon('material-symbols:edit', { size: 16 }) }
          ),
          [[vPermission, 'post/api/v1/education/students/update']]
        ),
        h(
          NPopconfirm,
          { onPositiveClick: () => handleDelete({ student_id: row.id }, false) },
          {
            trigger: () =>
              withDirectives(
                h(NButton, { size: 'small', type: 'error' }, { default: () => '删除', icon: renderIcon('material-symbols:delete-outline', { size: 16 }) }),
                [[vPermission, 'delete/api/v1/education/students/delete']]
              ),
            default: () => h('div', {}, '确定删除该学生吗?'),
          }
        ),
      ]
    },
  },
]

const rules = {
  name: [{ required: true, message: '请输入学生姓名', trigger: ['input', 'blur'] }],
}
</script>

<template>
  <CommonPage show-footer title="学生列表">
    <template #action>
      <NButton v-permission="'post/api/v1/education/students/create'" type="primary" @click="handleAdd">
        <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />新建学生
      </NButton>
    </template>

    <CrudTable ref="$table" v-model:query-items="queryItems" :columns="columns" :get-data="educationApi.getStudentList">
      <template #queryBar>
        <QueryBarItem label="姓名" :label-width="40">
          <NInput v-model:value="queryItems.name" clearable placeholder="请输入学生姓名" @keypress.enter="$table?.handleSearch()" />
        </QueryBarItem>
        <QueryBarItem label="电话" :label-width="40">
          <NInput v-model:value="queryItems.phone" clearable placeholder="请输入联系电话" @keypress.enter="$table?.handleSearch()" />
        </QueryBarItem>
      </template>
    </CrudTable>

    <CrudModal v-model:visible="modalVisible" :title="modalTitle" :loading="modalLoading" @save="handleSave">
      <NForm ref="modalFormRef" label-placement="left" label-align="left" :label-width="80" :model="modalForm" :rules="rules">
        <NFormItem label="姓名" path="name">
          <NInput v-model:value="modalForm.name" clearable placeholder="请输入学生姓名" />
        </NFormItem>
        <NFormItem label="性别" path="gender">
          <NRadioGroup v-model:value="modalForm.gender">
            <NRadio value="男">男</NRadio>
            <NRadio value="女">女</NRadio>
          </NRadioGroup>
        </NFormItem>
        <NFormItem label="出生日期" path="birthday">
          <NDatePicker v-model:value="modalForm.birthday" type="date" clearable />
        </NFormItem>
        <NFormItem label="联系电话" path="phone">
          <NInput v-model:value="modalForm.phone" clearable placeholder="请输入联系电话" />
        </NFormItem>
        <NFormItem label="监护人" path="guardian">
          <NInput v-model:value="modalForm.guardian" clearable placeholder="请输入监护人姓名" />
        </NFormItem>
        <NFormItem label="监护人电话" path="guardian_phone">
          <NInput v-model:value="modalForm.guardian_phone" clearable placeholder="请输入监护人电话" />
        </NFormItem>
        <NFormItem label="家庭住址" path="address">
          <NInput v-model:value="modalForm.address" clearable placeholder="请输入家庭住址" />
        </NFormItem>
        <NFormItem label="备注" path="remark">
          <NInput v-model:value="modalForm.remark" type="textarea" clearable placeholder="请输入备注" />
        </NFormItem>
        <NFormItem v-if="modalAction === 'edit'" label="在读状态" path="is_active">
          <NSwitch v-model:value="modalForm.is_active" />
        </NFormItem>
      </NForm>
    </CrudModal>

    <!-- 学生详情弹窗 -->
    <NModal v-model:show="studentDetailVisible" preset="card" title="学生详情" style="width: 800px">
      <NDescriptions label-placement="left" :column="2" bordered>
        <NDescriptionsItem label="姓名">{{ studentDetail.name }}</NDescriptionsItem>
        <NDescriptionsItem label="性别">{{ studentDetail.gender || '-' }}</NDescriptionsItem>
        <NDescriptionsItem label="出生日期">{{ studentDetail.birthday || '-' }}</NDescriptionsItem>
        <NDescriptionsItem label="电话">{{ studentDetail.phone || '-' }}</NDescriptionsItem>
        <NDescriptionsItem label="监护人">{{ studentDetail.guardian || '-' }}</NDescriptionsItem>
        <NDescriptionsItem label="监护人电话">{{ studentDetail.guardian_phone || '-' }}</NDescriptionsItem>
        <NDescriptionsItem label="家庭住址">{{ studentDetail.address || '-' }}</NDescriptionsItem>
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

      <NDivider>课时列表</NDivider>
      <NDataTable :columns="[
        { title: '上课日期', key: 'class_date', width: 100 },
        { title: '课程', key: 'course_name', width: 100 },
        { title: '授课老师', key: 'teacher', width: 80 },
        { title: '实际课时', key: 'actual_hours', width: 80 },
        { title: '请假课时', key: 'leave_hours', width: 80 },
        { title: '费用', key: 'fee', width: 80, render: (row) => `¥${row.fee}` },
      ]" :data="studentDetail.class_hours_list || []" :bordered="false" size="small" :max-height="200" />

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
