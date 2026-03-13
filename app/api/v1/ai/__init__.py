"""
AI助手API模块
"""

from fastapi import APIRouter

from .chat import router as chat_router

router = APIRouter(prefix="/ai")
router.include_router(chat_router)

__all__ = ["router"]
