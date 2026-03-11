from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Tuple

from fastapi.exceptions import HTTPException
from tortoise.expressions import Q

from app.core.crud import CRUDBase
from app.models.education import (
    ClassAttendance,
    ClassRecord,
    Course,
    CourseStudent,
    FeeRecord,
    Payment,
    Student,
)
from app.schemas.education import (
    AttendanceCreate,
    ClassRecordCreate,
    ClassRecordUpdate,
    CourseCreate,
    CourseStudentCreate,
    CourseUpdate,
    FeeType,
    PaymentCreate,
    StudentCreate,
    StudentUpdate,
)


class StudentController(CRUDBase[Student, StudentCreate, StudentUpdate]):
    def __init__(self):
        super().__init__(model=Student)

    async def get_active_students(self) -> List[Student]:
        """获取所有在读学生"""
        return await self.model.filter(is_active=True).all()

    async def search(
        self, page: int, page_size: int, name: str = None, phone: str = None, is_active: bool = None
    ) -> Tuple[int, List[Student]]:
        """搜索学生"""
        q = Q()
        if name:
            q &= Q(name__contains=name)
        if phone:
            q &= Q(phone__contains=phone)
        if is_active is not None:
            q &= Q(is_active=is_active)
        return await self.list(page=page, page_size=page_size, search=q, order=["-created_at"])

    async def get_student_detail(self, student_id: int) -> dict:
        """获取学生详情（包含课程和请假记录）"""
        student = await self.get(id=student_id)
        student_dict = await student.to_dict()
        
        # 获取学生所有课程
        course_students = await CourseStudent.filter(student_id=student_id).all()
        courses = []
        for cs in course_students:
            course = await Course.get_or_none(id=cs.course_id)
            if course:
                # 计算该课程的总课时和费用
                attendances = await ClassAttendance.filter(student_id=student_id).all()
                total_hours = sum(float(a.actual_hours) for a in attendances)
                # 获取该课程的课时
                course_hours = 0
                for att in attendances:
                    cr = await ClassRecord.get_or_none(id=att.class_record_id)
                    if cr and cr.course_id == course.id:
                        course_hours += float(att.actual_hours)
                
                # 费用 = 课时 * 单价 - 优惠金额
                discount = float(cs.discount) if cs.discount else 0
                total_fee = course_hours * float(course.unit_price) - discount
                
                courses.append({
                    "id": course.id,
                    "name": course.name,
                    "teacher": course.teacher,
                    "unit_price": float(course.unit_price),
                    "discount": discount,
                    "total_hours": course_hours,
                    "total_fee": max(0, total_fee),
                    "enroll_date": cs.enroll_date.isoformat() if cs.enroll_date else None,
                    "status": cs.status,
                })
        
        # 获取学生请假记录
        attendances = await ClassAttendance.filter(student_id=student_id, leave_hours__gt=0).all()
        leave_records = []
        for att in attendances:
            class_record = await ClassRecord.get_or_none(id=att.class_record_id)
            if class_record:
                course = await Course.get_or_none(id=class_record.course_id)
                leave_records.append({
                    "id": att.id,
                    "class_date": class_record.class_date.isoformat(),
                    "course_name": course.name if course else "",
                    "leave_hours": float(att.leave_hours),
                    "leave_reason": att.leave_reason,
                })
        
        # 获取缴费记录
        payments = await Payment.filter(student_id=student_id).order_by("-payment_time").all()
        payment_records = []
        for p in payments:
            payment_records.append({
                "id": p.id,
                "amount": float(p.amount),
                "payment_method": p.payment_method,
                "payment_time": p.payment_time.isoformat() if p.payment_time else None,
                "remark": p.remark,
            })
        
        # 获取费用汇总
        fee_summary = await fee_controller.get_student_fee_summary(student_id)
        
        # 获取课时列表（时间倒序）
        all_attendances = await ClassAttendance.filter(student_id=student_id).all()
        class_hours_list = []
        for att in all_attendances:
            class_record = await ClassRecord.get_or_none(id=att.class_record_id)
            if class_record:
                course = await Course.get_or_none(id=class_record.course_id)
                class_hours_list.append({
                    "id": att.id,
                    "class_date": class_record.class_date.isoformat(),
                    "course_name": course.name if course else "",
                    "teacher": class_record.teacher,
                    "actual_hours": float(att.actual_hours),
                    "leave_hours": float(att.leave_hours),
                    "fee": float(att.fee),
                })
        # 按日期倒序排列
        class_hours_list.sort(key=lambda x: x["class_date"], reverse=True)
        
        student_dict["courses"] = courses
        student_dict["leave_records"] = leave_records
        student_dict["payment_records"] = payment_records
        student_dict["fee_summary"] = fee_summary[0] if fee_summary else None
        student_dict["class_hours_list"] = class_hours_list
        
        return student_dict


class CourseController(CRUDBase[Course, CourseCreate, CourseUpdate]):
    def __init__(self):
        super().__init__(model=Course)

    async def get_active_courses(self) -> List[Course]:
        """获取所有启用的课程"""
        return await self.model.filter(status="active").all()

    async def search(
        self, page: int, page_size: int, name: str = None, teacher: str = None, status: str = None
    ) -> Tuple[int, List[Course]]:
        """搜索课程"""
        q = Q()
        if name:
            q &= Q(name__contains=name)
        if teacher:
            q &= Q(teacher__contains=teacher)
        if status:
            q &= Q(status=status)
        return await self.list(page=page, page_size=page_size, search=q, order=["-created_at"])

    async def add_student(self, course_id: int, data: CourseStudentCreate) -> CourseStudent:
        """添加学生到课程"""
        # 检查是否已存在
        existing = await CourseStudent.filter(
            course_id=course_id, student_id=data.student_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="该学生已在课程中")
        
        cs = CourseStudent(
            course_id=course_id,
            student_id=data.student_id,
            enroll_date=data.enroll_date or date.today(),
            discount=data.discount,
            status="active",
        )
        await cs.save()
        return cs

    async def remove_student(self, course_id: int, student_id: int) -> None:
        """从课程移除学生"""
        cs = await CourseStudent.filter(
            course_id=course_id, student_id=student_id
        ).first()
        if not cs:
            raise HTTPException(status_code=404, detail="未找到该学生的课程记录")
        await cs.delete()

    async def update_student(self, course_id: int, student_id: int, discount) -> CourseStudent:
        """更新课程学生的优惠金额"""
        cs = await CourseStudent.filter(
            course_id=course_id, student_id=student_id
        ).first()
        if not cs:
            raise HTTPException(status_code=404, detail="未找到该学生的课程记录")
        cs.discount = discount
        await cs.save()
        return cs

    async def get_course_students(self, course_id: int) -> List[dict]:
        """获取课程的学生列表"""
        course_students = await CourseStudent.filter(
            course_id=course_id, status="active"
        ).all()
        
        result = []
        for cs in course_students:
            student = await Student.get(id=cs.student_id)
            result.append({
                "id": cs.id,
                "student_id": student.id,
                "student_name": student.name,
                "phone": student.phone,
                "guardian": student.guardian,
                "enroll_date": cs.enroll_date.isoformat() if cs.enroll_date else None,
                "discount": float(cs.discount) if cs.discount else 0,
                "status": cs.status,
            })
        return result


class ClassRecordController(CRUDBase[ClassRecord, ClassRecordCreate, ClassRecordUpdate]):
    def __init__(self):
        super().__init__(model=ClassRecord)

    async def search(
        self,
        page: int,
        page_size: int,
        course_id: int = None,
        teacher: str = None,
        class_date_start: date = None,
        class_date_end: date = None,
    ) -> Tuple[int, List[ClassRecord]]:
        """搜索上课记录"""
        q = Q()
        if course_id:
            q &= Q(course_id=course_id)
        if teacher:
            q &= Q(teacher__contains=teacher)
        if class_date_start:
            q &= Q(class_date__gte=class_date_start)
        if class_date_end:
            q &= Q(class_date__lte=class_date_end)
        return await self.list(page=page, page_size=page_size, search=q, order=["-class_date", "-created_at"])

    async def create_with_attendance(self, data: ClassRecordCreate) -> ClassRecord:
        """创建上课记录并处理考勤"""
        # 获取课程信息
        course = await Course.get(id=data.course_id)
        
        # 创建上课记录
        record = ClassRecord(
            course_id=data.course_id,
            teacher=data.teacher or course.teacher,
            class_date=data.class_date,
            start_time=data.start_time,
            end_time=data.end_time,
            class_hours=data.class_hours,
            content=data.content,
        )
        await record.save()

        # 处理考勤记录
        for attendance in data.attendances:
            await self._process_attendance(record, attendance, course.unit_price)

        return record

    async def batch_create(self, data: "ClassRecordBatchCreate") -> List[ClassRecord]:
        """批量创建上课记录"""
        from app.schemas.education import ClassRecordBatchCreate
        
        # 获取课程信息
        course = await Course.get(id=data.course_id)
        
        records = []
        for class_date in data.class_dates:
            # 创建上课记录
            record = ClassRecord(
                course_id=data.course_id,
                teacher=data.teacher or course.teacher,
                class_date=class_date,
                start_time=data.start_time,
                end_time=data.end_time,
                class_hours=data.class_hours,
                content=data.content,
            )
            await record.save()

            # 处理考勤记录
            for attendance in data.attendances:
                await self._process_attendance(record, attendance, course.unit_price)
            
            records.append(record)

        return records

    async def _process_attendance(
        self, record: ClassRecord, attendance: AttendanceCreate, unit_price: Decimal
    ) -> ClassAttendance:
        """处理单条考勤记录"""
        # 计算费用 = 实际课时 * 单价（请假不扣费，只是记录）
        fee = attendance.actual_hours * unit_price

        # 创建考勤记录
        ca = ClassAttendance(
            class_record_id=record.id,
            student_id=attendance.student_id,
            actual_hours=attendance.actual_hours,
            leave_hours=attendance.leave_hours,
            leave_reason=attendance.leave_reason,
            fee=fee,
        )
        await ca.save()

        # 创建费用记录（只有费用大于0才记录）
        if fee > 0:
            fee_record = FeeRecord(
                student_id=attendance.student_id,
                course_id=record.course_id,
                fee_type=FeeType.CLASS_FEE,
                amount=fee,
                ref_type="class_attendance",
                ref_id=ca.id,
            )
            await fee_record.save()

        return ca

    async def update_with_attendance(self, record_id: int, data: ClassRecordUpdate) -> ClassRecord:
        """更新上课记录和考勤"""
        record = await self.get(id=record_id)
        
        # 更新上课记录基本信息
        if data.teacher is not None:
            record.teacher = data.teacher
        if data.class_date is not None:
            record.class_date = data.class_date
        if data.start_time is not None:
            record.start_time = data.start_time
        if data.end_time is not None:
            record.end_time = data.end_time
        if data.class_hours is not None:
            record.class_hours = data.class_hours
        if data.content is not None:
            record.content = data.content
        await record.save()
        
        # 如果提供了考勤数据，更新考勤记录
        if data.attendances:
            course = await Course.get(id=record.course_id)
            
            # 获取现有考勤记录
            existing_attendances = await ClassAttendance.filter(class_record_id=record_id).all()
            existing_map = {att.student_id: att for att in existing_attendances}
            
            for attendance in data.attendances:
                if attendance.student_id in existing_map:
                    # 更新现有考勤记录
                    att = existing_map[attendance.student_id]
                    old_actual_hours = float(att.actual_hours)
                    att.actual_hours = attendance.actual_hours
                    att.leave_hours = attendance.leave_hours
                    att.leave_reason = attendance.leave_reason
                    att.fee = attendance.actual_hours * course.unit_price
                    await att.save()
                    
                    # 更新费用记录
                    fee_diff = float(att.fee) - (old_actual_hours * float(course.unit_price))
                    if fee_diff != 0:
                        fee_record = await FeeRecord.filter(
                            ref_type="class_attendance",
                            ref_id=att.id
                        ).first()
                        if fee_record:
                            fee_record.amount = att.fee
                            await fee_record.save()
        
        return record

    async def get_detail(self, record_id: int) -> dict:
        """获取上课记录详情（含考勤）"""
        record = await self.get(id=record_id)
        attendances = await ClassAttendance.filter(class_record_id=record_id).all()
        
        # 获取学生姓名
        result = {
            "id": record.id,
            "course_id": record.course_id,
            "teacher": record.teacher,
            "class_date": record.class_date.isoformat(),
            "start_time": str(record.start_time) if record.start_time else None,
            "end_time": str(record.end_time) if record.end_time else None,
            "class_hours": float(record.class_hours),
            "content": record.content,
            "created_at": record.created_at.isoformat(),
            "updated_at": record.updated_at.isoformat(),
            "attendances": [],
        }
        
        for att in attendances:
            student = await Student.get(id=att.student_id)
            result["attendances"].append({
                "id": att.id,
                "student_id": att.student_id,
                "student_name": student.name,
                "actual_hours": float(att.actual_hours),
                "leave_hours": float(att.leave_hours),
                "leave_reason": att.leave_reason,
                "fee": float(att.fee),
            })
        
        return result


class FeeController:
    """费用控制器"""

    async def get_fee_records(
        self,
        page: int,
        page_size: int,
        student_id: int = None,
        course_id: int = None,
        fee_type: str = None,
        start_date: date = None,
        end_date: date = None,
    ) -> Tuple[int, List[FeeRecord]]:
        """获取费用记录（默认只显示课时费，不显示缴费）"""
        q = Q(fee_type="class_fee")  # 默认只显示课时费
        if student_id:
            q &= Q(student_id=student_id)
        if course_id:
            q &= Q(course_id=course_id)
        if fee_type:
            q = Q(fee_type=fee_type)  # 如果指定了类型，则按指定类型查询
            if student_id:
                q &= Q(student_id=student_id)
            if course_id:
                q &= Q(course_id=course_id)
        if start_date:
            q &= Q(created_at__gte=start_date)
        if end_date:
            from datetime import datetime, timedelta
            end_datetime = datetime.combine(end_date, datetime.max.time())
            q &= Q(created_at__lte=end_datetime)
        
        total = await FeeRecord.filter(q).count()
        records = await FeeRecord.filter(q).offset((page - 1) * page_size).limit(page_size).order_by("-created_at")
        return total, records

    async def get_student_fee_summary(self, student_id: int = None) -> List[dict]:
        """获取学生费用汇总"""
        query = """
            SELECT 
                s.id as student_id,
                s.name as student_name,
                COALESCE(SUM(CASE WHEN fr.fee_type = 'class_fee' THEN fr.amount ELSE 0 END), 0) as total_fee,
                COALESCE(SUM(CASE WHEN fr.fee_type = 'payment' THEN ABS(fr.amount) ELSE 0 END), 0) as total_paid,
                COALESCE(SUM(CASE WHEN fr.fee_type = 'class_fee' THEN fr.amount ELSE 0 END), 0) - 
                COALESCE(SUM(CASE WHEN fr.fee_type = 'payment' THEN ABS(fr.amount) ELSE 0 END), 0) as balance_before_discount,
                COALESCE((SELECT SUM(discount) FROM course_student WHERE student_id = s.id), 0) as total_discount
            FROM student s
            LEFT JOIN fee_record fr ON s.id = fr.student_id
            WHERE s.is_active = 1
        """
        if student_id:
            query += f" AND s.id = {student_id}"
        query += " GROUP BY s.id, s.name ORDER BY balance_before_discount DESC"
        
        from tortoise import Tortoise
        conn = Tortoise.get_connection("default")
        results = await conn.execute_query(query)
        
        return [
            {
                "student_id": row["student_id"],
                "student_name": row["student_name"],
                "total_fee": float(row["total_fee"]),
                "total_paid": float(row["total_paid"]),
                "total_discount": float(row["total_discount"]),
                "balance": float(row["balance_before_discount"]) - float(row["total_discount"]),
            }
            for row in results[1]
        ]

    async def get_arrears_students(self) -> List[dict]:
        """获取欠费学生列表"""
        summary = await self.get_student_fee_summary()
        return [s for s in summary if s["balance"] > 0]


class PaymentController(CRUDBase[Payment, PaymentCreate, PaymentCreate]):
    def __init__(self):
        super().__init__(model=Payment)

    async def search(
        self,
        page: int,
        page_size: int,
        student_id: int = None,
        payment_method: str = None,
        start_date: date = None,
        end_date: date = None,
    ) -> Tuple[int, List[Payment]]:
        """搜索缴费记录"""
        q = Q()
        if student_id:
            q &= Q(student_id=student_id)
        if payment_method:
            q &= Q(payment_method=payment_method)
        if start_date:
            q &= Q(payment_time__gte=start_date)
        if end_date:
            from datetime import datetime
            end_datetime = datetime.combine(end_date, datetime.max.time())
            q &= Q(payment_time__lte=end_datetime)
        return await self.list(page=page, page_size=page_size, search=q, order=["-payment_time"])

    async def create_payment(self, data: PaymentCreate) -> Payment:
        """创建缴费记录"""
        # 创建缴费记录
        payment = await self.create(data)
        
        # 创建费用记录（缴费为负数）
        fee_record = FeeRecord(
            student_id=data.student_id,
            fee_type=FeeType.PAYMENT,
            amount=-data.amount,
            ref_type="payment",
            ref_id=payment.id,
            remark=data.remark,
        )
        await fee_record.save()
        
        return payment


class ReportController:
    """报表控制器"""

    async def get_monthly_report(self, year: int = None, month: int = None) -> List[dict]:
        """获取月度报表"""
        from tortoise import connections
        
        where_clause = ""
        if year and month:
            where_clause = f"WHERE YEAR(created_at) = {year} AND MONTH(created_at) = {month}"
        elif year:
            where_clause = f"WHERE YEAR(created_at) = {year}"
        
        query = f"""
            SELECT 
                DATE_FORMAT(created_at, '%Y-%m') as month,
                SUM(CASE WHEN fee_type = 'class_fee' THEN amount ELSE 0 END) as total_class_fee,
                SUM(CASE WHEN fee_type = 'payment' THEN ABS(amount) ELSE 0 END) as total_payment,
                COUNT(DISTINCT CASE WHEN fee_type = 'class_fee' THEN ref_id END) as class_count,
                COUNT(DISTINCT student_id) as student_count
            FROM fee_record
            {where_clause}
            GROUP BY DATE_FORMAT(created_at, '%Y-%m')
            ORDER BY month DESC
        """
        
        from tortoise import Tortoise
        conn = Tortoise.get_connection("default")
        results = await conn.execute_query(query)
        
        return [
            {
                "month": row["month"],
                "total_class_fee": float(row["total_class_fee"]),
                "total_payment": float(row["total_payment"]),
                "class_count": row["class_count"],
                "student_count": row["student_count"],
            }
            for row in results[1]
        ]

    async def get_student_detail_report(
        self, student_id: int = None, course_id: int = None, year: int = None, month: int = None
    ) -> List[dict]:
        """获取学生明细报表（只显示有课时消费的学生）"""
        from tortoise import Tortoise
        
        conditions = ["fr.fee_type = 'class_fee'"]  # 只显示课时费记录
        if student_id:
            conditions.append(f"fr.student_id = {student_id}")
        if course_id:
            conditions.append(f"fr.course_id = {course_id}")
        if year and month:
            conditions.append(f"YEAR(fr.created_at) = {year} AND MONTH(fr.created_at) = {month}")
        elif year:
            conditions.append(f"YEAR(fr.created_at) = {year}")
        elif month:
            conditions.append(f"MONTH(fr.created_at) = {month}")
        
        where_clause = "WHERE " + " AND ".join(conditions)
        
        query = f"""
            SELECT 
                s.id as student_id,
                s.name as student_name,
                c.name as course_name,
                COUNT(DISTINCT ca.id) as class_count,
                COALESCE(SUM(ca.actual_hours), 0) as total_hours,
                COALESCE(SUM(fr.amount), 0) as total_fee,
                (SELECT COALESCE(SUM(ABS(fr2.amount)), 0) FROM fee_record fr2 WHERE fr2.student_id = s.id AND fr2.fee_type = 'payment') as total_paid,
                (SELECT COALESCE(SUM(discount), 0) FROM course_student cs WHERE cs.student_id = s.id) as total_discount
            FROM student s
            JOIN fee_record fr ON s.id = fr.student_id
            JOIN course c ON fr.course_id = c.id
            LEFT JOIN class_attendance ca ON fr.ref_id = ca.id AND fr.ref_type = 'class_attendance'
            {where_clause}
            GROUP BY s.id, s.name, c.name
            ORDER BY total_fee DESC
        """
        
        conn = Tortoise.get_connection("default")
        results = await conn.execute_query(query)
        
        return [
            {
                "student_id": row["student_id"],
                "student_name": row["student_name"],
                "course_name": row["course_name"],
                "class_count": row["class_count"],
                "total_hours": float(row["total_hours"]),
                "total_fee": float(row["total_fee"]),
                "total_paid": float(row["total_paid"]),
                "total_discount": float(row["total_discount"]),
                "balance": float(row["total_fee"]) - float(row["total_paid"]) - float(row["total_discount"]),
            }
            for row in results[1]
        ]


# 实例化控制器
student_controller = StudentController()
course_controller = CourseController()
class_record_controller = ClassRecordController()
fee_controller = FeeController()
payment_controller = PaymentController()
report_controller = ReportController()
