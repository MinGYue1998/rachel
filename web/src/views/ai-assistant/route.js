const Layout = () => import('@/layout/index.vue')

export default {
  path: '/ai',
  component: Layout,
  redirect: '/ai/assistant',
  name: 'AI',
  meta: { title: 'AI助手', icon: 'carbon:machine-learning-model' },
  children: [
    {
      path: 'assistant',
      name: 'AIAssistant',
      component: () => import('./index.vue'),
      meta: { title: 'AI助手', icon: 'carbon:chat-bot' },
    },
  ],
}
