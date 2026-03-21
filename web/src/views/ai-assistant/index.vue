<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { NButton, NCard, NSpace, NTag, NAlert, NSpin, NDivider, NIcon, NInput } from 'naive-ui'
import { 
  Bot, 
  MessageCircle, 
  Sparkles, 
  BookOpen, 
  Users, 
  Calendar, 
  Wallet, 
  FileText,
  Send,
  Loader2,
  Check,
  X
} from 'lucide-vue-next'
import VueMarkdownStream from 'vue-markdown-stream'
import 'vue-markdown-stream/dist/index.css'

import CommonPage from '@/components/page/CommonPage.vue'
import { useUserStore } from '@/store'
import { getToken } from '@/utils'

const userStore = useUserStore()
const token = getToken()
const messages = ref([
  {
    role: 'ai',
    content: '您好！我是您的教培管理助手 🤖\n\n我可以帮您管理学生、课程、上课记录和费用。\n\n请问有什么可以帮您？'
  }
])
const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref(null)
const pendingConfirmation = ref(null) // 待确认的操作

// 自动滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 解析确认消息，提取 operation_id
function parseConfirmationMessage(text) {
  // 检查是否是确认请求消息
  if (text.includes('请确认是否执行此操作')) {
    // 从消息中提取 operation_id（后端会在消息中包含）
    // 这里我们假设后端会在流式响应中返回 operation_id
    return true
  }
  return false
}

// 发送消息
async function sendMessage(text = null) {
  const messageText = text || inputMessage.value.trim()
  if (!messageText || isLoading.value) return

  // 添加用户消息
  messages.value.push({ role: 'user', content: messageText })
  inputMessage.value = ''
  scrollToBottom()

  // 准备 AI 回复占位
  const aiMessageIndex = messages.value.length
  messages.value.push({ role: 'ai', content: '' })
  isLoading.value = true

  try {
    // 转换消息格式 - 将 'ai' 转换为 'assistant'
    const requestBody = {
      messages: messages.value
        .filter(m => m.role === 'user' || m.role === 'ai')
        .slice(0, -1) // 排除刚添加的空 AI 消息
        .map(m => ({
          role: m.role === 'ai' ? 'assistant' : m.role,
          content: m.content
        }))
    }

    const response = await fetch('/api/v1/ai/chat', {
      method: 'POST',
      headers: {
        'token': token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    })

    if (!response.ok) {
      throw new Error('请求失败')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let fullText = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line.trim()) continue
        try {
          const data = JSON.parse(line)
          if (data.text) {
            fullText += data.text
            messages.value[aiMessageIndex].content = fullText
            scrollToBottom()
          }
          // 处理确认请求
          if (data.confirmation) {
            pendingConfirmation.value = data.confirmation
            messages.value[aiMessageIndex].confirmation = data.confirmation
          }
        } catch (e) {
          console.error('解析响应失败:', e, line)
        }
      }
    }
  } catch (error) {
    messages.value[aiMessageIndex].content = '❌ ' + (error.message || '请求失败')
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

// 确认操作
async function confirmOperation(confirmed, confirmation = null) {
  // 如果没有传入 confirmation，使用全局 pendingConfirmation
  const confirmationData = confirmation || pendingConfirmation.value
  if (!confirmationData) return
  
  const operationId = confirmationData.operation_id
  // 清除全局 pendingConfirmation
  if (pendingConfirmation.value?.operation_id === operationId) {
    pendingConfirmation.value = null
  }
  
  // 清除消息中的 confirmation，防止重复点击
  const msgIndex = messages.value.findIndex(m => m.confirmation?.operation_id === operationId)
  if (msgIndex !== -1) {
    messages.value[msgIndex].confirmation = null
  }
  
  // 添加用户消息
  const confirmText = confirmed ? '✅ 确认执行' : '❌ 取消操作'
  messages.value.push({ role: 'user', content: confirmText })
  scrollToBottom()
  
  // 准备 AI 回复占位
  const aiMessageIndex = messages.value.length
  messages.value.push({ role: 'ai', content: '' })
  isLoading.value = true
  
  try {
    const response = await fetch('/api/v1/ai/confirm', {
      method: 'POST',
      headers: {
        'token': token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        operation_id: operationId,
        confirmed: confirmed
      })
    })
    
    if (!response.ok) {
      throw new Error('请求失败')
    }
    
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let fullText = ''
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      
      for (const line of lines) {
        if (!line.trim()) continue
        try {
          const data = JSON.parse(line)
          if (data.text) {
            fullText += data.text
            messages.value[aiMessageIndex].content = fullText
            scrollToBottom()
          }
        } catch (e) {
          console.error('解析响应失败:', e, line)
        }
      }
    }
  } catch (error) {
    messages.value[aiMessageIndex].content = '❌ ' + (error.message || '请求失败')
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

// 处理回车发送
function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// 使用示例问题
function askExample(question) {
  inputMessage.value = question
  sendMessage()
}

// 示例问题分类
const exampleCategories = [
  {
    icon: Users,
    title: '学生管理',
    color: '#52c41a',
    questions: ['有哪些学生？', '张三的联系方式是什么？', '新增学生李四，电话13800138000']
  },
  {
    icon: BookOpen,
    title: '课程管理',
    color: '#1890ff',
    questions: ['有哪些课程？', '数学课的课时费是多少？', '查询英语课程的上课记录']
  },
  {
    icon: Calendar,
    title: '上课记录',
    color: '#722ed1',
    questions: ['张三上了多少次课？', '给张三添加一次数学课记录，2课时', '本月有哪些上课记录？']
  },
  {
    icon: Wallet,
    title: '费用管理',
    color: '#fa8c16',
    questions: ['本月有哪些欠费学生？', '张三还欠多少课时费？', '记录张三缴费1000元']
  },
  {
    icon: FileText,
    title: '统计报表',
    color: '#eb2f96',
    questions: ['查询本月报表', '本月的收入统计', '各课程的学生人数统计']
  }
]
</script>

<template>
  <CommonPage title="智能助手" :show-back="false">
    <div class="ai-assistant-container">
      <!-- 左侧：信息面板 -->
      <div class="left-panel">
        <NCard class="info-card" :bordered="false">
          <div class="assistant-header">
            <div class="assistant-avatar">
              <NIcon :size="48" :component="Bot" color="#4472C4" />
            </div>
            <div class="assistant-info">
              <h2>教培管理助手</h2>
              <p>基于 AI 的智能助手</p>
            </div>
          </div>

          <NDivider />

          <div class="capabilities">
            <h3><NIcon :size="18" :component="Sparkles" /> 我能帮您做什么</h3>
            <ul>
              <li><span class="capability-dot query"></span>查询学生、课程信息</li>
              <li><span class="capability-dot query"></span>查看上课记录和费用</li>
              <li><span class="capability-dot write"></span>添加/修改上课记录</li>
              <li><span class="capability-dot write"></span>记录缴费信息</li>
              <li><span class="capability-dot report"></span>生成月度统计报表</li>
            </ul>
          </div>

          <NDivider />

          <div class="tips">
            <h3><NIcon :size="18" :component="MessageCircle" /> 使用提示</h3>
            <NAlert type="info" :show-icon="false" class="tip-alert">
              <p>💡 查询类操作会直接返回结果</p>
              <p>⚠️ 写操作需要您确认后才执行</p>
              <p>⏰ 确认操作有5分钟有效期</p>
            </NAlert>
          </div>
        </NCard>

        <!-- 示例问题分类 -->
        <NCard class="examples-card" title="💡 试试这些问题" :bordered="false">
          <div class="example-categories">
            <div 
              v-for="category in exampleCategories" 
              :key="category.title"
              class="category-section"
            >
              <div class="category-header" :style="{ color: category.color }">
                <NIcon :size="20" :component="category.icon" />
                <span>{{ category.title }}</span>
              </div>
              <div class="category-questions">
                <NTag
                  v-for="q in category.questions"
                  :key="q"
                  size="small"
                  class="question-tag"
                  :style="{ borderColor: category.color + '40', color: category.color }"
                  @click="askExample(q)"
                >
                  {{ q }}
                </NTag>
              </div>
            </div>
          </div>
        </NCard>
      </div>

      <!-- 右侧：聊天区域 -->
      <div class="right-panel">
        <NCard class="chat-card" :bordered="false">
          <!-- 消息列表 -->
          <div ref="messagesContainer" class="messages-container">
            <div
              v-for="(message, index) in messages"
              :key="index"
              class="message-item"
              :class="message.role"
            >
              <div class="message-avatar">
                <img
                  v-if="message.role === 'ai'"
                  src="https://api.dicebear.com/7.x/bottts/svg?seed=AI"
                  alt="AI"
                />
                <img
                  v-else
                  src="https://api.dicebear.com/7.x/avataaars/svg?seed=User"
                  alt="User"
                />
              </div>
              <div class="message-content">
                <div class="message-bubble">
                  <VueMarkdownStream
                    v-if="message.role === 'ai' && message.content"
                    :content="message.content"
                  />
                  <template v-else>{{ message.content }}</template>
                </div>
                <!-- 确认/取消按钮 -->
                <div v-if="message.confirmation && message.confirmation.operation_id" class="confirmation-buttons">
                  <NButton type="primary" :disabled="isLoading" @click="confirmOperation(true, message.confirmation)">
                    <template #icon><NIcon :component="Check" /></template>
                    确认执行
                  </NButton>
                  <NButton :disabled="isLoading" @click="confirmOperation(false, message.confirmation)">
                    <template #icon><NIcon :component="X" /></template>
                    取消操作
                  </NButton>
                </div>
              </div>
            </div>
            
            <!-- 加载指示器 -->
            <div v-if="isLoading" class="message-item ai loading">
              <div class="message-avatar">
                <img src="https://api.dicebear.com/7.x/bottts/svg?seed=AI" alt="AI" />
              </div>
              <div class="message-content">
                <div class="message-bubble typing">
                  <span class="dot"></span>
                  <span class="dot"></span>
                  <span class="dot"></span>
                </div>
              </div>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="input-area">
            <NInput
              v-model:value="inputMessage"
              type="textarea"
              :autosize="{ minRows: 1, maxRows: 4 }"
              placeholder="请输入您的问题，例如：查询所有学生..."
              :disabled="isLoading"
              @keydown="handleKeydown"
            />
            <NButton
              type="primary"
              :disabled="!inputMessage.trim() || isLoading"
              :loading="isLoading"
              @click="sendMessage"
            >
              <template #icon>
                <NIcon :component="Send" />
              </template>
              发送
            </NButton>
          </div>
        </NCard>
      </div>
    </div>
  </CommonPage>
</template>

<style scoped lang="scss">
.ai-assistant-container {
  display: flex;
  gap: 20px;
  height: calc(100vh - 140px);
  min-height: 600px;
}

.left-panel {
  width: 360px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex-shrink: 0;
}

.right-panel {
  flex: 1;
  min-width: 0;
}

.info-card {
  .assistant-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 8px;

    .assistant-avatar {
      width: 64px;
      height: 64px;
      border-radius: 16px;
      background: linear-gradient(135deg, #e6f0ff 0%, #f0f7ff 100%);
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .assistant-info {
      h2 {
        margin: 0;
        font-size: 20px;
        color: #1a1a1a;
      }

      p {
        margin: 4px 0 0;
        color: #666;
        font-size: 14px;
      }
    }
  }

  .capabilities {
    h3 {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0 0 12px;
      font-size: 15px;
      color: #1a1a1a;
    }

    ul {
      list-style: none;
      padding: 0;
      margin: 0;

      li {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 0;
        color: #555;
        font-size: 14px;

        .capability-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;

          &.query {
            background: #52c41a;
          }

          &.write {
            background: #fa8c16;
          }

          &.report {
            background: #eb2f96;
          }
        }
      }
    }
  }

  .tips {
    h3 {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0 0 12px;
      font-size: 15px;
      color: #1a1a1a;
    }

    .tip-alert {
      p {
        margin: 4px 0;
      }
    }
  }
}

.examples-card {
  flex: 1;
  overflow-y: auto;

  :deep(.n-card__content) {
    padding: 16px;
  }

  .example-categories {
    display: flex;
    flex-direction: column;
    gap: 16px;

    .category-section {
      .category-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 8px;
      }

      .category-questions {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;

        .question-tag {
          cursor: pointer;
          transition: all 0.2s;

          &:hover {
            opacity: 0.8;
            transform: translateY(-1px);
          }
        }
      }
    }
  }
}

.chat-card {
  height: 100%;
  display: flex;
  flex-direction: column;

  :deep(.n-card__content) {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 16px;
  }

  .messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
    display: flex;
    flex-direction: column;
    gap: 16px;

    .message-item {
      display: flex;
      gap: 12px;
      max-width: 85%;

      &.user {
        align-self: flex-end;
        flex-direction: row-reverse;

        .message-bubble {
          background: #4472C4;
          color: white;
          border-bottom-right-radius: 4px;
        }
      }

      &.ai {
        align-self: flex-start;

        .message-bubble {
          background: #f5f5f5;
          color: #1a1a1a;
          border-bottom-left-radius: 4px;
        }
      }

      .message-avatar {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        overflow: hidden;
        flex-shrink: 0;

        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
      }

      .message-content {
        .message-bubble {
          padding: 12px 16px;
          border-radius: 16px;
          font-size: 14px;
          line-height: 1.6;
          word-break: break-word;

          &.typing {
            display: flex;
            gap: 4px;
            padding: 16px 20px;

            .dot {
              width: 8px;
              height: 8px;
              background: #999;
              border-radius: 50%;
              animation: typing 1.4s infinite;

              &:nth-child(2) {
                animation-delay: 0.2s;
              }

              &:nth-child(3) {
                animation-delay: 0.4s;
              }
            }
          }
        }

        .confirmation-buttons {
          display: flex;
          gap: 12px;
          margin-top: 12px;
          padding-left: 4px;
        }
      }
    }
  }

  .input-area {
    display: flex;
    gap: 12px;
    padding-top: 16px;
    border-top: 1px solid #e8e8e8;
    margin-top: 16px;

    .n-input {
      flex: 1;
    }

    .n-button {
      align-self: flex-end;
    }
  }
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

@media (max-width: 1024px) {
  .ai-assistant-container {
    flex-direction: column;
    height: auto;
  }

  .left-panel {
    width: 100%;
  }

  .right-panel {
    height: 600px;
  }
}
</style>
