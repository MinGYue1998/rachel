import { request } from '@/utils'

export default {
  // ==================== 学生管理 ====================
  getStudentList: (params = {}) => request.get('/education/students/list', { params }),
  getStudentById: (params = {}) => request.get('/education/students/get', { params }),
  getStudentDetail: (params = {}) => request.get('/education/students/detail', { params }),
  createStudent: (data = {}) => request.post('/education/students/create', data),
  updateStudent: (data = {}) => request.post('/education/students/update', data),
  deleteStudent: (params = {}) => request.delete('/education/students/delete', { params }),
  getActiveStudents: () => request.get('/education/students/active'),

  // ==================== 课程管理 ====================
  getCourseList: (params = {}) => request.get('/education/courses/list', { params }),
  getCourseById: (params = {}) => request.get('/education/courses/get', { params }),
  createCourse: (data = {}) => request.post('/education/courses/create', data),
  updateCourse: (data = {}) => request.post('/education/courses/update', data),
  deleteCourse: (params = {}) => request.delete('/education/courses/delete', { params }),
  getCourseStudents: (courseId) => request.get(`/education/courses/${courseId}/students`),
  addStudentToCourse: (courseId, data) => request.post(`/education/courses/${courseId}/students`, data),
  updateCourseStudent: (courseId, studentId, data) => request.put(`/education/courses/${courseId}/students/${studentId}`, data),
  removeStudentFromCourse: (courseId, studentId) => request.delete(`/education/courses/${courseId}/students/${studentId}`),
  getActiveCourses: () => request.get('/education/courses/active'),

  // ==================== 上课记录 ====================
  getClassRecordList: (params = {}) => request.get('/education/class-records/list', { params }),
  getClassRecordById: (params = {}) => request.get('/education/class-records/get', { params }),
  createClassRecord: (data = {}) => request.post('/education/class-records/create', data),
  batchCreateClassRecord: (data = {}) => request.post('/education/class-records/batch-create', data),
  updateClassRecord: (data = {}) => request.post('/education/class-records/update', data),
  deleteClassRecord: (params = {}) => request.delete('/education/class-records/delete', { params }),

  // ==================== 费用管理 ====================
  getFeeRecordList: (params = {}) => request.get('/education/fees/records', { params }),
  getFeeSummary: (params = {}) => request.get('/education/fees/summary', { params }),
  getArrearsStudents: () => request.get('/education/fees/arrears'),

  // ==================== 缴费管理 ====================
  getPaymentList: (params = {}) => request.get('/education/payments/list', { params }),
  createPayment: (data = {}) => request.post('/education/payments/create', data),
  getStudentPayments: (studentId) => request.get(`/education/payments/student/${studentId}`),

  // ==================== 统计报表 ====================
  getMonthlyReport: (params = {}) => request.get('/education/reports/monthly', { params }),
  getStudentDetailReport: (params = {}) => request.get('/education/reports/student-detail', { params }),
  exportReport: (params = {}) => request.get('/education/reports/export', { params, responseType: 'blob' }),
  exportReportExcel: (params = {}) => request.get('/education/reports/export-excel', { params, responseType: 'blob' }),
}
