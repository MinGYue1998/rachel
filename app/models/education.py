from tortoise import fields

from .base import BaseModel, TimestampMixin


class Student(BaseModel, TimestampMixin):
    """学生表"""
    name = fields.CharField(max_length=50, description="学生姓名", index=True)
    gender = fields.CharField(max_length=10, null=True, description="性别")
    birthday = fields.DateField(null=True, description="出生日期")
    phone = fields.CharField(max_length=20, null=True, description="联系电话", index=True)
    guardian = fields.CharField(max_length=50, null=True, description="监护人姓名", index=True)
    guardian_phone = fields.CharField(max_length=20, null=True, description="监护人电话")
    address = fields.CharField(max_length=200, null=True, description="家庭住址")
    remark = fields.TextField(null=True, description="备注")
    is_active = fields.BooleanField(default=True, description="是否在读", index=True)

    class Meta:
        table = "student"


class Course(BaseModel, TimestampMixin):
    """课程表"""
    name = fields.CharField(max_length=100, description="课程名称", index=True)
    unit_price = fields.DecimalField(max_digits=10, decimal_places=2, default=0, description="课时单价")
    teacher = fields.CharField(max_length=50, null=True, description="授课老师", index=True)
    description = fields.TextField(null=True, description="课程描述")
    status = fields.CharField(max_length=20, default="active", description="状态", index=True)

    class Meta:
        table = "course"


class CourseStudent(BaseModel, TimestampMixin):
    """课程学生关联表"""
    course_id = fields.BigIntField(description="课程ID", index=True)
    student_id = fields.BigIntField(description="学生ID", index=True)
    enroll_date = fields.DateField(null=True, description="报名日期")
    discount = fields.DecimalField(max_digits=10, decimal_places=2, default=0, description="优惠金额")
    status = fields.CharField(max_length=20, default="active", description="状态", index=True)

    class Meta:
        table = "course_student"


class ClassRecord(BaseModel, TimestampMixin):
    """上课记录表"""
    course_id = fields.BigIntField(description="课程ID", index=True)
    teacher = fields.CharField(max_length=50, null=True, description="授课老师", index=True)
    class_date = fields.DateField(description="上课日期", index=True)
    start_time = fields.TimeField(null=True, description="开始时间")
    end_time = fields.TimeField(null=True, description="结束时间")
    class_hours = fields.DecimalField(max_digits=5, decimal_places=1, default=0, description="课时数")
    content = fields.TextField(null=True, description="上课内容")

    class Meta:
        table = "class_record"


class ClassAttendance(BaseModel, TimestampMixin):
    """课堂考勤表"""
    class_record_id = fields.BigIntField(description="上课记录ID", index=True)
    student_id = fields.BigIntField(description="学生ID", index=True)
    actual_hours = fields.DecimalField(max_digits=5, decimal_places=1, default=0, description="实际课时")
    leave_hours = fields.DecimalField(max_digits=5, decimal_places=1, default=0, description="请假课时")
    leave_reason = fields.CharField(max_length=200, null=True, description="请假原因")
    fee = fields.DecimalField(max_digits=10, decimal_places=2, default=0, description="产生费用")

    class Meta:
        table = "class_attendance"


class FeeRecord(BaseModel, TimestampMixin):
    """费用记录表"""
    student_id = fields.BigIntField(description="学生ID", index=True)
    course_id = fields.BigIntField(null=True, description="课程ID", index=True)
    fee_type = fields.CharField(max_length=20, description="费用类型", index=True)
    amount = fields.DecimalField(max_digits=10, decimal_places=2, default=0, description="金额")
    ref_type = fields.CharField(max_length=20, null=True, description="关联类型", index=True)
    ref_id = fields.BigIntField(null=True, description="关联记录ID", index=True)
    remark = fields.CharField(max_length=200, null=True, description="备注")

    class Meta:
        table = "fee_record"


class Payment(BaseModel, TimestampMixin):
    """缴费记录表"""
    student_id = fields.BigIntField(description="学生ID", index=True)
    amount = fields.DecimalField(max_digits=10, decimal_places=2, default=0, description="缴费金额")
    payment_method = fields.CharField(max_length=20, default="cash", description="支付方式", index=True)
    payment_time = fields.DatetimeField(description="缴费时间", index=True)
    remark = fields.CharField(max_length=200, null=True, description="备注")

    class Meta:
        table = "payment"
