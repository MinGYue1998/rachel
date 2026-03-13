"""
AI助手数据模型
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


class Message(BaseModel):
    """对话消息"""
    role: Literal["user", "assistant", "system", "tool"] = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")
    tool_call_id: Optional[str] = Field(None, description="工具调用ID（tool角色时使用）")


class ChatRequest(BaseModel):
    """聊天请求"""
    messages: List[Message] = Field(..., description="对话历史")
    session_id: Optional[str] = Field(None, description="会话ID")


class ToolCall(BaseModel):
    """工具调用"""
    id: str = Field(..., description="工具调用ID")
    name: str = Field(..., description="工具名称")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="工具参数")


class ConfirmationRequest(BaseModel):
    """确认请求"""
    type: Literal["confirmation_required"] = "confirmation_required"
    understanding: str = Field(..., description="用户需求理解")
    operation: Dict[str, Any] = Field(..., description="即将执行的操作")
    consequences: List[str] = Field(default_factory=list, description="操作可能产生的后果")
    message: str = Field(..., description="确认提示消息")


class ConfirmationResponse(BaseModel):
    """用户确认响应"""
    confirmed: bool = Field(..., description="是否确认执行")
    operation_id: str = Field(..., description="操作ID")


class OperationResult(BaseModel):
    """操作执行结果"""
    type: Literal["operation_completed", "operation_failed"] = "operation_completed"
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="结果消息")
    details: Optional[Dict[str, Any]] = Field(None, description="详细结果")


class ChatResponse(BaseModel):
    """聊天响应"""
    type: Literal["text", "confirmation_required", "operation_executing", "operation_completed"] = "text"
    content: Optional[str] = Field(None, description="文本内容")
    data: Optional[Dict[str, Any]] = Field(None, description="结构化数据")
