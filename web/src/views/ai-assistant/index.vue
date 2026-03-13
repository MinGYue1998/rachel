<script setup>
import { ref, onMounted, computed } from 'vue'
import { NButton, NCard, NSpace, NTag, NAlert, NSpin } from 'naive-ui'
import 'deep-chat'

import CommonPage from '@/components/page/CommonPage.vue'
import { useUserStore } from '@/store'

const userStore = useUserStore()
const chatRef = ref(null)
const pendingConfirmation = ref(null)
const isLoading = ref(false)

// 连接配置
const connectConfig = computed(() => ({
  url: '/api/v1/ai/chat',
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${userStore.token}`,
    'Content-Type': 'application/json'
  },
  stream: true,
  // 自定义请求处理，用于处理确认流程
  handler: handleChatRequest
}))

// 处理聊天请求
async function handleChatRequest(body, signals) {
  try {
    isLoading.value = true
    
    const response = await fetch('/api/v1/ai/chat', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${userStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    })
    
    if (!response.ok) {
      throw new Error('请求失败')
    }
    
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            
            // 处理确认请求
            if (data.type === 'confirmation_required') {
              pendingConfirmation.value = data
              signals.onResponse({
                text: formatConfirmationMessage(data),
                html: generateConfirmationHTML(data)
              })
              isLoading.value = false
              return
            }
            
            // 处理执行中状态
            if (data.type === 'operation_executing') {
              signals.onResponse({ text: data.message })
              continue
            }
            
            // 处理执行完成
            if (data.type === 'operation_completed') {
              signals.onResponse({
                text: data.content,
                html: data.data ? formatResultHTML(data.data) : null
              })
              isLoading.value = false
              return
            }
            
            // 处理执行失败
            if (data.type === 'operation_failed') {
              signals.onResponse({
                text: `❌ ${data.content}`,
                error: data.error
              })
              isLoading.value = false
              return
            }
            
            // 普通文本响应
            if (data.type === 'text' && data.content) {
              signals.onResponse({ text: data.content })
            }
          } catch (e) {
            console.error('解析响应失败:', e)
          }
        }
      }
    }
    
    isLoading.value = false
  } catch (error) {
    isLoading.value = false
    signals.onResponse({ error: error.message || '请求失败' })
  }
}

// 格式化确认消息
function formatConfirmationMessage(data) {
  let text = `🤔 ${data.understanding}\n\n`
  text += `📋 操作详情：\n${JSON.stringify(data.operation.params, null, 2)}\n\n`
  text += `⚠️ 可能产生的后果：\n`
  data.consequences.forEach((c, i) => {
    text += `${i + 1}. ${c}\n`
  })
  text += `\n${data.message}`
  return text
}

// 生成确认按钮HTML
function generateConfirmationHTML(data) {
  return `
    <div style="margin-top: 12px; padding: 12px; background: #f5f5f5; border-radius: 8px;">
      <p style="margin: 0 0 8px 0; color: #666;">${data.understanding}</p>
      <div style="margin: 8px 0;">
        ${data.consequences.map(c => `<p style="margin: 4px 0; color: #ff4d4f;">⚠️ ${c}</p>`).join('')}
      </div>
      <div style="display: flex; gap: 8px; margin-top: 12px;">
        <button onclick="window.confirmOperation('${data.operation_id}', true)" 
                style="padding: 8px 16px; background: #52c41a; color: white; border: none; border-radius: 4px; cursor: pointer;">
          ✅ 确认执行
        </button>
        <button onclick="window.confirmOperation('${data.operation_id}', false)"
                style="padding: 8px 16px; background: #ff4d4f; color: white; border: none; border-radius: 4px; cursor: pointer;">
          ❌ 取消
        </button>
      </div>
    </div>
  `
}

// 格式化结果HTML
function formatResultHTML(data) {
  if (!data) return null
  return `
    <div style="margin-top: 8px; padding: 12px; background: #f6ffed; border: 1px solid #b7eb8f; border-radius: 8px;">
      <pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word;">${JSON.stringify(data, null, 2)}</pre>
    </div>
  `
}

// 确认操作
async function confirmOperation(operationId, confirmed) {
  try {
    isLoading.value = true
    pendingConfirmation.value = null
    
    const response = await fetch('/api/v1/ai/confirm', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${userStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        operation_id: operationId,
        confirmed: confirmed
      })
    })
    
    if (!response.ok) {
      throw new Error('确认请求失败')
    }
    
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let fullText = ''
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            
            if (data.type === 'text' && data.content) {
              fullText += data.content
            } else if (data.type === 'operation_completed') {
              fullText = data.content
              if (data.data) {
                fullText += '\n\n' + JSON.stringify(data.data, null, 2)
              }
            } else if (data.type === 'operation_failed') {
              fullText = '❌ ' + data.content
            }
          } catch (e) {
            console.error('解析响应失败:', e)
          }
        }
      }
    }
    
    // 添加系统消息到聊天
    if (chatRef.value) {
      chatRef.value.addMessage({
        text: fullText || (confirmed ? '✅ 操作已确认并执行' : '❌ 操作已取消'),
        role: 'ai'
      })
    }
    
    isLoading.value = false
  } catch (error) {
    isLoading.value = false
    if (chatRef.value) {
      chatRef.value.addMessage({
        text: '❌ ' + (error.message || '操作失败'),
        role: 'ai'
      })
    }
  }
}

// 注册全局函数供HTML调用
onMounted(() => {
  window.confirmOperation = confirmOperation
})

// 示例问题
const exampleQuestions = [
  '有哪些学生？',
  '张三上了多少次课？',
  '本月有哪些欠费学生？',
  '给张三添加一次上课记录，2课时',
  '查询本月报表'
]

function askExample(question) {
  if (chatRef.value) {
    chatRef.value.submitUserMessage({ text: question })
  }
}
</script>

<template>
  <CommonPage show-footer title="AI助手">
    <div class="ai-assistant-container">
      <!-- 示例问题 -->
      <NCard class="mb-4" size="small">
        <NSpace>
          <span class="text-gray-500">示例问题：</span>
          <NTag
            v-for="q in exampleQuestions"
            :key="q"
            size="small"
            class="cursor-pointer hover:bg-blue-100"
            @click="askExample(q)"
          >
            {{ q }}
          </NTag>
        </NSpace>
      </NCard>

      <!-- 聊天组件 -->
      <NCard class="chat-card">
        <deep-chat
          ref="chatRef"
          :connect="connectConfig"
          :intro-message="{ 
            text: '您好！我是教培管理助手 🤖\n\n我可以帮您：\n• 查询学生、课程信息\n• 查看上课记录和费用\n• 生成月度报表\n• 管理上课记录和缴费\n\n请问有什么可以帮您？',
            role: 'ai'
          }"
          :text-input="{ 
            placeholder: { text: '请输入您的问题...' },
            disabled: isLoading
          }"
          :submit-button-styles="{
            submit: { 
              container: { 
                default: { backgroundColor: isLoading ? '#ccc' : '#4472C4' } 
              } 
            }
          }"
          :error-messages="{
            displayServiceErrorMessages: true
          }"
          :avatars="{
            ai: { src: 'https://api.dicebear.com/7.x/bottts/svg?seed=AI', styles: { avatar: { width: '36px', height: '36px' } } },
            user: { src: 'https://api.dicebear.com/7.x/avataaars/svg?seed=User', styles: { avatar: { width: '36px', height: '36px' } } }
          }"
          :message-styles="{
            default: { shared: { bubble: { backgroundColor: '#f5f5f5', maxWidth: '80%' } } }
          }"
          style="height: calc(100vh - 280px); border: none;"
        />
      </NCard>

      <!-- 使用说明 -->
      <NAlert type="info" class="mt-4" :show-icon="true">
        <template #header>
          使用说明
        </template>
        <ul class="text-sm">
          <li>• 查询类操作（如"有哪些学生"）会直接返回结果</li>
          <li>• 写操作（如"添加记录"）需要您确认后才执行</li>
          <li>• 支持自然语言，您可以像和人对话一样提问</li>
          <li>• 确认操作有5分钟有效期，过期需重新发起</li>
        </ul>
      </NAlert>
    </div>
  </CommonPage>
</template>

<style scoped>
.ai-assistant-container {
  max-width: 1000px;
  margin: 0 auto;
}

.chat-card {
  :deep(.n-card__content) {
    padding: 0;
  }
}

:deep(.deep-chat) {
  --deep-chat-font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
</style>
