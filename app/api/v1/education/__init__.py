from fastapi import APIRouter

from .class_records import router as class_records_router
from .courses import router as courses_router
from .fees import router as fees_router
from .payments import router as payments_router
from .reports import router as reports_router
from .students import router as students_router

router = APIRouter(prefix="/education", tags=["教培管理"])

router.include_router(students_router, prefix="/students", tags=["学生管理"])
router.include_router(courses_router, prefix="/courses", tags=["课程管理"])
router.include_router(class_records_router, prefix="/class-records", tags=["上课记录"])
router.include_router(fees_router, prefix="/fees", tags=["费用管理"])
router.include_router(payments_router, prefix="/payments", tags=["缴费管理"])
router.include_router(reports_router, prefix="/reports", tags=["统计报表"])
