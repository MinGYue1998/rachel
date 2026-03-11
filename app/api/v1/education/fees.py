from datetime import date
from fastapi import APIRouter, Query

from app.controllers.education import fee_controller
from app.core.dependency import DependAuth
from app.schemas.base import Success, SuccessExtra

router = APIRouter(dependencies=[DependAuth])


@router.get("/records", summary="费用记录列表")
async def list_fee_records(
    page: int = Query(1, description="页码"),
    page_size: int = Query(20, description="每页数量"),
    student_id: int = Query(None, description="学生ID"),
    course_id: int = Query(None, description="课程ID"),
    fee_type: str = Query(None, description="费用类型"),
    start_date: date = Query(None, description="开始日期"),
    end_date: date = Query(None, description="结束日期"),
):
    total, records = await fee_controller.get_fee_records(
        page=page,
        page_size=page_size,
        student_id=student_id,
        course_id=course_id,
        fee_type=fee_type,
        start_date=start_date,
        end_date=end_date,
    )
    
    # 获取学生和课程名称
    from app.models.education import Course, Student
    data = []
    for obj in records:
        obj_dict = await obj.to_dict()
        student = await Student.get_or_none(id=obj.student_id)
        course = await Course.get_or_none(id=obj.course_id) if obj.course_id else None
        obj_dict["student_name"] = student.name if student else ""
        obj_dict["course_name"] = course.name if course else ""
        data.append(obj_dict)
    
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get("/summary", summary="学生费用汇总")
async def get_fee_summary(
    student_id: int = Query(None, description="学生ID"),
):
    summary = await fee_controller.get_student_fee_summary(student_id)
    return Success(data=summary)


@router.get("/arrears", summary="欠费学生列表")
async def get_arrears_students():
    arrears = await fee_controller.get_arrears_students()
    return Success(data=arrears)
