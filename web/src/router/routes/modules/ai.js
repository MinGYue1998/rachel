import { BasicLayout } from '@/layouts'

export default {
  path: '/ai',
  component: BasicLayout,
  redirect: '/ai/assistant',
  name: 'AI助手',
  meta: { title: 'AI助手', icon: 'carbon:machine-learning-model' },
  children: [
    {
      path: 'assistant',
      name: 'AI助手',
      component: () => import('@/views/ai-assistant/index.vue'),
      meta: { title: 'AI助手', icon: 'carbon:chat-bot', keepAlive: true },
    },
  ],
}
