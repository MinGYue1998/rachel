"""
AI服务层
处理与Qwen模型的交互
"""

import json
from typing import AsyncGenerator, List, Dict, Any, Optional
from openai import AsyncOpenAI

from .schemas import Message, ConfirmationResponse
from .tools import TOOLS, is_write_tool
from .prompts import SYSTEM_PROMPT
from .confirm import confirmation_manager
from .executor import ToolExecutor


class AIService:
    """AI服务"""
    
    def __init__(self):
        # 延迟导入避免循环依赖
        from app.settings import settings
        self.client = AsyncOpenAI(
            api_key=settings.DASHSCOPE_API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.model = settings.QWEN_MODEL
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        user_id: int,
        executor: ToolExecutor
    ) -> AsyncGenerator[str, None]:
        """
        流式对话
        
        Yields:
            SSE格式的数据流
        """
        # 添加系统提示词
        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        
        # 调用模型
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            tools=TOOLS,
            tool_choice="auto",
            stream=True,
        )
        
        # 收集响应内容
        collected_content = ""
        tool_calls = []
        current_tool_call = None
        
        async for chunk in response:
            delta = chunk.choices[0].delta
            
            # 处理文本内容
            if delta.content:
                collected_content += delta.content
                # deep-chat 格式：直接返回文本
                yield json.dumps({'text': delta.content}) + '\n'
            
            # 处理工具调用
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    if tc.index is not None:
                        # 新的工具调用
                        if tc.index >= len(tool_calls):
                            tool_calls.append({
                                "id": "",
                                "name": "",
                                "arguments": ""
                            })
                        current_tool_call = tool_calls[tc.index]
                    
                    if tc.id:
                        current_tool_call["id"] = tc.id
                    if tc.function.name:
                        current_tool_call["name"] = tc.function.name
                    if tc.function.arguments:
                        current_tool_call["arguments"] += tc.function.arguments
        
        # 如果有工具调用，处理它们
        if tool_calls:
            for tc in tool_calls:
                tool_name = tc.get("name", "")
                tool_args = json.loads(tc.get("arguments", "{}"))
                tool_call_id = tc.get("id", "")
                
                # 检查是否为写操作
                if is_write_tool(tool_name):
                    # 生成确认请求
                    confirmation = confirmation_manager.create_confirmation(
                        tool_name=tool_name,
                        arguments=tool_args,
                        user_id=user_id
                    )
                    # deep-chat 格式：返回确认消息文本
                    confirm_text = f"🤔 {confirmation['understanding']}\n\n"
                    confirm_text += f"📋 操作：{confirmation['operation']['action']}\n"
                    confirm_text += f"⚠️ 影响：{', '.join(confirmation['consequences'])}\n\n"
                    confirm_text += f"{confirmation['message']}\n\n"
                    confirm_text += f"📝 操作ID: {confirmation['operation_id']}"
                    yield json.dumps({'text': confirm_text, 'confirmation': confirmation}) + '\n'
                    return
                else:
                    # 只读操作，直接执行
                    yield json.dumps({'text': '\n正在查询...\n'}) + '\n'
                    
                    result = await executor.execute(tool_name, tool_args)
                    
                    # 将工具结果添加到消息历史
                    full_messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [{
                            "id": tool_call_id,
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": json.dumps(tool_args)
                            }
                        }]
                    })
                    full_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": json.dumps(result)
                    })
                    
                    # 再次调用模型生成自然语言回复
                    async for chunk in self._generate_summary(full_messages):
                        yield chunk
    
    async def _generate_summary(
        self,
        messages: List[Dict[str, Any]]
    ) -> AsyncGenerator[str, None]:
        """生成工具执行结果的自然语言总结"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
        )
        
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                # deep-chat 格式
                yield json.dumps({'text': delta.content}) + '\n'
    
    async def handle_confirmation(
        self,
        operation_id: str,
        confirmed: bool,
        user_id: int,
        executor: ToolExecutor
    ) -> AsyncGenerator[str, None]:
        """
        处理用户确认
        
        Args:
            operation_id: 操作ID
            confirmed: 是否确认
            user_id: 用户ID
            executor: 工具执行器
        """
        if not confirmed:
            # 用户取消
            confirmation_manager.cancel_operation(operation_id, user_id)
            yield json.dumps({'text': '❌ 操作已取消'}) + '\n'
            return
        
        # 确认操作
        pending = confirmation_manager.confirm_operation(operation_id, user_id)
        
        if not pending:
            yield json.dumps({'text': '⚠️ 操作已过期或不存在，请重新发起'}) + '\n'
            return
        
        # 执行操作
        yield json.dumps({'text': '\n正在执行操作...\n'}) + '\n'
        
        result = await executor.execute(pending.tool_name, pending.arguments)
        
        # 返回执行结果
        if result["success"]:
            result_text = f"✅ {result['message']}\n"
            if result.get("data"):
                result_text += f"\n{json.dumps(result['data'], ensure_ascii=False, indent=2)}"
            yield json.dumps({'text': result_text}) + '\n'
        else:
            yield json.dumps({'text': f"❌ {result['message']}"}) + '\n'
