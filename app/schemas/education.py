import sys
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

# Python 3.10 兼容 StrEnum
if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    class StrEnum(str, Enum):
        pass


# ==================== 枚举类型 ====================
class CourseStatus(StrEnum):
    """课程状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class CourseStudentStatus(StrEnum):
    """课程学生状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class FeeType(StrEnum):
    """费用类型"""
    CLASS_FEE = "class_fee"
    PAYMENT = "payment"


class PaymentMethod(StrEnum):
    """支付方式"""
    CASH = "cash"
    WECHAT = "wechat"
    ALIPAY = "alipay"
    BANK = "bank"


# ==================== 学生 Schema ====================
class StudentBase(BaseModel):
    """学生基础信息"""
    name: str = Field(..., max_length=50, description="学生姓名")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    birthday: Optional[date] = Field(None, description="出生日期")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    guardian: Optional[str] = Field(None, max_length=50, description="监护人姓名")
    guardian_phone: Optional[str] = Field(None, max_length=20, description="监护人电话")
    address: Optional[str] = Field(None, max_length=200, description="家庭住址")
    remark: Optional[str] = Field(None, description="备注")


class StudentCreate(StudentBase):
    """创建学生"""
    pass


class StudentUpdate(BaseModel):
    """更新学生"""
    name: Optional[str] = Field(None, max_length=50, description="学生姓名")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    birthday: Optional[date] = Field(None, description="出生日期")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    guardian: Optional[str] = Field(None, max_length=50, description="监护人姓名")
    guardian_phone: Optional[str] = Field(None, max_length=20, description="监护人电话")
    address: Optional[str] = Field(None, max_length=200, description="家庭住址")
    remark: Optional[str] = Field(None, description="备注")
    is_active: Optional[bool] = Field(None, description="是否在读")


class StudentResponse(StudentBase):
    """学生响应"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 课程 Schema ====================
class CourseBase(BaseModel):
    """课程基础信息"""
    name: str = Field(..., max_length=100, description="课程名称")
    unit_price: Decimal = Field(default=Decimal("0.00"), description="课时单价")
    teacher: Optional[str] = Field(None, max_length=50, description="授课老师")
    description: Optional[str] = Field(None, description="课程描述")


class CourseCreate(CourseBase):
    """创建课程"""
    pass


class CourseUpdate(BaseModel):
    """更新课程"""
    name: Optional[str] = Field(None, max_length=100, description="课程名称")
    unit_price: Optional[Decimal] = Field(None, description="课时单价")
    teacher: Optional[str] = Field(None, max_length=50, description="授课老师")
    description: Optional[str] = Field(None, description="课程描述")
    status: Optional[str] = Field(None, description="状态")


class CourseResponse(CourseBase):
    """课程响应"""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 课程学生关联 Schema ====================
class CourseStudentCreate(BaseModel):
    """添加学生到课程"""
    student_id: int = Field(..., description="学生ID")
    enroll_date: Optional[date] = Field(None, description="报名日期")
    discount: Decimal = Field(default=Decimal("0.00"), description="优惠金额")


class CourseStudentUpdate(BaseModel):
    """更新课程学生"""
    discount: Decimal = Field(..., description="优惠金额")


class CourseStudentResponse(BaseModel):
    """课程学生响应"""
    id: int
    course_id: int
    student_id: int
    enroll_date: Optional[date]
    discount: Decimal = Decimal("0.00")
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 上课记录 Schema ====================
class ClassRecordBase(BaseModel):
    """上课记录基础信息"""
    course_id: int = Field(..., description="课程ID")
    teacher: Optional[str] = Field(None, max_length=50, description="授课老师")
    class_date: date = Field(..., description="上课日期")
    start_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
    class_hours: Decimal = Field(default=Decimal("0.0"), description="课时数")
    content: Optional[str] = Field(None, description="上课内容")


class ClassRecordCreate(ClassRecordBase):
    """创建上课记录"""
    attendances: List["AttendanceCreate"] = Field(default_factory=list, description="考勤记录")


class ClassRecordBatchCreate(BaseModel):
    """批量创建上课记录"""
    course_id: int = Field(..., description="课程ID")
    class_dates: List[date] = Field(..., max_length=10, description="上课日期列表(最多10个)")
    teacher: Optional[str] = Field(None, max_length=50, description="授课老师")
    start_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
    class_hours: Decimal = Field(default=Decimal("0.0"), description="课时数")
    content: Optional[str] = Field(None, description="上课内容")
    attendances: List["AttendanceCreate"] = Field(default_factory=list, description="考勤记录")


class ClassRecordUpdate(BaseModel):
    """更新上课记录"""
    record_id: int = Field(..., description="记录ID")
    teacher: Optional[str] = Field(None, max_length=50, description="授课老师")
    class_date: Optional[date] = Field(None, description="上课日期")
    start_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
    class_hours: Optional[Decimal] = Field(None, description="课时数")
    content: Optional[str] = Field(None, description="上课内容")
    attendances: Optional[List["AttendanceCreate"]] = Field(None, description="考勤记录")


class AttendanceCreate(BaseModel):
    """考勤记录创建"""
    student_id: int = Field(..., description="学生ID")
    actual_hours: Decimal = Field(default=Decimal("0.0"), description="实际课时")
    leave_hours: Decimal = Field(default=Decimal("0.0"), description="请假课时")
    leave_reason: Optional[str] = Field(None, max_length=200, description="请假原因")


class AttendanceResponse(BaseModel):
    """考勤记录响应"""
    id: int
    class_record_id: int
    student_id: int
    actual_hours: Decimal
    leave_hours: Decimal
    leave_reason: Optional[str]
    fee: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class ClassRecordResponse(ClassRecordBase):
    """上课记录响应"""
    id: int
    created_at: datetime
    updated_at: datetime
    attendances: List[AttendanceResponse] = []

    class Config:
        from_attributes = True


# ==================== 费用记录 Schema ====================
class FeeRecordBase(BaseModel):
    """费用记录基础信息"""
    student_id: int = Field(..., description="学生ID")
    course_id: Optional[int] = Field(None, description="课程ID")
    fee_type: str = Field(..., description="费用类型")
    amount: Decimal = Field(default=Decimal("0.00"), description="金额")
    ref_type: Optional[str] = Field(None, description="关联类型")
    ref_id: Optional[int] = Field(None, description="关联记录ID")
    remark: Optional[str] = Field(None, max_length=200, description="备注")


class FeeRecordResponse(FeeRecordBase):
    """费用记录响应"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StudentFeeSummary(BaseModel):
    """学生费用汇总"""
    student_id: int
    student_name: str
    total_fee: Decimal = Decimal("0.00")
    total_paid: Decimal = Decimal("0.00")
    balance: Decimal = Decimal("0.00")


# ==================== 缴费记录 Schema ====================
class PaymentBase(BaseModel):
    """缴费记录基础信息"""
    student_id: int = Field(..., description="学生ID")
    amount: Decimal = Field(..., description="缴费金额")
    payment_method: str = Field(default="cash", description="支付方式")
    payment_time: datetime = Field(..., description="缴费时间")
    remark: Optional[str] = Field(None, max_length=200, description="备注")


class PaymentCreate(PaymentBase):
    """创建缴费记录"""
    pass


class PaymentResponse(PaymentBase):
    """缴费记录响应"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 报表 Schema ====================
class MonthlyReport(BaseModel):
    """月度报表"""
    month: str
    total_class_fee: Decimal = Decimal("0.00")
    total_payment: Decimal = Decimal("0.00")
    class_count: int = 0
    student_count: int = 0


class StudentDetailReport(BaseModel):
    """学生明细报表"""
    student_id: int
    student_name: str
    course_name: Optional[str]
    class_count: int = 0
    total_hours: Decimal = Decimal("0.0")
    total_fee: Decimal = Decimal("0.00")
    total_paid: Decimal = Decimal("0.00")
    balance: Decimal = Decimal("0.00")


# 更新前向引用
ClassRecordCreate.model_rebuild()
ClassRecordBatchCreate.model_rebuild()
ClassRecordUpdate.model_rebuild()
ClassRecordResponse.model_rebuild()
