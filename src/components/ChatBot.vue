

<script setup>
import { ref, nextTick, onMounted } from 'vue'

// 控制聊天窗口开关
const isChatOpen = ref(false)
// 用户输入内容
const userInput = ref('')
// 消息列表
const messages = ref([
  {
    type: 'bot-message',
    content: '您好！我是湘绣AI助手，很高兴为您提供帮助。\n您可以向我询问关于湘绣的历史、技法、作品等相关信息。'
  }
])
// 是否正在输入
const isTyping = ref(false)
// 消息容器引用
const messagesContainer = ref(null)
// Coze SDK实例
let cozeWebSDK = null

// Bot ID - 使用提供的bot_id
const botId = '7486101891035447346'
// PAT令牌 - 实际使用时需要从安全的地方获取
const patToken = 'pat_5G1AogU0NX2yx0dRSHe5yjj233ykcllkbtx5ofqWRwOouoOEycgONJj4FIuHrkK3'

// 动态加载Coze SDK
const loadCozeSDK = () => {
  return new Promise((resolve, reject) => {
    // 检查SDK是否已经加载
    if (window.CozeWebSDK) {
      resolve(window.CozeWebSDK)
      return
    }
    
    // 创建script标签
    const script = document.createElement('script')
    script.src = 'https://lf-cdn.coze.cn/obj/unpkg/flow-platform/chat-app-sdk/1.1.0-beta.0/libs/cn/index.js'
    script.async = true
    
    // 加载成功回调
    script.onload = () => {
      console.log('Coze SDK 加载成功')
      resolve(window.CozeWebSDK)
    }
    
    // 加载失败回调
    script.onerror = (error) => {
      console.error('Coze SDK 加载失败:', error)
      reject(new Error('Coze SDK 加载失败'))
    }
    
    // 添加到document
    document.head.appendChild(script)
  })
}

// 初始化Coze SDK
const initCozeSDK = async () => {
  try {
    // 加载SDK
    const CozeWebSDK = await loadCozeSDK()
    
    if (CozeWebSDK) {
      // 初始化WebChatClient
      cozeWebSDK = new CozeWebSDK.WebChatClient({
        config: {
          // Agent ID
          botId: botId,
          isIframe: false,
        },
        auth: {
          // Authentication methods, the default type is 'unauth', which means no authentication is required
          type: 'token',
          // When the type is set to 'token', it is necessary to configure a PAT (Personal Access Token) or OAuth access token for authentication.
          token: patToken,
          // When the access token expires, use a new token and set it as needed.
          onRefreshToken: () => patToken,
        },
        chatBot: {
          title: '湘绣AI助手',
          uploadable: true,
          width: 390
        },
        footer: {
          isShow: false,
        }
      })
      
      console.log('Coze SDK 初始化成功')
    }
  } catch (error) {
    console.error('Coze SDK 初始化失败:', error)
  }
}

// 切换聊天窗口显示状态
const toggleChat = () => {
  isChatOpen.value = !isChatOpen.value
  if (isChatOpen.value) {
    nextTick(() => scrollToBottom())
  }
}

// 发送消息
const sendMessage = () => {
  if (userInput.value.trim() && !isTyping.value) {
    const userMessage = userInput.value.trim()
    
    // 添加用户消息
    messages.value.push({
      type: 'user-message',
      content: userMessage
    })
    
    // 清空输入框
    userInput.value = ''
    
    // 滚动到底部
    scrollToBottom()
    
    // 获取AI回复
    getAIResponse(userMessage)
  }
}

// 使用Coze SDK获取AI回复
const getAIResponse = async (question) => {
  // 设置正在输入状态
  isTyping.value = true
  
  // 滚动到底部
  nextTick(() => scrollToBottom())
  
  try {
    if (!cozeWebSDK) {
      throw new Error('Coze SDK 未初始化')
    }
    
    console.log('通过Coze SDK发送消息:', question)
    
    // 使用SDK发送消息
    const response = await cozeWebSDK.chat({ query: question, stream: false })
    
    console.log('Coze SDK响应数据:', response)
    
    // 处理SDK返回的回复
    let botResponse = '抱歉，我无法获取回复。请稍后再试。'
    
    // 根据SDK响应结构提取回复内容
    if (response.code === 0 && response.data) {
      if (response.data.messages && response.data.messages.length > 0) {
        const lastMessage = response.data.messages[response.data.messages.length - 1]
        if (lastMessage.content) {
          botResponse = lastMessage.content
        }
      } else if (response.data.answer) {
        // 兼容可能的其他响应格式
        botResponse = response.data.answer
      }
    } else {
      botResponse = `获取回复失败: ${response.msg || '未知错误'}`
    }
    
    // 关闭正在输入状态
    isTyping.value = false
    
    // 添加AI回复
    messages.value.push({
      type: 'bot-message',
      content: botResponse
    })
    
  } catch (error) {
    console.error('获取AI回复失败:', error)
    
    // 错误情况下也关闭输入状态并显示友好提示
    isTyping.value = false
    
    messages.value.push({
      type: 'bot-message',
      content: '抱歉，我暂时无法为您提供回答。可能是网络问题或服务暂时不可用，请稍后再试。'
    })
  } finally {
    // 滚动到底部
    nextTick(() => scrollToBottom())
  }
}

// 发送预设问题
const sendQuestion = (question) => {
  userInput.value = question
  sendMessage()
}

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 生命周期钩子
onMounted(async () => {
  console.log('聊天机器人组件已加载')
  // 初始化Coze SDK
  await initCozeSDK()
})
</script>

<style scoped>

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-bot-container {
    bottom: 20px;
    right: 20px;
  }
  
  .chat-bot-trigger {
    width: 50px;
    height: 50px;
  }
  
  .chat-interface {
    bottom: 60px;
    width: 320px;
    height: 450px;
  }
  
  .message-content {
    max-width: 85%;
    font-size: 13px;
  }
}
</style>