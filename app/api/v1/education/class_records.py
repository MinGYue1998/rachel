from datetime import date

from fastapi import APIRouter, Query

from app.controllers.education import class_record_controller
from app.core.dependency import DependAuth
from app.schemas.base import Fail, Success, SuccessExtra
from app.schemas.education import ClassRecordBatchCreate, ClassRecordCreate, ClassRecordUpdate

router = APIRouter(dependencies=[DependAuth])


@router.get("/list", summary="上课记录列表")
async def list_class_records(
    page: int = Query(1, description="页码"),
    page_size: int = Query(20, description="每页数量"),
    course_id: int = Query(None, description="课程ID"),
    teacher: str = Query(None, description="授课老师"),
    class_date_start: date = Query(None, description="开始日期"),
    class_date_end: date = Query(None, description="结束日期"),
):
    total, records = await class_record_controller.search(
        page=page,
        page_size=page_size,
        course_id=course_id,
        teacher=teacher,
        class_date_start=class_date_start,
        class_date_end=class_date_end,
    )
    
    # 获取课程名称
    from app.models.education import Course
    data = []
    for obj in records:
        obj_dict = await obj.to_dict()
        course = await Course.get_or_none(id=obj.course_id)
        obj_dict["course_name"] = course.name if course else ""
        obj_dict["class_date"] = obj.class_date.isoformat()
        data.append(obj_dict)
    
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get("/get", summary="上课记录详情")
async def get_class_record(
    record_id: int = Query(..., description="记录ID"),
):
    data = await class_record_controller.get_detail(record_id)
    return Success(data=data)


@router.post("/create", summary="创建上课记录（结课）")
async def create_class_record(
    record_in: ClassRecordCreate,
):
    record = await class_record_controller.create_with_attendance(record_in)
    return Success(msg="创建成功", data={"id": record.id})


@router.post("/batch-create", summary="批量创建上课记录")
async def batch_create_class_record(
    record_in: ClassRecordBatchCreate,
):
    records = await class_record_controller.batch_create(record_in)
    return Success(msg=f"成功创建 {len(records)} 条记录", data={"ids": [r.id for r in records]})


@router.post("/update", summary="更新上课记录")
async def update_class_record(
    record_in: ClassRecordUpdate,
):
    await class_record_controller.update_with_attendance(record_id=record_in.record_id, data=record_in)
    return Success(msg="更新成功")


@router.delete("/delete", summary="删除上课记录")
async def delete_class_record(
    record_id: int = Query(..., description="记录ID"),
):
    await class_record_controller.remove(id=record_id)
    return Success(msg="删除成功")
