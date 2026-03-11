from fastapi import APIRouter, Query

from app.controllers.education import student_controller
from app.core.dependency import DependAuth
from app.schemas.base import Fail, Success, SuccessExtra
from app.schemas.education import StudentCreate, StudentUpdate

router = APIRouter(dependencies=[DependAuth])


@router.get("/list", summary="学生列表")
async def list_students(
    page: int = Query(1, description="页码"),
    page_size: int = Query(20, description="每页数量"),
    name: str = Query(None, description="学生姓名"),
    phone: str = Query(None, description="联系电话"),
    is_active: bool = Query(None, description="是否在读"),
):
    total, students = await student_controller.search(
        page=page,
        page_size=page_size,
        name=name,
        phone=phone,
        is_active=is_active,
    )
    data = [await obj.to_dict() for obj in students]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get("/get", summary="学生详情")
async def get_student(
    student_id: int = Query(..., description="学生ID"),
):
    student = await student_controller.get(id=student_id)
    data = await student.to_dict()
    return Success(data=data)


@router.get("/detail", summary="学生完整详情（含课程和请假）")
async def get_student_detail(
    student_id: int = Query(..., description="学生ID"),
):
    data = await student_controller.get_student_detail(student_id)
    return Success(data=data)


@router.post("/create", summary="创建学生")
async def create_student(
    student_in: StudentCreate,
):
    student = await student_controller.create(obj_in=student_in)
    return Success(msg="创建成功", data={"id": student.id})


@router.post("/update", summary="更新学生")
async def update_student(
    student_in: StudentUpdate,
):
    await student_controller.update(id=student_in.id, obj_in=student_in)
    return Success(msg="更新成功")


@router.delete("/delete", summary="删除学生")
async def delete_student(
    student_id: int = Query(..., description="学生ID"),
):
    await student_controller.remove(id=student_id)
    return Success(msg="删除成功")


@router.get("/active", summary="所有在读学生")
async def get_active_students():
    students = await student_controller.get_active_students()
    data = [{"id": s.id, "name": s.name, "phone": s.phone} for s in students]
    return Success(data=data)
