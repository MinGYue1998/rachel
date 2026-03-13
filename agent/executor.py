"""
工具执行器
执行具体的业务工具调用
"""

import json
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import date, datetime


class ToolExecutor:
    """工具执行器"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        # 延迟导入避免循环依赖
        from app.controllers.education import (
            student_controller,
            course_controller,
            class_record_controller,
            fee_controller,
            payment_controller,
            report_controller,
        )
        self._student_controller = student_controller
        self._course_controller = course_controller
        self._class_record_controller = class_record_controller
        self._fee_controller = fee_controller
        self._payment_controller = payment_controller
        self._report_controller = report_controller
    
    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工具
        
        Returns:
            {"success": bool, "message": str, "data": Any}
        """
        method = getattr(self, f"_exec_{tool_name}", None)
        
        if not method:
            return {
                "success": False,
                "message": f"未知工具: {tool_name}",
                "data": None
            }
        
        try:
            result = await method(arguments)
            return result
        except Exception as e:
            return {
                "success": False,
                "message": f"执行失败: {str(e)}",
                "data": None
            }
    
    # ==================== 只读工具 ====================
    
    async def _exec_query_students(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """查询学生列表"""
        name = args.get("name")
        status = args.get("status")
        
        # 构建查询参数
        params = {}
        if name:
            params["name"] = name
        if status:
            params["status"] = status
        
        # 调用控制器
        students = await self._student_controller.get_list(**params)
        
        if not students:
            return {
                "success": True,
                "message": "未找到符合条件的学生",
                "data": []
            }
        
        # 格式化结果
        formatted = [
            {
                "id": s.get("id"),
                "name": s.get("name"),
                "phone": s.get("phone", "-"),
                "status": "在读" if s.get("status") == "active" else "已停用"
            }
            for s in students[:20]  # 最多返回20条
        ]
        
        return {
            "success": True,
            "message": f"找到 {len(students)} 名学生",
            "data": formatted
        }
    
    async def _exec_get_student_detail(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """获取学生详情"""
        student_id = args.get("student_id")
        student_name = args.get("student_name")
        
        # 如果只有姓名，先查询ID
        if not student_id and student_name:
            students = await self._student_controller.get_list(name=student_name)
            if not students:
                return {
                    "success": False,
                    "message": f"未找到学生: {student_name}",
                    "data": None
                }
            student_id = students[0]["id"]
        
        if not student_id:
            return {
                "success": False,
                "message": "请提供学生ID或姓名",
                "data": None
            }
        
        # 获取详情
        detail = await self._student_controller.get_detail(student_id)
        
        if not detail:
            return {
                "success": False,
                "message": "未找到该学生详情",
                "data": None
            }
        
        return {
            "success": True,
            "message": "获取成功",
            "data": detail
        }
    
    async def _exec_query_courses(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """查询课程列表"""
        name = args.get("name")
        
        params = {}
        if name:
            params["name"] = name
        
        courses = await self._course_controller.get_list(**params)
        
        if not courses:
            return {
                "success": True,
                "message": "未找到符合条件的课程",
                "data": []
            }
        
        formatted = [
            {
                "id": c.get("id"),
                "name": c.get("name"),
                "unit_price": float(c.get("unit_price", 0)),
                "status": "启用" if c.get("status") == "active" else "停用"
            }
            for c in courses[:20]
        ]
        
        return {
            "success": True,
            "message": f"找到 {len(courses)} 门课程",
            "data": formatted
        }
    
    async def _exec_query_class_records(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """查询上课记录"""
        student_name = args.get("student_name")
        course_name = args.get("course_name")
        date_from = args.get("date_from")
        date_to = args.get("date_to")
        
        # 构建查询参数
        params = {}
        
        if student_name:
            # 先查询学生ID
            students = await self._student_controller.get_list(name=student_name)
            if students:
                params["student_id"] = students[0]["id"]
        
        if course_name:
            # 先查询课程ID
            courses = await self._course_controller.get_list(name=course_name)
            if courses:
                params["course_id"] = courses[0]["id"]
        
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        
        records = await self._class_record_controller.get_list(**params)
        
        if not records:
            return {
                "success": True,
                "message": "未找到上课记录",
                "data": []
            }
        
        formatted = [
            {
                "id": r.get("id"),
                "student_name": r.get("student_name"),
                "course_name": r.get("course_name"),
                "class_date": r.get("class_date"),
                "class_hours": float(r.get("class_hours", 0)),
                "content": r.get("content", "-")
            }
            for r in records[:50]
        ]
        
        return {
            "success": True,
            "message": f"找到 {len(records)} 条上课记录",
            "data": formatted
        }
    
    async def _exec_query_fees(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """查询费用记录"""
        student_name = args.get("student_name")
        
        params = {}
        if student_name:
            students = await self._student_controller.get_list(name=student_name)
            if students:
                params["student_id"] = students[0]["id"]
        
        records = await self._fee_controller.get_records(**params)
        
        if not records:
            return {
                "success": True,
                "message": "未找到费用记录",
                "data": []
            }
        
        return {
            "success": True,
            "message": f"找到 {len(records)} 条费用记录",
            "data": records[:50]
        }
    
    async def _exec_query_arrears_students(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """查询欠费学生"""
        arrears = await self._fee_controller.get_arrears_students()
        
        if not arrears:
            return {
                "success": True,
                "message": "当前没有欠费学生",
                "data": []
            }
        
        formatted = [
            {
                "student_id": a.get("student_id"),
                "student_name": a.get("student_name"),
                "total_fee": float(a.get("total_fee", 0)),
                "total_paid": float(a.get("total_paid", 0)),
                "total_discount": float(a.get("total_discount", 0)),
                "balance": float(a.get("balance", 0))
            }
            for a in arrears
        ]
        
        return {
            "success": True,
            "message": f"找到 {len(arrears)} 名欠费学生",
            "data": formatted
        }
    
    async def _exec_query_monthly_report(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """查询月度报表"""
        year = args.get("year", datetime.now().year)
        month = args.get("month", datetime.now().month)
        
        report = await self._report_controller.get_monthly_report(year, month)
        
        if not report:
            return {
                "success": True,
                "message": f"{year}年{month}月暂无数据",
                "data": []
            }
        
        return {
            "success": True,
            "message": f"{year}年{month}月报表",
            "data": report
        }
    
    async def _exec_query_student_detail_report(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """查询学生明细报表"""
        student_id = args.get("student_id")
        course_id = args.get("course_id")
        year = args.get("year")
        month = args.get("month")
        
        report = await self._report_controller.get_student_detail_report(
            student_id=student_id,
            course_id=course_id,
            year=year,
            month=month
        )
        
        if not report:
            return {
                "success": True,
                "message": "未找到符合条件的数据",
                "data": []
            }
        
        return {
            "success": True,
            "message": f"找到 {len(report)} 条记录",
            "data": report
        }
    
    # ==================== 写操作工具 ====================
    
    async def _exec_create_class_record(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """创建上课记录"""
        student_name = args.get("student_name")
        course_name = args.get("course_name")
        class_date = args.get("class_date")
        class_hours = args.get("class_hours")
        content = args.get("content", "")
        
        # 查询学生ID
        students = await self._student_controller.get_list(name=student_name)
        if not students:
            return {"success": False, "message": f"未找到学生: {student_name}", "data": None}
        student_id = students[0]["id"]
        
        # 查询课程ID
        courses = await self._course_controller.get_list(name=course_name)
        if not courses:
            return {"success": False, "message": f"未找到课程: {course_name}", "data": None}
        course_id = courses[0]["id"]
        
        # 创建记录
        data = {
            "student_id": student_id,
            "course_id": course_id,
            "class_date": class_date,
            "class_hours": Decimal(str(class_hours)),
            "content": content
        }
        
        result = await self._class_record_controller.create(data)
        
        return {
            "success": True,
            "message": "上课记录创建成功",
            "data": {
                "record_id": result.get("id"),
                "student": student_name,
                "course": course_name,
                "date": class_date,
                "hours": class_hours
            }
        }
    
    async def _exec_batch_create_class_records(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """批量创建上课记录"""
        records = args.get("records", [])
        
        if len(records) > 10:
            return {"success": False, "message": "单次最多批量创建10条记录", "data": None}
        
        created_count = 0
        errors = []
        
        for record in records:
            result = await self._exec_create_class_record(record)
            if result["success"]:
                created_count += 1
            else:
                errors.append(f"{record.get('student_name')}: {result['message']}")
        
        return {
            "success": errors == [],
            "message": f"成功创建 {created_count}/{len(records)} 条记录",
            "data": {"created": created_count, "errors": errors}
        }
    
    async def _exec_update_student_discount(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """更新学生优惠金额"""
        student_name = args.get("student_name")
        course_name = args.get("course_name")
        discount = args.get("discount")
        
        # 查询学生ID
        students = await self._student_controller.get_list(name=student_name)
        if not students:
            return {"success": False, "message": f"未找到学生: {student_name}", "data": None}
        student_id = students[0]["id"]
        
        # 查询课程ID
        courses = await self._course_controller.get_list(name=course_name)
        if not courses:
            return {"success": False, "message": f"未找到课程: {course_name}", "data": None}
        course_id = courses[0]["id"]
        
        # 更新优惠金额
        data = {
            "student_id": student_id,
            "course_id": course_id,
            "discount": Decimal(str(discount))
        }
        
        await self._course_controller.update_student(course_id, student_id, data)
        
        return {
            "success": True,
            "message": "优惠金额更新成功",
            "data": {
                "student": student_name,
                "course": course_name,
                "discount": discount
            }
        }
    
    async def _exec_create_payment(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """登记缴费"""
        student_name = args.get("student_name")
        amount = args.get("amount")
        payment_method = args.get("payment_method")
        remark = args.get("remark", "")
        
        # 查询学生ID
        students = await self._student_controller.get_list(name=student_name)
        if not students:
            return {"success": False, "message": f"未找到学生: {student_name}", "data": None}
        student_id = students[0]["id"]
        
        # 创建缴费记录
        data = {
            "student_id": student_id,
            "amount": Decimal(str(amount)),
            "payment_method": payment_method,
            "remark": remark
        }
        
        result = await self._payment_controller.create(data)
        
        method_map = {
            "cash": "现金",
            "wechat": "微信",
            "alipay": "支付宝",
            "bank_transfer": "银行转账"
        }
        
        return {
            "success": True,
            "message": "缴费登记成功",
            "data": {
                "payment_id": result.get("id"),
                "student": student_name,
                "amount": amount,
                "method": method_map.get(payment_method, payment_method)
            }
        }
