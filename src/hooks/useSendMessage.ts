import { v4 as uuidv4 } from 'uuid'
import { useChatStore } from '../store/chatStore'
import { useKBStore } from '../store/kbStore'
import { sendMessage } from '../services/chatService'
import { detectFrustration } from '../utils/frustrationDetect'
import type { Message } from '../types'

export function useSendMessage() {
  const {
    messages,
    pageUrl,
    appendMessage,
    setLoading,
    incrementFrustration,
    flagFrustration,
  } = useChatStore()
  const files = useKBStore((s) => s.files)

  const send = async (text: string) => {
    if (!text.trim()) return

    const userMsg: Message = {
      id: uuidv4(),
      role: 'user',
      content: text.trim(),
      timestamp: new Date(),
      showDisclaimer: false,
    }
    appendMessage(userMsg)
    setLoading(true)

    if (detectFrustration(text)) {
      flagFrustration()
    }

    try {
      const payload = {
        messages: [...messages, userMsg].map((m) => ({
          role: m.role,
          content: m.content,
        })),
        kbFileIds: files.filter((f) => f.status === 'ready').map((f) => f.id),
        pageUrl,
      }

      const response = await sendMessage(payload)

      const jamesMsg: Message = {
        id: uuidv4(),
        role: 'james',
        content: response.content,
        timestamp: new Date(),
        showDisclaimer: response.show_disclaimer ?? false,
        bondsData: response.bonds_data,
      }
      appendMessage(jamesMsg)
      incrementFrustration()
    } catch {
      appendMessage({
        id: uuidv4(),
        role: 'james',
        content:
          "I'm having trouble connecting right now. Please try again in a moment, or contact our support team at support@bondscanner.com.",
        timestamp: new Date(),
        showDisclaimer: false,
      })
    } finally {
      setLoading(false)
    }
  }

  return { send }
}
