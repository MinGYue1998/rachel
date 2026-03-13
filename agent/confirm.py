"""
用户确认机制
管理写操作的确认流程
"""

import uuid
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from .tools import is_write_tool, get_tool_by_name


class PendingOperation:
    """待确认的操作"""
    
    def __init__(self, tool_name: str, arguments: Dict[str, Any], user_id: int):
        self.id = str(uuid.uuid4())[:8]  # 短ID便于展示
        self.tool_name = tool_name
        self.arguments = arguments
        self.user_id = user_id
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(minutes=5)  # 5分钟过期
        self.confirmed = False
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }


class ConfirmationManager:
    """确认管理器"""
    
    def __init__(self):
        # 内存中存储待确认操作，实际生产环境应使用Redis
        self._pending: Dict[str, PendingOperation] = {}
    
    def create_confirmation(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        user_id: int
    ) -> Dict[str, Any]:
        """
        创建确认请求
        
        Returns:
            确认请求消息，包含：
            - type: confirmation_required
            - understanding: 对需求的理解
            - operation: 操作详情
            - consequences: 可能产生的后果
            - message: 确认提示
        """
        # 创建待确认操作
        pending = PendingOperation(tool_name, arguments, user_id)
        self._pending[pending.id] = pending
        
        # 生成确认消息
        return self._generate_confirmation_message(pending)
    
    def _generate_confirmation_message(self, pending: PendingOperation) -> Dict[str, Any]:
        """生成确认消息"""
        tool_name = pending.tool_name
        args = pending.arguments
        
        # 获取工具定义
        tool_def = get_tool_by_name(tool_name)
        tool_desc = tool_def.get("function", {}).get("description", "")
        
        # 生成需求理解
        understanding = self._generate_understanding(tool_name, args)
        
        # 生成后果说明
        consequences = self._generate_consequences(tool_name, args)
        
        return {
            "type": "confirmation_required",
            "operation_id": pending.id,
            "understanding": understanding,
            "operation": {
                "action": tool_name,
                "params": args,
                "description": tool_desc.split("【")[0].strip() if "【" in tool_desc else tool_desc
            },
            "consequences": consequences,
            "message": "请确认是否执行此操作？",
            "expires_at": pending.expires_at.isoformat()
        }
    
    def _generate_understanding(self, tool_name: str, args: Dict[str, Any]) -> str:
        """生成对需求的理解"""
        
        if tool_name == "create_class_record":
            student = args.get("student_name", "未知")
            course = args.get("course_name", "未知")
            date = args.get("class_date", "今天")
            hours = args.get("class_hours", 0)
            return f"您想要为 {student} 在 {course} 课程中添加一次 {hours} 课时的上课记录（{date}）"
        
        elif tool_name == "batch_create_class_records":
            count = len(args.get("records", []))
            return f"您想要批量创建 {count} 条上课记录"
        
        elif tool_name == "update_student_discount":
            student = args.get("student_name", "未知")
            course = args.get("course_name", "未知")
            discount = args.get("discount", 0)
            return f"您想要将 {student} 在 {course} 课程的优惠金额设置为 ¥{discount:.2f}"
        
        elif tool_name == "create_payment":
            student = args.get("student_name", "未知")
            amount = args.get("amount", 0)
            method = args.get("payment_method", "现金")
            method_map = {
                "cash": "现金",
                "wechat": "微信",
                "alipay": "支付宝",
                "bank_transfer": "银行转账"
            }
            return f"您想要为 {student} 登记一笔 {method_map.get(method, method)} 缴费，金额 ¥{amount:.2f}"
        
        return f"您想要执行 {tool_name} 操作"
    
    def _generate_consequences(self, tool_name: str, args: Dict[str, Any]) -> List[str]:
        """生成操作可能产生的后果"""
        
        consequences = []
        
        if tool_name == "create_class_record":
            student = args.get("student_name", "该学生")
            hours = args.get("class_hours", 0)
            consequences = [
                f"将为 {student} 创建一条新的上课记录",
                f"{student} 的课程将增加 {hours} 课时",
                "将产生相应的课时费用"
            ]
        
        elif tool_name == "batch_create_class_records":
            count = len(args.get("records", []))
            total_hours = sum(r.get("class_hours", 0) for r in args.get("records", []))
            consequences = [
                f"将批量创建 {count} 条上课记录",
                f"总计将增加 {total_hours} 课时",
                "将产生相应的课时费用"
            ]
        
        elif tool_name == "update_student_discount":
            student = args.get("student_name", "该学生")
            discount = args.get("discount", 0)
            consequences = [
                f"将更新 {student} 的优惠金额",
                f"新的优惠金额为 ¥{discount:.2f}",
                "这将影响该学生的费用计算"
            ]
        
        elif tool_name == "create_payment":
            student = args.get("student_name", "该学生")
            amount = args.get("amount", 0)
            consequences = [
                f"将为 {student} 登记一笔缴费记录",
                f"缴费金额为 ¥{amount:.2f}",
                f"{student} 的欠费金额将相应减少"
            ]
        
        return consequences
    
    def confirm_operation(self, operation_id: str, user_id: int) -> Optional[PendingOperation]:
        """
        确认操作
        
        Returns:
            PendingOperation: 确认成功，返回操作信息
            None: 确认失败（不存在、已过期或不属于该用户）
        """
        pending = self._pending.get(operation_id)
        
        if not pending:
            return None
        
        if pending.is_expired():
            del self._pending[operation_id]
            return None
        
        if pending.user_id != user_id:
            return None
        
        pending.confirmed = True
        return pending
    
    def cancel_operation(self, operation_id: str, user_id: int) -> bool:
        """取消操作"""
        pending = self._pending.get(operation_id)
        
        if not pending or pending.user_id != user_id:
            return False
        
        del self._pending[operation_id]
        return True
    
    def get_pending_operation(self, operation_id: str) -> Optional[PendingOperation]:
        """获取待确认操作"""
        pending = self._pending.get(operation_id)
        
        if pending and pending.is_expired():
            del self._pending[operation_id]
            return None
        
        return pending
    
    def cleanup_expired(self):
        """清理过期的待确认操作"""
        expired_ids = [
            op_id for op_id, op in self._pending.items()
            if op.is_expired()
        ]
        for op_id in expired_ids:
            del self._pending[op_id]


# 全局确认管理器实例
confirmation_manager = ConfirmationManager()
