"""
AI聊天API
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.core.dependency import DependAuth
from app.core.ctx import CTX_USER_ID
from agent import AIService, ToolExecutor
from agent.schemas import ChatRequest, ConfirmationResponse
from agent.tools import TOOLS

router = APIRouter()


def get_current_user_id() -> int:
    """获取当前用户ID"""
    return CTX_USER_ID.get() or 0


@router.post("/chat", summary="AI对话")
async def chat(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id)
):
    """
    AI对话接口（流式响应）
    
    支持：
    - 自然语言对话
    - 工具调用（查询类直接执行，写操作需确认）
    - 流式输出
    """
    service = AIService()
    executor = ToolExecutor(user_id)
    
    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    
    return StreamingResponse(
        service.chat(messages, user_id, executor),
        media_type="text/event-stream",
    )


@router.post("/confirm", summary="确认操作")
async def confirm_operation(
    request: ConfirmationResponse,
    user_id: int = Depends(get_current_user_id)
):
    """
    处理用户确认
    
    用户确认或取消待执行的操作
    """
    service = AIService()
    executor = ToolExecutor(user_id)
    
    return StreamingResponse(
        service.handle_confirmation(
            operation_id=request.operation_id,
            confirmed=request.confirmed,
            user_id=user_id,
            executor=executor
        ),
        media_type="text/event-stream",
    )


@router.get("/tools", summary="获取可用工具列表")
async def get_tools():
    """获取所有可用的工具列表"""
    return {
        "tools": [
            {
                "name": tool["function"]["name"],
                "description": tool["function"]["description"],
            }
            for tool in TOOLS
        ]
    }
