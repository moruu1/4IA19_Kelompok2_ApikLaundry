<script setup>
import { ref, nextTick, onMounted } from 'vue'

const emit = defineEmits(['close'])

const ML_API_URL = import.meta.env.VITE_ML_API_URL || 'http://localhost:5000'

const currentTime = ref('')
const isLoading = ref(false)

const messages = ref([
  {
    id: 1,
    text: 'Ada yang bisa Apik bantu?',
    isBot: true,
    timestamp: ''
  },
  {
    id: 2,
    text: 'Silakan tanyakan apapun seputar layanan laundry kami.',
    isBot: true,
    timestamp: ''
  }
])

const newMessage = ref('')
const chatContainer = ref(null)

onMounted(() => {
  updateTime()
  // Update timestamp for initial messages
  messages.value[0].timestamp = currentTime.value
  messages.value[1].timestamp = currentTime.value
})

function updateTime() {
  const now = new Date()
  const day = String(now.getDate()).padStart(2, '0')
  const monthNames = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 
                      'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
  const month = monthNames[now.getMonth()]
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  currentTime.value = `${day} ${month} ${hours}:${minutes}`
}

async function sendMessage() {
  if (!newMessage.value.trim() || isLoading.value) return
  
  const userMessageText = newMessage.value
  updateTime()
  
  // Add user message
  messages.value.push({
    id: messages.value.length + 1,
    text: userMessageText,
    isBot: false,
    timestamp: currentTime.value
  })
  
  // Clear input
  newMessage.value = ''
  scrollToBottom()
  
  // Set loading state
  isLoading.value = true
  
  try {
    // Call backend chatbot API
    const response = await fetch(`${ML_API_URL}/chatbot`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: userMessageText
      })
    })
    
    const data = await response.json()
    
    // Add bot response
    updateTime()
    messages.value.push({
      id: messages.value.length + 1,
      text: data.reply || 'Maaf, terjadi kesalahan. Silakan coba lagi.',
      isBot: true,
      timestamp: currentTime.value
    })
    
  } catch (error) {
    console.error('Chatbot error:', error)
    updateTime()
    messages.value.push({
      id: messages.value.length + 1,
      text: `Maaf, koneksi ke server chatbot gagal. Pastikan backend ML berjalan di ${ML_API_URL}`,
      isBot: true,
      timestamp: currentTime.value
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

function selectOption(option) {
  // Set the option as the message and send it
  newMessage.value = option
  sendMessage()
}

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

function closeChat() {
  emit('close')
}
</script>

<template>
  <div class="chat-widget">
    <!-- Chat Header -->
    <div class="chat-header">
      <div class="header-info">
        <div class="bot-avatar-small">
          <img src="../assets/images/logo_apik.png" alt="Apik">
        </div>
        <div class="header-text">
          <h3>Tanya Apik</h3>
          <span class="status">Online</span>
        </div>
      </div>
      <button @click="closeChat" class="close-button">
        <i class="fas fa-times"></i>
      </button>
    </div>

    <!-- Chat Container -->
    <div class="chat-container" ref="chatContainer">
      <!-- Date Header -->
      <div class="date-header">
        {{ currentTime }}
      </div>
      
      <!-- Messages -->
      <div class="messages-wrapper">
        <div 
          v-for="message in messages" 
          :key="message.id"
          :class="['message-row', message.isBot ? 'bot-message' : 'user-message']"
        >
          <!-- Bot Avatar -->
          <div v-if="message.isBot" class="avatar bot-avatar">
            <img src="../assets/images/logo_apik.png" alt="Apik">
          </div>
          
          <!-- Message Content -->
          <div class="message-content">
            <!-- Message Bubble -->
            <div class="message-bubble">
              {{ message.text }}
            </div>
            
            <!-- Options -->
            <div v-if="message.options" class="message-options">
              <button 
                v-for="(option, index) in message.options" 
                :key="index"
                @click="selectOption(option)"
                class="option-button"
              >
                {{ option }}
              </button>
            </div>
          </div>
          
          <!-- User Avatar -->
          <div v-if="!message.isBot" class="avatar user-avatar">
            <i class="fas fa-user"></i>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Input Area -->
    <div class="input-area">
      <input 
        v-model="newMessage"
        @keyup.enter="sendMessage"
        type="text" 
        :placeholder="isLoading ? 'Menunggu jawaban...' : 'Kirim Pesan'"
        :disabled="isLoading"
        class="message-input"
      />
      
      <button @click="sendMessage" class="send-button" :disabled="isLoading">
        <i v-if="!isLoading" class="fas fa-paper-plane"></i>
        <i v-else class="fas fa-spinner fa-spin"></i>
      </button>
    </div>
  </div>
</template>

<style scoped>
.chat-widget {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 400px;
  height: 600px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  overflow: hidden;
}

/* Chat Header */
.chat-header {
  background: linear-gradient(135deg, #1678F3 0%, #6BB6FF 100%);
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bot-avatar-small {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: white;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bot-avatar-small img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.header-text h3 {
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.status {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  opacity: 0.9;
}

.close-button {
  background: transparent;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.3s;
}

.close-button:hover {
  background: rgba(255, 255, 255, 0.2);
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: linear-gradient(180deg, #6BB6FF 0%, #87C4FF 100%);
}

.date-header {
  text-align: center;
  font-family: 'Inter', sans-serif;
  font-size: 11px;
  color: #333333;
  background: rgba(255, 255, 255, 0.9);
  padding: 5px 12px;
  border-radius: 12px;
  display: inline-block;
  margin: 0 auto 20px;
  width: fit-content;
  display: block;
  text-align: center;
}

.messages-wrapper {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message-row {
  display: flex;
  gap: 10px;
}

.bot-message {
  justify-content: flex-start;
}

.user-message {
  justify-content: flex-end;
}

.avatar {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.bot-avatar {
  background: #FF9AA2;
  padding: 6px;
}

.bot-avatar img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.user-avatar {
  background: #FFB7B2;
  color: white;
  font-size: 16px;
}

.message-content {
  max-width: 75%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-bubble {
  background: white;
  padding: 10px 14px;
  border-radius: 16px;
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  color: #333333;
  line-height: 1.5;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
  word-wrap: break-word;
}

.bot-message .message-bubble::before {
  content: '';
  position: absolute;
  left: -6px;
  top: 10px;
  width: 0;
  height: 0;
  border-top: 6px solid transparent;
  border-bottom: 6px solid transparent;
  border-right: 6px solid white;
}

.user-message .message-bubble {
  background: white;
  margin-left: auto;
}

.message-options {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.option-button {
  background: white;
  border: 1px solid #E0E0E0;
  border-radius: 10px;
  padding: 8px 12px;
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  color: #333333;
  cursor: pointer;
  transition: all 0.3s;
  text-align: left;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.option-button:hover {
  background: #F5F5F5;
  border-color: #1678F3;
  color: #1678F3;
}

.input-area {
  background: white;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-top: 1px solid #E0E0E0;
}

.send-button {
  width: 36px;
  height: 36px;
  border: none;
  background: #1678F3;
  color: white;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  border-radius: 50%;
  flex-shrink: 0;
}

.send-button:hover:not(:disabled) {
  background: #0d5ec4;
  transform: scale(1.05);
}

.send-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.message-input {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid #E0E0E0;
  border-radius: 20px;
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  outline: none;
  transition: border-color 0.3s;
}

.message-input:focus {
  border-color: #1678F3;
}

.message-input::placeholder {
  color: #AAAAAA;
}

/* Custom Scrollbar */
.chat-container::-webkit-scrollbar {
  width: 5px;
}

.chat-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.2);
}

.chat-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.5);
  border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.7);
}

/* Responsive */
@media (max-width: 768px) {
  .chat-widget {
    width: 100% !important;
    max-width: 100vw !important;
    height: 85vh !important;
    bottom: 0 !important;
    right: 0 !important;
    left: 0 !important;
    border-radius: 16px 16px 0 0 !important;
    box-sizing: border-box !important;
  }

  .chat-header {
    padding: 14px 16px !important;
  }

  .header-text h3 {
    font-size: 15px !important;
  }

  .status {
    font-size: 11px !important;
  }

  .bot-avatar-small {
    width: 36px !important;
    height: 36px !important;
  }

  .close-button {
    width: 36px !important;
    height: 36px !important;
    font-size: 18px !important;
  }

  .chat-container {
    padding: 16px !important;
  }

  .date-header {
    font-size: 10px !important;
    padding: 4px 10px !important;
    margin-bottom: 16px !important;
  }

  .avatar {
    width: 32px !important;
    height: 32px !important;
  }

  .user-avatar {
    font-size: 14px !important;
  }

  .message-content {
    max-width: 80% !important;
  }

  .message-bubble {
    padding: 10px 12px !important;
    font-size: 13px !important;
  }

  .input-area {
    padding: 12px !important;
  }

  .message-input {
    font-size: 14px !important;
    padding: 10px 14px !important;
  }

  .send-button {
    width: 40px !important;
    height: 40px !important;
    font-size: 16px !important;
  }
}
</style>
