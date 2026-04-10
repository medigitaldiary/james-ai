import { useEffect, useRef } from 'react'
import { useChatStore } from '../../store/chatStore'
import { MessageBubble } from './MessageBubble'
import { TypingIndicator } from './TypingIndicator'

export function MessageList() {
  const messages = useChatStore((s) => s.messages)
  const isLoading = useChatStore((s) => s.isLoading)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  return (
    <div className="flex-1 overflow-y-auto py-6 bg-james-bg">
      <div className="max-w-2xl mx-auto px-4 space-y-5">
        {messages.map((msg, idx) => {
          // For James messages, find the most recent user message before it
          const prevUserMsg =
            msg.role === 'james'
              ? [...messages].slice(0, idx).reverse().find((m) => m.role === 'user')?.content ?? ''
              : ''

          return (
            <MessageBubble key={msg.id} message={msg} userQuery={prevUserMsg} />
          )
        })}
        {isLoading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
