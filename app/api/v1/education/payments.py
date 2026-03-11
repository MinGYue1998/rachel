from datetime import date
from fastapi import APIRouter, Query

from app.controllers.education import payment_controller
from app.core.dependency import DependAuth
from app.schemas.base import Success, SuccessExtra
from app.schemas.education import PaymentCreate

router = APIRouter(dependencies=[DependAuth])


@router.get("/list", summary="缴费记录列表")
async def list_payments(
    page: int = Query(1, description="页码"),
    page_size: int = Query(20, description="每页数量"),
    student_id: int = Query(None, description="学生ID"),
    payment_method: str = Query(None, description="支付方式"),
    start_date: date = Query(None, description="开始日期"),
    end_date: date = Query(None, description="结束日期"),
):
    total, payments = await payment_controller.search(
        page=page,
        page_size=page_size,
        student_id=student_id,
        payment_method=payment_method,
        start_date=start_date,
        end_date=end_date,
    )
    
    # 获取学生名称
    from app.models.education import Student
    data = []
    for obj in payments:
        obj_dict = await obj.to_dict()
        student = await Student.get_or_none(id=obj.student_id)
        obj_dict["student_name"] = student.name if student else ""
        data.append(obj_dict)
    
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.post("/create", summary="登记缴费")
async def create_payment(
    payment_in: PaymentCreate,
):
    payment = await payment_controller.create_payment(payment_in)
    return Success(msg="缴费成功", data={"id": payment.id})


@router.get("/student/{student_id}", summary="学生缴费历史")
async def get_student_payments(
    student_id: int,
):
    payments = await payment_controller.model.filter(student_id=student_id).order_by("-payment_time")
    data = [await obj.to_dict() for obj in payments]
    return Success(data=data)
