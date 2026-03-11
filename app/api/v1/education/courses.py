from fastapi import APIRouter, Query

from app.controllers.education import course_controller
from app.core.dependency import DependAuth
from app.schemas.base import Fail, Success, SuccessExtra
from app.schemas.education import CourseCreate, CourseStudentCreate, CourseStudentUpdate, CourseUpdate

router = APIRouter(dependencies=[DependAuth])


@router.get("/list", summary="课程列表")
async def list_courses(
    page: int = Query(1, description="页码"),
    page_size: int = Query(20, description="每页数量"),
    name: str = Query(None, description="课程名称"),
    teacher: str = Query(None, description="授课老师"),
    status: str = Query(None, description="状态"),
):
    total, courses = await course_controller.search(
        page=page,
        page_size=page_size,
        name=name,
        teacher=teacher,
        status=status,
    )
    data = [await obj.to_dict() for obj in courses]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get("/get", summary="课程详情")
async def get_course(
    course_id: int = Query(..., description="课程ID"),
):
    course = await course_controller.get(id=course_id)
    data = await course.to_dict()
    return Success(data=data)


@router.post("/create", summary="创建课程")
async def create_course(
    course_in: CourseCreate,
):
    course = await course_controller.create(obj_in=course_in)
    return Success(msg="创建成功", data={"id": course.id})


@router.post("/update", summary="更新课程")
async def update_course(
    course_in: CourseUpdate,
):
    await course_controller.update(id=course_in.id, obj_in=course_in)
    return Success(msg="更新成功")


@router.delete("/delete", summary="删除课程")
async def delete_course(
    course_id: int = Query(..., description="课程ID"),
):
    await course_controller.remove(id=course_id)
    return Success(msg="删除成功")


@router.get("/{course_id}/students", summary="课程学生列表")
async def get_course_students(
    course_id: int,
):
    students = await course_controller.get_course_students(course_id)
    return Success(data=students)


@router.post("/{course_id}/students", summary="添加学生到课程")
async def add_student_to_course(
    course_id: int,
    data: CourseStudentCreate,
):
    cs = await course_controller.add_student(course_id, data)
    return Success(msg="添加成功", data={"id": cs.id})


@router.delete("/{course_id}/students/{student_id}", summary="从课程移除学生")
async def remove_student_from_course(
    course_id: int,
    student_id: int,
):
    await course_controller.remove_student(course_id, student_id)
    return Success(msg="移除成功")


@router.put("/{course_id}/students/{student_id}", summary="更新课程学生优惠金额")
async def update_course_student(
    course_id: int,
    student_id: int,
    data: CourseStudentUpdate,
):
    cs = await course_controller.update_student(course_id, student_id, data.discount)
    return Success(msg="更新成功", data={"id": cs.id})


@router.get("/active", summary="所有启用的课程")
async def get_active_courses():
    courses = await course_controller.get_active_courses()
    data = [{"id": c.id, "name": c.name, "unit_price": float(c.unit_price), "teacher": c.teacher} for c in courses]
    return Success(data=data)
