"""
AI聊天API
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.core.dependency import DependAuth
from agent import AIService, ToolExecutor
from agent.schemas import ChatRequest, ConfirmationResponse
from agent.tools import TOOLS

router = APIRouter()


@router.post("/chat", summary="AI对话")
async def chat(
    request: ChatRequest,
    current_user = DependAuth
):
    """
    AI对话接口（流式响应）
    
    支持：
    - 自然语言对话
    - 工具调用（查询类直接执行，写操作需确认）
    - 流式输出
    """
    service = AIService()
    executor = ToolExecutor(current_user.id)
    
    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    
    return StreamingResponse(
        service.chat(messages, current_user.id, executor),
        media_type="application/x-ndjson",
    )


@router.post("/confirm", summary="确认操作")
async def confirm_operation(
    request: ConfirmationResponse,
    current_user = DependAuth
):
    """
    处理用户确认
    
    用户确认或取消待执行的操作
    """
    service = AIService()
    executor = ToolExecutor(current_user.id)
    
    return StreamingResponse(
        service.handle_confirmation(
            operation_id=request.operation_id,
            confirmed=request.confirmed,
            user_id=current_user.id,
            executor=executor
        ),
        media_type="application/x-ndjson",
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
